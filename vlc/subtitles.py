#!/usr/bin/env python3
"""English SRT selection and explicit, cancelable OpenSubtitles download consent."""
from __future__ import annotations
import base64,hashlib,json,os,re,shutil,signal,subprocess,sys,tempfile,threading,time,tarfile
from pathlib import Path
from urllib.parse import urlencode,urlsplit,unquote
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
MAX_SRT=5*1024*1024
class Player:
 def __init__(self,data):self.data=data;self.auth='Basic '+base64.b64encode((':'+data['password']).encode()).decode()
 def request(self,route='enochian.json',**params):
  url=f'http://127.0.0.1:{self.data["port"]}/requests/{route}'+('?' + urlencode(params) if params else '')
  with urlopen(Request(url,headers={'Authorization':self.auth}),timeout=8) as response:return json.load(response)
 def current(self):return self.request().get('uri')
 def apply(self,path,uri):
  before=self.request()
  if before.get('uri')!=uri:raise ValueError('The video changed. The subtitle was saved but has not been applied to another video.')
  result=self.request(subtitle=path.resolve().as_uri(),expected=uri)
  if result.get('error'):raise ValueError(result['error'])
  if result.get('subtitle_added') is False:raise ValueError('VLC could not read this subtitle file.')
  for _ in range(30):
   result=self.request()
   if result.get('uri')!=uri:raise ValueError('The video changed. The subtitle has not been applied to another video.')
   if result.get('spu',-1)!=-1 and (result.get('spu') not in (before.get('subtitle_ids') or []) or result.get('spu')==english_track(result)):break
   time.sleep(.1)
  else:raise ValueError('VLC could not activate this subtitle file.')
  self.request(message='English subtitles enabled')


def local_media(uri):
 value=urlsplit(uri)
 if value.scheme=='file':return Path(unquote(value.path)).resolve()
 # Resolve only the suite's loopback rqbit stream contract; never arbitrary hosts.
 match=re.fullmatch(r'/torrents/(\d+)/stream/(\d+)(?:/.*)?',value.path)
 if value.scheme=='http' and value.hostname in ('127.0.0.1','localhost') and match:
  try:
   with urlopen(f'http://{value.netloc}/torrents/{match[1]}',timeout=3) as response:details=json.load(response)
   file=details['files'][int(match[2])];components=file['components']
   if not components or any(c in ('','..','.') or '/' in c or '\\' in c for c in components):return None
   root=Path(details['output_folder']).resolve();target=root.joinpath(*components).resolve()
   return target if target.is_relative_to(root) else None
  except (OSError,ValueError,KeyError,IndexError):return None
 return None


def english_sidecar(video):
 if not video:return None
 try:files={p.name.casefold():p for p in video.parent.iterdir() if p.is_file()}
 except OSError:return None
 for suffix in ['.en.srt','.eng.srt','.english.srt','.en-us.srt','.en-gb.srt','.srt']:
  target=files.get((video.stem+suffix).casefold())
  if target and 0<target.stat().st_size<=MAX_SRT:return target
 return None


def english_track(state):
 ids=state.get('subtitle_ids') or [];names=state.get('subtitle_names') or []
 if isinstance(ids,dict):ids=list(ids.values())
 if isinstance(names,dict):names=list(names.values())
 for ident,name in zip(ids,names):
  if int(ident)>=0 and re.search(r'\b(english|eng|en)\b',str(name),re.I):return int(ident)
 return None


def hash_proxy(video,target):
 """Give the official client the original filename/size/hash without copying a film.
 The sparse temporary proxy contains only the hash's first/last 64 KiB and is
 never played. It is removed with the download staging directory.
 """
 size=video.stat().st_size
 with video.open('rb') as source,target.open('xb') as output:
  output.truncate(size);output.seek(0);output.write(source.read(65536))
  if size>65536:source.seek(max(0,size-65536));output.seek(max(0,size-65536));output.write(source.read(65536))


def download_english(video,cache,cancelled,started=lambda p:None):
 if not video or not video.is_file():raise ValueError('This stream has no local video file to match. Open an English SRT manually.')
 node=shutil.which('node');client=ROOT/'subtitle-client/node_modules/opensubs-cli/dist/Run.js'
 if not node or not client.is_file():raise ValueError('The subtitle downloader is not installed. Reinstall the complete Linux bundle, or choose a local SRT.')
 cache.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='search-',dir=cache) as name:
  stage=Path(name);proxy=stage/video.name;hash_proxy(video,proxy)
  if cancelled.is_set():return None
  process=subprocess.Popen([node,str(client),str(proxy),'--lang','en','--no-prompt'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env={**os.environ,'NO_COLOR':'1'})
  started(process)
  if cancelled.is_set() and process.poll() is None:process.terminate()
  try:output,_=process.communicate(timeout=100)
  except subprocess.TimeoutExpired:process.terminate();process.communicate();raise ValueError('Subtitle search timed out. Try again or choose a local SRT.')
  if cancelled.is_set():return None
  choices=sorted(stage.rglob('*.en.srt'))
  if not choices:
   if any(word in output.lower() for word in ['quota','limit','login','log in','authentication']):raise ValueError('OpenSubtitles requires sign-in or its download limit has been reached. You can choose a local SRT or try again later.')
   raise ValueError('No matching English subtitle was downloaded. Try a more descriptive video filename or choose a local SRT.')
  chosen=choices[0]
  if not 0<chosen.stat().st_size<=MAX_SRT:raise ValueError('The downloaded subtitle is empty or too large.')
  text=chosen.read_text(encoding='utf-8-sig')
  if '-->' not in text:raise ValueError('The downloaded file is not a valid SRT subtitle.')
  target=cache/(video.stem+'.en.srt');temp=cache/(video.stem+'.download');temp.write_text(text,encoding='utf-8');temp.replace(target)
  # Never replace an existing user subtitle. The app cache is a read-only fallback.
  beside=video.with_name(video.stem+'.en.srt')
  try:
   with beside.open('xb') as output:output.write(target.read_bytes())
   return beside
  except OSError:return target


def run_dialog(control):
 import gi;gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0')
 from gi.repository import Gtk,Gdk,GLib,GdkPixbuf
 player=Player(control);state=player.request();uri=state.get('uri')
 finish=control['finish'];dark=finish=='obsidian'
 provider=Gtk.CssProvider();provider.load_from_data(('''window,dialog{background:%s;color:%s}label{color:%s;font-family:monospace;font-size:13px}button{background:transparent;border:0;box-shadow:none;padding:0}button:focus{outline:2px solid #cc0000;outline-offset:2px}''' % ('#121214' if dark else '#ededf0','#f2f2f4' if dark else '#1d1d1f','#f2f2f4' if dark else '#1d1d1f')).encode());Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
 archive=tarfile.open(control['skin'])
 def key(label,response,dialog):
  button=Gtk.Button();image=Gtk.Image();button.add(image)
  def set_image(state):
   raw=archive.extractfile('assets/mini-'+label+'-'+state+'.png').read();loader=GdkPixbuf.PixbufLoader.new_with_type('png');loader.write(raw);loader.close();image.set_from_pixbuf(loader.get_pixbuf())
  set_image('up');button.connect('pressed',lambda *_:set_image('down'));button.connect('released',lambda *_:set_image('up'));button.set_can_default(True);dialog.add_action_widget(button,response);return button
 def dialog(title,text,actions):
  d=Gtk.Dialog(title=title);d.set_default_size(520,190);d.set_border_width(18);d.set_resizable(False)
  label=Gtk.Label(label=text);label.set_line_wrap(True);label.set_max_width_chars(62);label.set_xalign(0);d.get_content_area().pack_start(label,True,True,12)
  cancel_key=None
  for name,response in actions:
   button=key(name,response,d)
   if response==Gtk.ResponseType.CANCEL:cancel_key=button
  d.connect('key-press-event',lambda _,event:d.response(Gtk.ResponseType.CANCEL) if event.keyval==Gdk.KEY_Escape else False);d.show_all()
  if cancel_key:cancel_key.grab_default();cancel_key.grab_focus()
  return d,label
 def info(text):
  d,_=dialog('English subtitles',text,[('close',Gtk.ResponseType.CLOSE)]);d.run();d.destroy()
 if not uri:info('Open a video before choosing English subtitles.');return
 video=local_media(uri);cache=Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))/'enochian-vlc/subtitles'/hashlib.sha256(uri.encode()).hexdigest()[:24]
 track=english_track(state)
 if track is not None and state.get('spu')==track:player.request(message='English subtitles already enabled');return
 local=english_sidecar(video) or english_sidecar(cache/(video.name if video else 'stream.mp4'))
 if local:
  try:player.apply(local,uri)
  except (OSError,ValueError) as e:info(str(e))
  return
 track=english_track(state)
 if track is not None:player.request(spu=track,expected=uri,message='English subtitle track enabled');return
 if not video:info('This stream has no local file or known English subtitle track. Use Menu → Subtitle → Add Subtitle File to choose an SRT.');return
 d,_=dialog('English subtitles',f'No English SRT was found for {video.name}.\n\nDownload the best English match from OpenSubtitles? The file name and a content hash will be sent only if you choose Download.',[('download',1),('open',2),('cancel',Gtk.ResponseType.CANCEL)])
 d.set_default_response(Gtk.ResponseType.CANCEL)
 choice=d.run();d.destroy()
 if choice==2:
  chooser=Gtk.FileChooserDialog(title='Open English SRT',action=Gtk.FileChooserAction.OPEN);chooser.add_buttons('Cancel',Gtk.ResponseType.CANCEL,'Open',Gtk.ResponseType.OK);f=Gtk.FileFilter();f.set_name('SRT subtitles');f.add_pattern('*.srt');chooser.add_filter(f)
  if chooser.run()==Gtk.ResponseType.OK:
   try:player.apply(Path(chooser.get_filename()),uri)
   except (OSError,ValueError) as e:info(str(e))
  chooser.destroy();return
 if choice!=1:return
 cancelled=threading.Event();running=[None]
 pending,label=dialog('English subtitles','Finding and downloading English subtitles…',[('cancel',Gtk.ResponseType.CANCEL)])
 def done(path,error):
  if cancelled.is_set():return False
  pending.response(Gtk.ResponseType.OK);pending.destroy()
  try:
   if error:info(str(error))
   elif path:player.apply(path,uri)
  except (OSError,ValueError) as e:info(str(e))
  Gtk.main_quit();return False
 def work():
  try:path=download_english(video,cache,cancelled,lambda p:running.__setitem__(0,p));error=None
  except Exception as e:path=None;error=e
  GLib.idle_add(done,path,error)
 def cancel(*_):
  cancelled.set()
  if running[0] and running[0].poll() is None:running[0].terminate()
  pending.destroy();Gtk.main_quit()
 pending.connect('response',lambda _,value:cancel() if value in (Gtk.ResponseType.CANCEL,Gtk.ResponseType.DELETE_EVENT) else None);signal.signal(signal.SIGTERM,cancel)
 threading.Thread(target=work,daemon=True).start();Gtk.main()
 archive.close()

if __name__=='__main__':
 try:run_dialog(json.loads(Path(sys.argv[1]).read_text()))
 except (OSError,ValueError) as error:
  message='Could not connect to this player. Reopen SUBS, or reopen the player if it persists.'
  if shutil.which('notify-send'):subprocess.run(['notify-send','Enochian subtitles',message],check=False)
  print(message,file=sys.stderr)
