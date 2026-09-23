"""New sqlite3 event-journal comparator; no production admission/planner imports.

Research comparator, NOT an existing third-party product. Both modes retain all
candidate rows, rich review content, used candidate, complete sources and atomicity.
The exact mode adds authorization-to-reviewed-instance binding.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from common import canonical, context, digest


class Journal:
    def __init__(self, path, fields, exact):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.exact = exact
        self.fields = set(fields)
        self.con = sqlite3.connect(path, isolation_level=None)
        self.con.row_factory = sqlite3.Row
        self.con.executescript('''PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL;
            PRAGMA busy_timeout=5000;
            CREATE TABLE head(id INTEGER PRIMARY KEY, version INTEGER NOT NULL);
            INSERT INTO head VALUES(1,0);
            CREATE TABLE candidates(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE approvals(id TEXT PRIMARY KEY, version INTEGER, reviewer TEXT, values_json TEXT);
            CREATE TABLE review_items(approval TEXT REFERENCES approvals(id), field TEXT,
                context_json TEXT, reviewed_id TEXT REFERENCES candidates(id), PRIMARY KEY(approval,field));
            CREATE TABLE versions(version INTEGER PRIMARY KEY, values_json TEXT, sources_json TEXT);
            CREATE TABLE consumption(approval TEXT PRIMARY KEY REFERENCES approvals(id), version INTEGER REFERENCES versions(version));
            CREATE TABLE events(id TEXT PRIMARY KEY, version INTEGER REFERENCES versions(version), field TEXT,
                used_candidate TEXT REFERENCES candidates(id), approval TEXT REFERENCES approvals(id),
                value_json TEXT, UNIQUE(version,field));
            CREATE TABLE audit(version INTEGER PRIMARY KEY REFERENCES versions(version),
                before_json TEXT, after_json TEXT, previous_hash TEXT, row_hash TEXT);
        ''')
        for table in ('candidates','approvals','review_items','versions','consumption','events','audit'):
            for op in ('UPDATE','DELETE'):
                self.con.execute(f"CREATE TRIGGER freeze_{table}_{op} BEFORE {op} ON {table} BEGIN SELECT RAISE(ABORT,'immutable'); END")

    def add(self, p):
        self.con.execute('INSERT INTO candidates VALUES (?,?)', (p['id'], canonical(p)))

    def candidate(self, cid):
        row = self.con.execute('SELECT payload FROM candidates WHERE id=?',(cid,)).fetchone()
        if not row:
            raise ValueError('UNKNOWN_CANDIDATE')
        return json.loads(row[0])

    def prepare(self, version, values, ids, actor='reviewer'):
        if actor not in ('reviewer', 'reviewer-2'):
            raise ValueError('PRINCIPAL')
        old = self.con.execute('SELECT values_json FROM versions ORDER BY version DESC LIMIT 1').fetchone()
        old = json.loads(old[0]) if old else {}
        complete = old | values
        if set(complete) != self.fields:
            raise ValueError('FIELD_DOMAIN')
        changed = {f for f in complete if f not in old or canonical(complete[f]) != canonical(old[f])}
        if not changed or not changed.issubset(ids):
            raise ValueError('NOOP_OR_MISSING_CANDIDATE')
        aid = 'A-'+digest([version, actor, values, ids])
        self.con.execute('BEGIN IMMEDIATE')
        try:
            self.con.execute('INSERT INTO approvals VALUES (?,?,?,?)',(aid,version,actor,canonical(complete)))
            for f in sorted(changed):
                p = self.candidate(ids[f])
                self.con.execute('INSERT INTO review_items VALUES (?,?,?,?)',
                    (aid,f,canonical(context(p)),p['id'] if self.exact else None))
            self.con.commit()
        except Exception:
            self.con.rollback()
            raise
        return aid

    def admit(self, approval, ids, values=None, failpoint=None):
        self.con.execute('BEGIN IMMEDIATE')
        try:
            a = self.con.execute('SELECT * FROM approvals WHERE id=?',(approval,)).fetchone()
            if not a:
                raise ValueError('UNKNOWN_APPROVAL')
            v = self.con.execute('SELECT version FROM head').fetchone()[0]
            if v != a['version'] or self.con.execute('SELECT 1 FROM consumption WHERE approval=?',(approval,)).fetchone():
                raise ValueError('STALE_OR_REPLAY')
            prior = self.con.execute('SELECT * FROM versions WHERE version=?',(v,)).fetchone()
            old = json.loads(prior['values_json']) if prior else {}
            sources = json.loads(prior['sources_json']) if prior else {}
            approved = json.loads(a['values_json'])
            complete = approved if values is None else approved | values
            if canonical(approved) != canonical(complete):
                raise ValueError('AUTHORIZED_VALUE_MISMATCH')
            items = list(self.con.execute('SELECT * FROM review_items WHERE approval=?',(approval,)))
            changed = {f for f in complete if f not in old or canonical(old[f]) != canonical(complete[f])}
            if set(complete) != self.fields or changed != {i['field'] for i in items}:
                raise ValueError('INCOMPLETE_BATCH')
            for item in items:
                p = self.candidate(ids[item['field']])
                if p['record_id'] != 'FORM-1' or p['field'] != item['field'] or p['expected_version'] != v:
                    raise ValueError('CONTEXT_OR_FRESHNESS')
                if canonical(context(p)) != item['context_json']:
                    raise ValueError('REVIEW_CONTEXT_MISMATCH')
                if self.exact and p['id'] != item['reviewed_id']:
                    raise ValueError('REVIEWED_INSTANCE_MISMATCH')
                sources[item['field']] = f"FORM-1:{v+1}:{item['field']}"
            cur = self.con.execute('UPDATE head SET version=? WHERE id=1 AND version=?',(v+1,v))
            if cur.rowcount != 1:
                raise ValueError('CAS')
            if failpoint == 'after_cas':
                raise RuntimeError('INJECTED:after_cas')
            self.con.execute('INSERT INTO versions VALUES(?,?,?)',(v+1,canonical(complete),canonical(sources)))
            for item in items:
                if failpoint == 'before_transition':
                    raise RuntimeError('INJECTED:before_transition')
                f = item['field']
                self.con.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',
                    (sources[f],v+1,f,ids[f],approval,canonical(complete[f])))
            prev = self.con.execute('SELECT row_hash FROM audit ORDER BY version DESC LIMIT 1').fetchone()
            prev = prev[0] if prev else ''
            self.con.execute('INSERT INTO audit VALUES(?,?,?,?,?)',
                (v+1,canonical(old),canonical(complete),prev,digest([v+1,old,complete,prev])))
            self.con.execute('INSERT INTO consumption VALUES(?,?)',(approval,v+1))
            if failpoint == 'before_commit':
                raise RuntimeError('INJECTED:before_commit')
            self.con.commit()
        except Exception:
            self.con.rollback()
            raise

    def confirm(self, version, values, ids, actor='reviewer'):
        a = self.prepare(version, values, ids, actor)
        self.admit(a, ids)

    def query(self):
        # Separate read connection; approval context rather than the used candidate
        # answers the reviewed-instance query. A used id is not assumed to be reviewed.
        with sqlite3.connect(self.path) as con:
            con.row_factory = sqlite3.Row
            vr = con.execute('SELECT * FROM versions ORDER BY version DESC LIMIT 1').fetchone()
            if not vr:
                return {}
            vals, sources = json.loads(vr['values_json']), json.loads(vr['sources_json'])
            candidates = [json.loads(r[0]) for r in con.execute('SELECT payload FROM candidates')]
            out = {}
            for f, eid in sources.items():
                r = con.execute('''SELECT e.version, e.value_json, a.reviewer, i.context_json, i.reviewed_id
                    FROM events e JOIN approvals a ON a.id=e.approval
                    JOIN review_items i ON i.approval=a.id AND i.field=e.field WHERE e.id=?''',(eid,)).fetchone()
                ctx = json.loads(r['context_json'])
                possible = [r['reviewed_id']] if r['reviewed_id'] else sorted(p['id'] for p in candidates if context(p)==ctx)
                out[f] = {'proposal':ctx['proposed'], 'authorized':json.loads(r['value_json']),
                    'reviewer':r['reviewer'], 'reviewed_candidates':possible,
                    'committed': vals[f], 'source_version':r['version']}
            return out

    def close(self):
        self.con.close()
