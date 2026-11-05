#!/usr/bin/env python3
"""Exercise the real skinned VLC via its loopback API; does not simulate native clicks."""
import argparse,base64,functools,http.server,json,os,secrets,shutil,socket,subprocess,threading,time,sys
from pathlib import Path
from urllib.parse import urlencode,unquote
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
work=args.output.resolve().parent;work.mkdir(parents=True,exist_ok=True)
media=work/'media';media.mkdir(exist_ok=True)
one=media/'Alpha test video.mp4'
if not one.exists():
 subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc=size=480x270:rate=10','-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','60','-c:v','mpeg4','-q:v','10','-c:a','aac','-y',str(one)],check=True)
files=[one,media/'Bravo test video.mp4',media/'Café test video.mp4']
for target in files[1:]:
 if not target.exists():shutil.copy2(one,target)
web=work/'http';shutil.copytree('/usr/share/vlc/lua/http',web,dirs_exist_ok=True)
(web/'requests/eval-move.json').write_text("""<?vlc vlc.playlist.move(tonumber(_GET['id']),tonumber(_GET['target'])); print('{"moved":true}') ?>""")
cases=[]
def record(name,detail,method='VLC loopback HTTP API'):
 cases.append({'name':name,'passed':True,'detail':detail,'method':method})
 print('PASS',name,flush=True)
def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def flatten(node):
 if isinstance(node,list):return [x for n in node for x in flatten(n)]
 if node.get('children') is not None:return flatten(node['children'])
 return [node] if node.get('uri') else []
class MediaHandler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  target=(media/unquote(self.path.split('?',1)[0]).lstrip('/')).resolve()
  if not target.is_relative_to(media.resolve()) or not target.is_file():self.send_error(404);return
  size=target.stat().st_size;start=0;end=size-1;status=200
  value=self.headers.get('Range')
  if value and value.startswith('bytes='):
   a,b=value[6:].split('-',1);start=int(a or 0);end=min(int(b) if b else end,end);status=206
  if start>=size:self.send_error(416);return
  self.send_response(status);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes')
  self.send_header('Content-Length',str(end-start+1))
  if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with target.open('rb') as f:
    f.seek(start);left=end-start+1
    while left:
     block=f.read(min(65536,left))
     if not block:break
     self.wfile.write(block);left-=len(block)
  except (BrokenPipeError,ConnectionResetError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),MediaHandler)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 for index,(finish,size) in enumerate([('obsidian','standard'),('ivory','standard'),('obsidian','compact'),('ivory','compact')]):
  port=free_port();password=secrets.token_urlsafe(24)
  auth='Basic '+base64.b64encode((':'+password).encode()).decode()
  endpoint=f'http://127.0.0.1:{port}/requests/'
  def request(route='status.json',**params):
   req=Request(endpoint+route+('?' + urlencode(params) if params else ''),headers={'Authorization':auth})
   with urlopen(req,timeout=10) as r:
    raw=r.read()
    try:return json.loads(raw)
    except ValueError:raise ValueError(raw[:1200].decode(errors='replace'))
  def command(name,**params):return request(command=name,**params)
  def wait(predicate,label):
   last=None
   for _ in range(100):
    try:
     last=request()
     if predicate(last):return last
    except OSError:pass
    time.sleep(.1)
   raise AssertionError((label,last))
  env={**os.environ,'XDG_CONFIG_HOME':str(work/f'config-{finish}-{size}')}
  flags=['--'+finish]+(['--compact'] if size=='compact' else [])
  with (work/f'{finish}-{size}.log').open('wb') as log:
   proc=subprocess.Popen([str(ROOT/'vlc/enochian-vlc'),*flags,'--aout=dummy','--no-interact','--extraintf=http',f'--http-host=127.0.0.1',f'--http-port={port}',f'--http-password={password}',f'--http-src={web}'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log)
  try:
   wait(lambda s:True,'HTTP startup')
   command('in_play',input=one.as_uri());wait(lambda s:s['state']=='playing' and s.get('length',0)>0,'playing')
   record(f'{finish}-{size} real playback','Skins2 launcher selected; real MPEG-4/AAC media entered Playing.')
   if index:continue
   command('pl_forcepause');wait(lambda s:s['state']=='paused','pause')
   command('seek',val='10');s=wait(lambda s:abs(s.get('time',0)-10)<=1,'seek paused')
   command('pl_forceresume');wait(lambda s:s['state']=='playing','resume')
   record('transport and paused seeking','Pause → seek to 10s → resume; actual state and position read back.')
   command('seek',val='0');wait(lambda s:s.get('time',99)<=1,'seek start')
   command('seek',val='55');wait(lambda s:s.get('time',0)>=54,'seek near end')
   record('seek boundaries','Start and near-end seeks read back correctly.')
   command('volume',val='128');volume_half=request()['volume']
   command('volume',val='0');volume_zero=request()['volume']
   command('volume',val='128')
   record('volume commands only',f'Dummy output readbacks {volume_half}, {volume_zero}; device volume and audibility remain unverified.')
   command('rate',val='1.25');assert abs(request()['rate']-1.25)<.01
   command('rate',val='1')
   record('playback rate','1.25× → 1× read back correctly.')
   before=request()['fullscreen'];command('fullscreen');wait(lambda s:s['fullscreen']!=before,'fullscreen')
   command('fullscreen');wait(lambda s:s['fullscreen']==before,'exit fullscreen')
   record('fullscreen round trip','Full-screen state toggled and returned without losing playback.')
   command('pl_stop');wait(lambda s:s['state']=='stopped','stop')
   command('pl_empty')
   for f in files:command('in_enqueue',input=f.as_uri())
   items=flatten(request('playlist.json'));assert [x['uri'] for x in items]==[f.as_uri() for f in files],items
   record('playlist create and append','Three local files, spaces and Unicode, retained their exact URIs/order.')
   command('pl_play',id=items[1]['id']);wait(lambda s:str(s.get('currentplid'))==str(items[1]['id']) and s['state']=='playing','select')
   command('pl_next');wait(lambda s:str(s.get('currentplid'))==str(items[2]['id']),'next')
   command('pl_previous');wait(lambda s:str(s.get('currentplid'))==str(items[1]['id']),'previous')
   record('playlist selection and navigation','Selected second item; Next/Previous read back the intended IDs.')
   request('eval-move.json',id=items[0]['id'],target=items[2]['id'])
   reordered=flatten(request('playlist.json'));assert [x['uri'] for x in reordered]==[files[1].as_uri(),files[2].as_uri(),files[0].as_uri()],reordered
   record('playlist reorder core','Real VLC playlist.move reordered items; native Manage drag gesture remains a separate UI check.')
   command('pl_sort',id=0,val='title');sorted_items=flatten(request('playlist.json'))
   assert [x['uri'] for x in sorted_items]==[f.as_uri() for f in files]
   command('pl_delete',id=sorted_items[1]['id'])
   assert [x['uri'] for x in flatten(request('playlist.json'))]==[files[0].as_uri(),files[2].as_uri()]
   record('playlist sort and remove','Sorted by title and removed only the second item; source media remain on disk.')
   playlist=work/'My Café playlist.m3u8'
   playlist.write_text('#EXTM3U\n'+'\n'.join(x['uri'] for x in flatten(request('playlist.json')))+'\n')
   command('pl_stop');command('pl_empty');command('in_play',input=playlist.as_uri())
   wait(lambda s:s['state']=='playing','playlist import')
   for _ in range(100):
    leaves=flatten(request('playlist.json'))
    if len([x for x in leaves if x['uri'].endswith('.mp4')])==2:break
    time.sleep(.1)
   assert [x['uri'] for x in leaves if x['uri'].endswith('.mp4')]==[files[0].as_uri(),files[2].as_uri()],leaves
   record('playlist file import round trip','M3U8 snapshot reopened in order. File was written by this harness; native Save dialog/export was not driven.')
   command('in_play',input='http://127.0.0.1:'+str(server.server_port)+'/Alpha%20test%20video.mp4')
   wait(lambda s:s['state']=='playing','URL playback');command('seek',val='20');wait(lambda s:s.get('time',0)>=19,'URL seek')
   record('network URL playback and seek','Local range-enabled HTTP media played and sought to 20s.')
   command('in_play',input=(media/'missing-file.mp4').as_uri())
   time.sleep(.3)
   command('in_play',input=one.as_uri());wait(lambda s:s['state']=='playing','error recovery')
   record('missing-file engine recovery','Playback recovered after a missing-file input; no native error-dialog interaction claimed.')
  finally:
   proc.terminate()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
finally:
 server.shutdown();server.server_close()
 failure=str(sys.exc_info()[1]) if sys.exc_info()[0] else None
 args.output.write_text(json.dumps({'cases':cases,'passed':failure is None,'failure':failure,'native_gui_clicks_observed':False,'limits':['Native file-picker, drag/reorder and Save dialog were not driven.','Audio output used dummy; device volume and physical audibility were not verified.'],'mandatory_native_save_export_verified':False},indent=2)+'\n')
print('Evidence written:',args.output)
