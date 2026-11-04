#!/usr/bin/env python3
"""Local Enochian rqbit desktop bridge; Python 3 standard library only."""
from __future__ import annotations
import argparse, base64, http.client, json, mimetypes, os, re, secrets, shutil
import signal, subprocess, sys, threading, time, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI_PORT = int(os.environ.get('ENOCHIAN_RQBIT_PORT', '19380'))
ENGINE_PORT = int(os.environ.get('ENOCHIAN_RQBIT_ENGINE_PORT', '19381'))
ORIGIN = f'http://127.0.0.1:{UI_PORT}'
STATE = Path(os.environ.get('ENOCHIAN_RQBIT_STATE', str(Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'enochian-rqbit-state')))
DOWNLOADS = Path(os.environ.get('ENOCHIAN_RQBIT_DOWNLOADS', str(Path.home()/'Downloads/Enochian'))).expanduser().resolve()
VLC = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))/'enochian-vlc/enochian-vlc'
ENGINE = ROOT/'bin/rqbit'
DIST = ROOT/'web'
AUTH = 'Basic '+base64.b64encode(('enochian:'+secrets.token_urlsafe(32)).encode()).decode()
ENGINE_PROCESS: subprocess.Popen | None = None


def engine_request(method: str, path: str, body: bytes | None = None, headers: dict | None = None):
    conn = http.client.HTTPConnection('127.0.0.1', ENGINE_PORT, timeout=60)
    conn.request(method, path, body, {'Authorization':AUTH, **(headers or {})})
    return conn,conn.getresponse()


def engine_json(path: str):
    conn,r=engine_request('GET',path)
    try:
        data=json.loads(r.read())
        if r.status >= 400:raise ValueError(data.get('human_readable', 'Torrent is not available'))
        return data
    finally:conn.close()


class Handler(BaseHTTPRequestHandler):
    server_version='EnochianRqbit/1'
    def log_message(self,format,*args):
        # Do not write user magnet links, filenames or credentials to request logs.
        pass
    def send_bytes(self,code:int,data:bytes,content_type:str='application/json'):
        self.send_response(code)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        if self.command!='HEAD':self.wfile.write(data)
    def reply(self,code:int,data:dict):
        self.send_bytes(code,json.dumps(data).encode())
    def allowed(self,mutation=False):
        if self.headers.get('Host') != f'127.0.0.1:{UI_PORT}':
            self.reply(403,{'error':'Unexpected host'});return False
        origin=self.headers.get('Origin')
        if origin and origin != ORIGIN:
            self.reply(403,{'error':'Use the local Enochian app'});return False
        if mutation and origin != ORIGIN:
            self.reply(403,{'error':'A same-origin request is required'});return False
        return True
    def do_HEAD(self):self.do_GET()
    def do_GET(self):
        if not self.allowed():return
        path=urllib.parse.urlsplit(self.path).path
        if path=='/enochian/health':
            self.reply(200,{'app':'enochian-rqbit','engine':engine_json('/').get('version')});return
        if path in ('/web','/web/','/web/index.html'):
            data=(DIST/'index.html').read_text().replace('<head>','<head><meta name="enochian-bridge" content="1">')
            self.send_bytes(200,data.encode(),'text/html; charset=utf-8');return
        if path.startswith(('/assets/','/web/assets/')):
            rel=urllib.parse.unquote(path.removeprefix('/web/').lstrip('/'))
            target=(DIST/rel).resolve()
            if target.is_relative_to(DIST.resolve()) and target.is_file():
                self.send_bytes(200,target.read_bytes(),mimetypes.guess_type(target)[0] or 'application/octet-stream');return
            self.reply(404,{'error':'Asset not found'});return
        if path=='/favicon.ico':self.send_bytes(204,b'');return
        self.proxy()
    def do_POST(self):
        if not self.allowed(mutation=True):return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<0 or length>16*1024*1024:
                self.reply(413,{'error':'Request is too large'});return
            body=self.rfile.read(length)
            path=urllib.parse.urlsplit(self.path).path
            if path=='/enochian/play':self.play(json.loads(body));return
            if path=='/enochian/stop':
                self.reply(200,{'stopped':True})
                threading.Thread(target=self.server.shutdown,daemon=True).start();return
            self.proxy(body)
        except (ValueError,KeyError,TypeError) as e:self.reply(400,{'error':str(e)})
        except (OSError,http.client.HTTPException) as e:self.reply(502,{'error':str(e)})
    def play(self,data):
        tid=data.get('torrent_id');fid=data.get('file_id');finish=data.get('finish','obsidian')
        if type(tid) is not int or tid<0 or (fid is not None and (type(fid) is not int or fid<0)):
            raise ValueError('Choose a valid torrent and file')
        if finish not in ('obsidian','ivory'):raise ValueError('Invalid finish')
        details=engine_json(f'/torrents/{tid}')
        files=details.get('files',[])
        if fid is None:
            fid=next((i for i,f in enumerate(files) if f.get('included') and re.search(r'\.(mp4|mkv|webm|mov|m4v|avi|mp3|flac|ogg|wav)$',f['name'],re.I)),None)
        if fid is None:raise ValueError('Select a media file in the Files tab')
        if fid>=len(files) or not files[fid].get('included'):raise ValueError('Select this file for download first')
        if not VLC.is_file():raise ValueError('Install Enochian VLC first')
        # Resume the selected torrent before opening its range-enabled HTTP stream.
        state=engine_json(f'/torrents/{tid}/stats/v1').get('state')
        if state in ('paused','error'):
            conn,r=engine_request('POST',f'/torrents/{tid}/start',b'')
            try:
                r.read()
                if r.status>=400:raise ValueError('Could not resume this torrent')
            finally:conn.close()
        elif state != 'live':raise ValueError('The torrent is still initializing. Try again in a moment.')
        url=f'{ORIGIN}/torrents/{tid}/stream/{fid}'
        subprocess.Popen([str(VLC),'--'+finish,url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        self.reply(200,{'opened':True,'torrent_id':tid,'file_id':fid})
    def proxy(self,body=None):
        if not re.match(r'^/(?:\?|$|torrents(?:[/?]|$)|stats(?:[/?]|$)|dht/|stream_logs(?:\?|$)|rust_log(?:\?|$)|metrics(?:\?|$))',self.path):
            self.reply(404,{'error':'Unknown route'});return
        headers={k:self.headers[k] for k in ('Accept','Content-Type','Range','If-Range') if k in self.headers}
        conn=None
        try:
            conn,r=engine_request(self.command,self.path,body,headers)
            self.send_response(r.status)
            for k,v in r.getheaders():
                if k.lower() not in ('transfer-encoding','connection','server','date','access-control-allow-origin'):
                    self.send_header(k,v)
            self.send_header('Connection','close');self.send_header('X-Content-Type-Options','nosniff');self.end_headers()
            if self.command!='HEAD':
                while block:=r.read1(65536):self.wfile.write(block)
        except (BrokenPipeError,ConnectionResetError):pass
        except (OSError,http.client.HTTPException):
            self.close_connection=True
        finally:
            if conn:conn.close()


def health():
    try:
        with urllib.request.urlopen(ORIGIN+'/enochian/health',timeout=2) as r:
            return json.load(r).get('app')=='enochian-rqbit'
    except (OSError,ValueError):return False


def serve():
    global ENGINE_PROCESS
    if not ENGINE.is_file() or not (DIST/'index.html').is_file():
        raise SystemExit('Build the Enochian bundle before launching it.')
    STATE.mkdir(parents=True,exist_ok=True);DOWNLOADS.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',UI_PORT),Handler)
    server.daemon_threads=True
    credentials=base64.b64decode(AUTH.split()[1]).decode()
    env={**os.environ,'RQBIT_HTTP_BASIC_AUTH_USERPASS':credentials,
         'XDG_CONFIG_HOME':str(STATE/'config'),'XDG_CACHE_HOME':str(STATE/'cache'),'XDG_DATA_HOME':str(STATE/'data')}
    args=[str(ENGINE),'--http-api-listen-addr',f'127.0.0.1:{ENGINE_PORT}',
          '--listen-port','4242','--disable-upnp-port-forward']
    if os.environ.get('ENOCHIAN_RQBIT_TEST')=='1':args+=['--disable-dht','--disable-lsd','--disable-trackers','--listen-ip','127.0.0.1']
    args+=['server','start',str(DOWNLOADS),'--persistence-location',str(STATE/'session')]
    log=(STATE/'engine.log').open('ab')
    ENGINE_PROCESS=subprocess.Popen(args,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log)
    def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        for _ in range(200):
            if ENGINE_PROCESS.poll() is not None:raise RuntimeError(f'rqbit exited. See {STATE}/engine.log')
            try:
                if engine_json('/').get('server')=='rqbit':break
            except (OSError,ValueError,http.client.HTTPException):time.sleep(.1)
        else:raise RuntimeError('The rqbit engine did not start')
        server.serve_forever(poll_interval=.2)
    finally:
        server.server_close()
        if ENGINE_PROCESS.poll() is None:
            ENGINE_PROCESS.send_signal(signal.SIGINT)
            try:ENGINE_PROCESS.wait(timeout=15)
            except subprocess.TimeoutExpired:ENGINE_PROCESS.kill();ENGINE_PROCESS.wait()
        log.close()


def launch():
    if not health():
        STATE.mkdir(parents=True,exist_ok=True)
        with (STATE/'companion.log').open('ab') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--serve'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        for _ in range(200):
            if health():break
            if process.poll() is not None:raise SystemExit(f'Enochian Rqbit could not start. See {STATE}/companion.log')
            time.sleep(.1)
        else:raise SystemExit('Enochian Rqbit did not start')
    chromium=shutil.which('chromium')
    if chromium:
        subprocess.Popen([chromium,'--class=EnochianRqbit','--app='+ORIGIN+'/web/'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    else:subprocess.Popen(['xdg-open',ORIGIN+'/web/'],start_new_session=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Enochian rqbit companion')
    parser.add_argument('--serve',action='store_true');parser.add_argument('--stop',action='store_true')
    opts=parser.parse_args()
    if opts.serve:serve()
    elif opts.stop:
        request=urllib.request.Request(ORIGIN+'/enochian/stop',data=b'',headers={'Origin':ORIGIN},method='POST')
        try:urllib.request.urlopen(request,timeout=5).close()
        except OSError:pass
    else:launch()
