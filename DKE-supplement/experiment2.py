"""Local browser experiment; automated interaction, not a human-subject study."""
from __future__ import annotations
import argparse
import json
import sqlite3
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from common import ROOT, canonical, db_digest, environment, write_json
from reference import Reference, packet

CASES = ['accept', 'correction', 'reselect', 'request_substitution', 'value_substitution',
         'principal_substitution', 'stale', 'replay', 'rollback', 'dom_only_substitution']
HTML = '''<!doctype html><meta charset="utf-8"><title>Local review experiment</title>
<style>body{font:18px sans-serif;margin:60px;max-width:950px}code{overflow-wrap:anywhere}textarea{width:90%;height:70px}button{padding:12px;margin:12px}pre{white-space:pre-wrap}</style>
<h1>Candidate review — local experimental fixture</h1><p>Candidate identifier:</p><code id="candidate"></code>
<p>Proposed JSON value:</p><pre id="proposal"></pre><label>Authorized JSON value<textarea id="value"></textarea></label>
<p><button id="authorize">Record review</button><button id="confirm">Confirm</button></p><pre id="result"></pre>
<script>
window.ready=false;window.client={};window.last=null;
async function post(path,body){return await (await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})).json()}
window.selectCandidate=async(which)=>{const d=await post('/display',{which});window.client=d;
document.querySelector('#candidate').textContent=d.candidate;document.querySelector('#proposal').textContent=JSON.stringify(d.proposed);
document.querySelector('#value').value=JSON.stringify(d.proposed);window.ready=true;};
document.querySelector('#authorize').onclick=async()=>{client.value=JSON.parse(document.querySelector('#value').value);
window.last=await post('/authorize',client);document.querySelector('#result').textContent=JSON.stringify(window.last);};
document.querySelector('#confirm').onclick=async()=>{window.last=await post('/confirm',client);document.querySelector('#result').textContent=JSON.stringify(window.last);};
selectCandidate('A');</script>'''


class Experiment:
    def __init__(self, output):
        self.output=output; self.system=None; self.current=None; self.lock=threading.Lock()
        self.receipts=[]
        self.sessions=sqlite3.connect(output/'review-sessions.db',check_same_thread=False)
        self.sessions.execute('CREATE TABLE sessions(token TEXT PRIMARY KEY, candidate TEXT, version INTEGER, actor TEXT, authorized TEXT, consumed INTEGER DEFAULT 0)')

    def setup(self, args):
        if self.system: self.system.close()
        case=args['case']; mode=args['mode']; value=args['value']; label=args['label']
        path=self.output/'databases'/label/mode/(case+'.db')
        self.system=Reference(path,{'quantity':90,'operator':'INITIAL'})
        initial={'quantity':90,'operator':'INITIAL'}
        for f,v in initial.items():
            p=packet(f,v,0,'seed-'+f,evidence='constructed initial '+f);self.system.add(p)
        ids={p['field']:p['id'] for p in self.system.packets.values()}
        self.system.confirm(0,initial,ids)
        a=packet('quantity',value,1,'browser-A',evidence='browser fixture '+canonical(value))
        b=packet('quantity',value,1,'browser-B',evidence='browser fixture '+canonical(value),now=__import__('datetime').datetime.fromisoformat(a['created_at']))
        for p in [a,b]:self.system.add(p)
        self.current=args|{'A':a,'B':b,'database':str(path.relative_to(self.output))}
        return {'A':a['id'],'B':b['id']}

    def display(self,args):
        p=self.current[args['which']];token=uuid.uuid4().hex
        self.sessions.execute('INSERT INTO sessions(token,candidate,version,actor) VALUES(?,?,?,?)',(token,p['id'],1,'reviewer'));self.sessions.commit()
        return {'token':token,'candidate':p['id'],'version':1,'actor':'reviewer','proposed':p['proposed']}

    def authorize(self,args):
        row=self.sessions.execute('SELECT candidate,actor FROM sessions WHERE token=?',(args['token'],)).fetchone()
        if not row or row!=(args['candidate'],args['actor']):return {'ok':False,'error':'REVIEW_TARGET_MISMATCH'}
        self.sessions.execute('UPDATE sessions SET authorized=? WHERE token=?',(canonical(args['value']),args['token']));self.sessions.commit()
        return {'ok':True,'phase':'authorized'}

    def perturb(self,args):
        p=packet('operator','CONCURRENT',1,'browser-concurrent',evidence='browser concurrency fixture');self.system.add(p)
        self.system.confirm(1,{'operator':'CONCURRENT'},{'operator':p['id']})
        return {'ok':True}

    def confirm(self,args):
        before=db_digest(self.system.path);error=None
        try:
            if self.current['mode']=='session_gate':
                row=self.sessions.execute('SELECT candidate,version,actor,authorized,consumed FROM sessions WHERE token=?',(args['token'],)).fetchone()
                if not row or row!=(args['candidate'],args['version'],args['actor'],canonical(args['value']),0):
                    raise ValueError('SESSION_AUTHORIZATION_MISMATCH')
            def fail(name):
                if self.current['case']=='rollback' and name=='before_commit':raise RuntimeError('INJECTED:before_commit')
            self.system.repo._admission_failpoint=fail
            self.system.confirm(args['version'],{'quantity':args['value']},{'quantity':args['candidate']},args['actor'])
            accepted=True
            if self.current['mode']=='session_gate':
                self.sessions.execute('UPDATE sessions SET consumed=1 WHERE token=?',(args['token'],));self.sessions.commit()
        except Exception as exc:
            accepted=False;error=type(exc).__name__+': '+str(exc)
        finally:self.system.repo._admission_failpoint=None
        after=db_digest(self.system.path)
        row={'label':self.current['label'],'case':self.current['case'],'mode':self.current['mode'],
             'database':self.current['database'],'request':args,'accepted':accepted,'error':error,
             'before_digest':before,'after_digest':after,'zero_write_on_reject':not accepted and before==after,
             'query':self.system.query()}
        self.receipts.append(row)
        with (self.output/'server-receipts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
        return row


def run(output,driver_python,limit=False):
    output.mkdir(parents=True,exist_ok=False);experiment=Experiment(output)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def do_GET(self):
            body=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(body)
        def do_POST(self):
            args=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            try:
                with experiment.lock:result=getattr(experiment,self.path.strip('/'))(args)
            except Exception as exc:result={'harness_error':repr(exc)}
            body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        cmd=[driver_python,'-B',str(ROOT/'browser_driver.py'),'--base',f'http://127.0.0.1:{server.server_port}', '--output',str(output.resolve())]
        if limit:cmd+=['--limit']
        subprocess.run(cmd,check=True)
    finally:
        server.shutdown();experiment.sessions.close()
        if experiment.system:experiment.system.close()
    write_json(output/'environment.json',environment())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--driver-python',default=r'D:\Python312\python.exe');p.add_argument('--limit',action='store_true')
    a=p.parse_args();run(a.output,a.driver_python,a.limit)
