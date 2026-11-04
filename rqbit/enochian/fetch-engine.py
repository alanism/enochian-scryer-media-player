#!/usr/bin/env python3
"""Fetch the pinned official Linux x86_64 engine, with integrity verification."""
import concurrent.futures, hashlib, os, platform, tempfile, time, urllib.request
from pathlib import Path
URL='https://github.com/ikatson/rqbit/releases/download/v9.1.0/rqbit-linux-amd64'
SHA='921061a82ee6a6b26754c6367886b5b6b4ce5916d3edd5db79c6cd5f2c23499f'
SIZE=28630928
if platform.system()!='Linux' or platform.machine() not in ('x86_64','amd64'):
    raise SystemExit('Use --source-engine on platforms other than Linux x86_64.')
dest=Path(__file__).resolve().parent/'bin/rqbit';dest.parent.mkdir(exist_ok=True)
if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==SHA:
    print('Official rqbit engine already verified.');raise SystemExit(0)
with urllib.request.urlopen(urllib.request.Request(URL,method='HEAD'),timeout=30) as response:url=response.url
chunk=524288
with tempfile.TemporaryDirectory(prefix='rqbit-download-') as folder:
    def fetch(i):
        start=i*chunk;end=min(SIZE-1,start+chunk-1)
        for attempt in range(4):
            try:
                req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
                with urllib.request.urlopen(req,timeout=90) as response:
                    if response.status!=206:raise ValueError('The release host did not honor the range request')
                    data=response.read()
                if len(data)!=end-start+1:raise ValueError('Incomplete release chunk')
                (Path(folder)/str(i)).write_bytes(data);return
            except Exception:
                if attempt==3:raise
                time.sleep(attempt+1)
    count=(SIZE+chunk-1)//chunk
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(fetch,range(count)))
    data=b''.join((Path(folder)/str(i)).read_bytes() for i in range(count))
    if hashlib.sha256(data).hexdigest()!=SHA:raise SystemExit('Release checksum mismatch')
    temporary=dest.with_suffix('.download');temporary.write_bytes(data);temporary.chmod(0o755);os.replace(temporary,dest)
print('Official rqbit 9.1.0 engine verified and ready.')
