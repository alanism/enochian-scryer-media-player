#!/usr/bin/env python3
"""Small X11 adapter for the two application actions absent from VLC Skins2.
Input-only children cover only this VLC process's Full and English-SRT keys.
The original bitmap controls still paint their own press/release feedback.
"""
from __future__ import annotations
import base64,ctypes as C,io,json,os,secrets,signal,socket,subprocess,sys,tempfile,time,tarfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
D=C.c_void_p;W=C.c_ulong;I=C.c_int;U=C.c_uint;L=C.c_long
class Button(C.Structure):
 _fields_=[('type',I),('serial',W),('send_event',I),('display',D),('window',W),('root',W),('subwindow',W),('time',W),('x',I),('y',I),('x_root',I),('y_root',I),('state',U),('button',U),('same_screen',I)]
class Motion(C.Structure):
 _fields_=Button._fields_[:-2]+[('is_hint',C.c_char),('same_screen',I)]
class Client(C.Structure):
 _fields_=[('type',I),('serial',W),('send_event',I),('display',D),('window',W),('message_type',W),('format',I),('data',L*5)]
class Key(C.Structure):_fields_=Button._fields_[:-2]+[('keycode',U),('same_screen',I)]
class Event(C.Union):_fields_=[('button',Button),('motion',Motion),('client',Client),('key',Key),('pad',L*24)]
class Attrs(C.Structure):
 _fields_=[('background_pixmap',W),('background_pixel',W),('border_pixmap',W),('border_pixel',W),('bit_gravity',I),('win_gravity',I),('backing_store',I),('backing_planes',W),('backing_pixel',W),('save_under',I),('event_mask',L),('do_not_propagate_mask',L),('override_redirect',I),('colormap',W),('cursor',W)]
class X11:
 def __init__(self):
  self.x=C.CDLL('libX11.so.6');x=self.x
  specs={'XOpenDisplay':([C.c_char_p],D),'XDefaultRootWindow':([D],W),'XInternAtom':([D,C.c_char_p,I],W),'XQueryTree':([D,W,C.POINTER(W),C.POINTER(W),C.POINTER(C.POINTER(W)),C.POINTER(U)],I),'XGetWindowProperty':([D,W,W,L,L,I,W,C.POINTER(W),C.POINTER(I),C.POINTER(W),C.POINTER(W),C.POINTER(C.POINTER(C.c_ubyte))],I),'XGetGeometry':([D,W,C.POINTER(W),C.POINTER(I),C.POINTER(I),C.POINTER(U),C.POINTER(U),C.POINTER(U),C.POINTER(U)],I),'XCreateWindow':([D,W,I,I,U,U,U,I,U,D,W,C.POINTER(Attrs)],W),'XSelectInput':([D,W,L],I),'XMapWindow':([D,W],I),'XMoveResizeWindow':([D,W,I,I,U,U],I),'XSendEvent':([D,W,I,L,C.POINTER(Event)],I),'XPending':([D],I),'XNextEvent':([D,C.POINTER(Event)],I),'XSync':([D,I],I),'XCloseDisplay':([D],I),'XFree':([D],I),'XLookupKeysym':([C.POINTER(Key),I],W),'XSetTransientForHint':([D,W,W],I)}
  for name,(args,result) in specs.items():f=getattr(x,name);f.argtypes=args;f.restype=result
  self.error=C.CFUNCTYPE(I,D,D)(lambda *_:0);x.XSetErrorHandler(self.error)
  self.d=x.XOpenDisplay(None)
  if not self.d:raise OSError('No X11 display')
  self.root=x.XDefaultRootWindow(self.d)
 def atom(self,name):return self.x.XInternAtom(self.d,name.encode(),False)
 def prop(self,w,name):
  t=W();fmt=I();n=W();remaining=W();data=C.POINTER(C.c_ubyte)()
  self.x.XGetWindowProperty(self.d,w,self.atom(name),0,4096,False,0,C.byref(t),C.byref(fmt),C.byref(n),C.byref(remaining),C.byref(data))
  if not data:return None
  try:return list(C.cast(data,C.POINTER(W))[:n.value]) if fmt.value==32 else C.string_at(data,n.value*(fmt.value//8))
  finally:self.x.XFree(data)
 def children(self,w):
  root=W();parent=W();data=C.POINTER(W)();n=U();self.x.XQueryTree(self.d,w,C.byref(root),C.byref(parent),C.byref(data),C.byref(n));result=list(data[:n.value]) if data else []
  if data:self.x.XFree(data)
  return result
 def geometry(self,w):
  root=W();x=I();y=I();width=U();height=U();border=U();depth=U();self.x.XGetGeometry(self.d,w,C.byref(root),C.byref(x),C.byref(y),C.byref(width),C.byref(height),C.byref(border),C.byref(depth));return width.value,height.value
 def forward(self,w,kind,px,py,button=1):
  e=Event();v=e.motion if kind==6 else e.button;v.type=kind;v.display=self.d;v.window=w;v.root=self.root;v.same_screen=1;v.x=px;v.y=py;v.send_event=1
  if kind!=6:v.button=button
  self.x.XSendEvent(self.d,w,False,{4:4,5:8,6:64}[kind],C.byref(e));self.x.XSync(self.d,False)
 def fullscreen(self,w,enabled):
  e=Event();v=e.client;v.type=33;v.display=self.d;v.window=w;v.message_type=self.atom('_NET_WM_STATE');v.format=32;v.data[0]=1 if enabled else 0;v.data[1]=self.atom('_NET_WM_STATE_FULLSCREEN');v.data[3]=1
  self.x.XSendEvent(self.d,self.root,False,(1<<19)|(1<<20),C.byref(e));self.x.XSync(self.d,False)


def controls(skin):
 with tarfile.open(skin) as t:
  root=ET.fromstring(t.extractfile('theme.xml').read());layout=root.find("Window[@id='main']/Layout");bitmaps={b.get('id'):b.get('file') for b in root.findall('Bitmap')};result={}
  for name in ['window-fullscreen','english-subtitles']:
   e=next(c for c in layout if c.get('id')==name);bitmap=e.get('up') or e.get('up1');data=t.extractfile(bitmaps[bitmap]).read();w=int.from_bytes(data[16:20],'big');h=int.from_bytes(data[20:24],'big')
   result[name]={'x':int(e.get('x')),'y':int(e.get('y')),'w':w,'h':h,'anchor':e.get('lefttop','lefttop')}
 return int(layout.get('width')),int(layout.get('height')),result


def main():
 args=sys.argv[1:]
 if args and args[0]=='--':args=args[1:]
 skin=next(Path(a.split('=',1)[1]) for a in args if a.startswith('--skins2-last='));basew,baseh,buttons=controls(skin)
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 password=secrets.token_urlsafe(32)
 args=args[:1]+['--extraintf=http','--http-host=127.0.0.1',f'--http-port={port}',f'--http-password={password}',f'--http-src={ROOT/"http"}']+args[1:]
 child=subprocess.Popen(args)
 control={'pid':child.pid,'bridge_pid':os.getpid(),'port':port,'password':password,'skin':str(skin),'finish':'ivory' if 'Ivory' in skin.name else 'obsidian'}
 private_dir=Path(tempfile.mkdtemp(prefix='enochian-player-',dir=os.environ.get('XDG_RUNTIME_DIR')));path=private_dir/'control.json';path.write_text(json.dumps(control));path.chmod(0o600)
 test=os.environ.get('ENOCHIAN_TEST_CONTROL')
 if test:
  p=Path(test);p.write_text(json.dumps(control));p.chmod(0o600)
 workers=[]
 def stop(*_):
  if child.poll() is None:child.terminate()
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  try:x=X11()
  except OSError:return child.wait()
  window=None;overlays={};rects={};mode=False;last_size=None
  for _ in range(300):
   if child.poll() is not None:return child.returncode
   for w in x.children(x.root):
    if x.prop(w,'_NET_WM_PID')==[child.pid] and x.prop(w,'WM_NAME')==b'VLC (TopWindow)':window=w;break
   if window:break
   time.sleep(.03)
  if not window:return child.wait()
  x.x.XSelectInput(x.d,window,(1<<1)|(1<<17));control['window']=window
  path.write_text(json.dumps(control));path.chmod(0o600)
  if test:Path(test).write_text(json.dumps(control));Path(test).chmod(0o600)
  for name,b in buttons.items():
   attrs=Attrs();attrs.event_mask=4|8|16|32|64
   overlay=x.x.XCreateWindow(x.d,window,b['x'],b['y'],b['w'],b['h'],0,0,2,None,1<<11,C.byref(attrs));x.x.XMapWindow(x.d,overlay);overlays[overlay]=name
  while child.poll() is None:
   width,height=x.geometry(window)
   if (width,height)!=last_size:
    for overlay,name in overlays.items():
     b=buttons[name];px=b['x']+(width-basew if b['anchor'].startswith('right') else 0);py=b['y']+(height-baseh if b['anchor'].endswith('bottom') else 0);rects[overlay]=(px,py,b['w'],b['h']);x.x.XMoveResizeWindow(x.d,overlay,px,py,b['w'],b['h'])
    last_size=(width,height);x.x.XSync(x.d,False)
   while x.x.XPending(x.d):
    e=Event();x.x.XNextEvent(x.d,C.byref(e));target=e.button.window
    if target in overlays and e.button.type in (4,5,6):
     px,py,bw,bh=rects[target];localx,localy=e.button.x,e.button.y
     if e.button.type==4:x.forward(window,6,px+localx,py+localy)
     x.forward(window,e.button.type,px+localx,py+localy,e.button.button)
     if e.button.type==5 and e.button.button==1 and 0<=localx<bw and 0<=localy<bh:
      if overlays[target]=='window-fullscreen':mode=not mode;x.fullscreen(window,mode)
      elif not any(p.poll() is None for p in workers):
       workers=[subprocess.Popen([sys.executable,str(ROOT/'subtitles.py'),str(path)],env={**os.environ,'GDK_BACKEND':'x11','GDK_SCALE':'1','GDK_DPI_SCALE':'1'})]
    elif target==window and e.key.type==3 and mode and x.x.XLookupKeysym(C.byref(e.key),0)==0xff1b:
     b=buttons['window-fullscreen'];px=b['x']+width-basew+b['w']//2;py=b['y']+b['h']//2
     for kind in (6,4,5):x.forward(window,kind,px,py)
     mode=False;x.fullscreen(window,False)
   time.sleep(.02)
  x.x.XCloseDisplay(x.d)
  return child.returncode
 finally:
  for worker in workers:
   if worker.poll() is None:worker.terminate()
  if child.poll() is None:
   child.terminate()
   try:child.wait(timeout=5)
   except subprocess.TimeoutExpired:child.kill();child.wait()
  path.unlink(missing_ok=True)
  try:private_dir.rmdir()
  except OSError:pass
if __name__=='__main__':raise SystemExit(main())
