"""Check frozen bibliography metadata and artifact URLs without changing references."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import difflib
import json
import re
import requests
import bibtexparser

HERE = Path(__file__).resolve().parent
entries = bibtexparser.loads((HERE / 'format-baseline/filtered.bib').read_text(encoding='utf-8')).entries
HEADERS = {'User-Agent': 'AutoDecte-JIIS-reference-check/1.0'}
def norm(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())
def check(entry):
    row = {'key': entry['ID'], 'title': entry.get('title'), 'doi': entry.get('doi'), 'url': entry.get('url')}
    try:
        doi = entry.get('doi', '')
        if doi and 'arxiv' not in doi.lower() and not doi.lower().startswith('10.17487/'):
            url = 'https://api.crossref.org/works/' + requests.utils.quote(doi, safe='')
            response = requests.get(url, headers=HEADERS, timeout=18)
            row.update(checked_url=url, http_status=response.status_code)
            if response.ok:
                data = response.json()['message']
                title = ': '.join(filter(None, [' '.join(data.get('title', [])), ' '.join(data.get('subtitle', []))]))
                row['registered_title'] = title
                row['title_similarity'] = round(difflib.SequenceMatcher(None, norm(entry['title']), norm(title)).ratio(), 4)
                row['registered_authors'] = data.get('author', [])
                row['registered_venue'] = data.get('container-title', [])
                row['status'] = 'metadata_matches' if row['title_similarity'] >= .90 else 'metadata_requires_review'
            else:
                row['status'] = 'metadata_unavailable'
        else:
            url = entry.get('url') or ('https://doi.org/' + doi)
            response = requests.get(url, headers=HEADERS, timeout=18)
            row.update(checked_url=url, final_url=response.url, http_status=response.status_code)
            row['status'] = 'page_accessible' if response.ok else 'access_unconfirmed'
            if response.ok:
                html = response.text
                title = re.search(r'<meta\s+name=["\']citation_title["\']\s+content=["\']([^"\']+)', html, re.I)
                if not title:
                    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
                if title:
                    row['page_title'] = title.group(1).strip()
    except Exception as error:
        row.update(status='network_unconfirmed', error=str(error))
    return row
with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(check, entries))
artifact_urls = [
    'https://api.github.com/repos/lhh666-6/auto-dete/contents/DKE-supplement?ref=2645e5e18c900ea91c9c980e44195dc71e410432',
    'https://api.github.com/repos/lhh666-6/auto-dete/contents/latest/code/implementation-fixed?ref=c6d512843c905cab6d8521dd8c914f7fb26d85ae',
    'https://api.github.com/repos/lhh666-6/auto-dete/contents/latest?ref=r31-jss-2026-09-13',
    'https://api.github.com/repos/lhh666-6/auto-dete/git/ref/tags/r21-jss-2026-09-07-v8',
]
artifacts = []
for url in artifact_urls:
    try:
        response = requests.get(url, headers=HEADERS, timeout=18)
        row = {'url': url, 'http_status': response.status_code, 'accessible': response.ok}
        if response.ok:
            data = response.json()
            row['names'] = [item['name'] for item in data] if isinstance(data, list) else data.get('ref')
        artifacts.append(row)
    except Exception as error:
        artifacts.append({'url': url, 'accessible': None, 'error': str(error)})
output = {'references': results, 'artifact_links': artifacts,
          'reference_manager_check': 'Unavailable: neither Paperpile connector nor CLI is installed.',
          'verification_limit': 'Crossref metadata and primary-page reachability; not a full cited-claim or peer-reviewed-version audit.'}
(HERE / 'external-source-audit.json').write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'references': [{k:r.get(k) for k in ('key','status','title_similarity','page_title','http_status')} for r in results], 'artifacts': artifacts}, ensure_ascii=False, indent=2))
