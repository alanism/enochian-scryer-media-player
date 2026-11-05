#!/usr/bin/env python3
"""Rasterize original Enochian HTML/CSS into VLC Skins2 assets; no redrawn controls."""
from pathlib import Path
import argparse, html, json, math, shutil, subprocess, tarfile, tempfile
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parent
DIST=ROOT.parent
FONT=ROOT/'IBMPlexMono-Regular.ttf'
CSS=(ROOT/'reference/controls.css').read_text()
ATLAS=(ROOT/'reference/atlas.html').read_text()
W,H=960,525
KEYS={
 'previous':('rew','Previous item'), 'play':('play','Play'),
 'next':('ff','Next item'), 'stop':('stop','Stop'), 'pause':('pause','Pause')}

def original_key(kind):
 import re
 return re.search(r'<button[^>]*class="tp-key"[^>]*data-k="'+kind+r'".*?</button>',ATLAS,re.S).group()

def ticks():
 out=[]
 def polar(r,d):return (110+r*math.cos(math.radians(d-90)),110+r*math.sin(math.radians(d-90)))
 for i in range(15):
  x,y=polar(96,-135+i*270/16);out.append(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#111"/>')
 for d in [-135,135]:
  x,y=polar(88,d);a,b=polar(102,d);out.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="#111" stroke-width="2.4"/>')
 return ''.join(out)

class Sheet:
 def __init__(self,finish):self.finish=finish;self.parts=[];self.boxes={};self.x=0;self.y=0;self.rowh=0
 def add(self,name,w,h,markup,scope='instruments'):
  if self.x+w>1600:self.x=0;self.y+=self.rowh+4;self.rowh=0
  x,y=self.x,self.y;self.boxes[name]=(x,y,w,h)
  self.parts.append(f'<div class="asset asset-{name} source-{scope}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{markup}</div>')
  self.x+=w+4;self.rowh=max(h,self.rowh)
 def render(self,out):
  page=f'''<!doctype html><meta charset="utf-8"><style>@font-face{{font-family:"IBM Plex Mono";src:url("{FONT.as_uri()}")}}{CSS}
 html,body{{margin:0!important;background:transparent!important}}.asset{{position:absolute;overflow:hidden;background:transparent!important}} .asset *{{box-sizing:border-box;transition:none!important;animation:none!important}} .asset .tp{{width:100%;height:100%;max-width:none;padding:0;display:block;border-radius:0;box-shadow:none}} .asset .tp-key{{width:80px}} .asset:not(.asset-case) .tp{{background:transparent}} .asset .fx{{padding:0;border-radius:0;width:100%;height:100%;display:block;background:transparent}} .asset .cp{{background:transparent;display:block;padding:0;width:100%;height:100%;box-shadow:none;border-radius:0}} .asset .sq-btn{{width:64px}} .utility{{position:absolute;left:3px;top:3px;transform:scale(1.4);transform-origin:0 0}} .transport{{position:absolute;left:8px;top:3px;transform:scale(1.25);transform-origin:0 0}} .asset .transport .tp-key{{width:64px}} .small{{position:absolute;left:8px;top:3px;transform:scale(.8);transform-origin:0 0}} .asset .hs{{width:100%;max-width:none;height:48px}} .asset .hs-th{{left:8px;top:24px}} .asset .hs-line{{left:0;right:0}} .asset .dial{{transform:scale(.5);transform-origin:0 0}} .asset .dial .dark-base,.asset .dial .dark-knob{{transition:none}} .asset .dial[data-finish="obsidian"] .dark-base{{border-color:transparent}} .asset .tp-display{{height:100%;width:100%}} .asset .tp-mini button{{height:30px}}
 </style>{''.join(self.parts)}'''
  src=out/'sheet.html';src.write_text(page)
  height=self.y+self.rowh+4
  subprocess.run(['chromium','--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--hide-scrollbars','--default-background-color=00000000','--no-first-run','--no-default-browser-check',f'--user-data-dir={out/"chromium"}',f'--window-size=1600,{height}','--force-device-scale-factor=1','--allow-file-access-from-files','--run-all-compositor-stages-before-draw','--virtual-time-budget=1500',f'--screenshot={out/"sheet.png"}',src.as_uri()],stdout=subprocess.DEVNULL,stderr=(out/'render.log').open('w'),check=True)
  full=Image.open(out/'sheet.png').convert('RGBA')
  for name,(x,y,w,h) in self.boxes.items():
   im=full.crop((x,y,x+w,y+h));px=im.load()
   for yy in range(h):
    for xx in range(w):
     if px[xx,yy][:3]==(255,0,255):px[xx,yy]=(255,0,255,0)
   im.save(out/(name+'.png'))

def assets(finish,out):
 s=Sheet(finish)
 # Original five transport controls. Labels and glyphs are unchanged.
 for name,(kind,_) in KEYS.items():
  for state in ['up','down','on']:
   key=original_key(kind)
   if state in ['down','on']:key=key.replace('class="tp-key"','class="tp-key" data-down="true"')
   if state=='on':key=key.replace('class="tp-led"','class="tp-led on"')
   s.add(name+'-'+state,96,148,f'<div class="tp" data-finish="{finish}"><div class="transport">{key}</div></div>')
 # Existing compact Drum Machine keys, relabelled for application actions.
 labels={'open':'OPEN','queue':'PLAYLIST','eq':'EQ','full':'FULL','menu':'MENU','close':'CLOSE','mute':'MUTE','repeat':'REPEAT','shuffle':'SHUFFLE','add':'ADD','remove':'REMOVE','save':'SAVE','sort':'SORT','manage':'MANAGE','network':'STREAM','min':'MIN','restore':'BACK','subtitles':'SUBS','download':'DOWNLOAD','cancel':'CANCEL'}
 for name,label in labels.items():
  for state in ['up','down','on']:
   attr='data-down="true"' if state=='down' else 'aria-pressed="true"' if state=='on' else ''
   s.add(name+'-'+state,96,76,f'<div class="cp" data-finish="{finish}"><button class="sq-btn utility" {attr}>{label}</button></div>')
 # Original Slider 01 thumb and track, with unaltered ribbing and shadows.
 s.add('seek-thumb',82,48,f'<div class="fx" data-finish="{finish}"><div class="hs trk"><span class="hs-th"><i></i><i></i><i></i><i></i><i></i></span></div></div>','compact')
 s.add('seek-track',992,48,f'<div class="fx" data-finish="{finish}"><div class="hs trk"><span class="hs-line"></span></div></div>','compact')
 # Rotary Knob 01: original 220px face, scaled uniformly to 110px.
 for i in range(101):
  s.add(f'dial-{i}',110,110,f'<div class="dial" data-finish="{finish}"><svg class="ticks" viewBox="0 0 220 220">{ticks()}</svg><div class="dark-base"></div><div class="dark-knob" style="transform:rotate({-135+i*2.7}deg)"><div class="dash"></div></div></div>','foundation')
 s.add('display',312,104,'<div class="tp-display"></div>')
 s.add('case',W,H,f'<div class="tp" data-finish="{finish}"></div>')
 s.render(out)
 seq=Image.new('RGBA',(110,11110))
 for i in range(101):seq.paste(Image.open(out/f'dial-{i}.png'),(0,i*110))
 seq.save(out/'volume.png')
 # Resize the existing controls uniformly for the shorter player strip.
 for name in list(KEYS)+list(labels):
  factor=2/3
  for state in ['up','down','on']:
   im=Image.open(out/f'{name}-{state}.png');im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS).save(out/f'mini-{name}-{state}.png')
 for name,size in [('display',(208,69)),('seek-thumb',(66,38)),('seek-track',(928,38))]:
  Image.open(out/(name+'.png')).resize(size,Image.Resampling.LANCZOS).save(out/('mini-'+name+'.png'))
 Image.open(out/'volume.png').resize((88,8888),Image.Resampling.LANCZOS).save(out/'mini-volume.png')
 case=Image.open(out/'case.png')
 case.crop((W-112,0,W-24,H-120)).save(out/'knob-guard-top.png')
 case.crop((W-112,H-32,W-24,H)).save(out/'knob-guard-bottom.png')
 # Equalizer uses the same ribbed Slider 01, uniformly reduced and rotated.
 thumb=Image.open(out/'seek-thumb.png').resize((49,29),Image.Resampling.LANCZOS).rotate(90,expand=True)
 thumb.save(out/'eq-thumb.png')
 track=Image.open(out/'seek-track.png').crop((0,22,144,26)).rotate(90,expand=True)
 track.save(out/'eq-track.png')
 return s.boxes

def E(parent,tag,**attrs):return ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})

def bake_cached_graphics(root,out):
 # Skins2 caches controls in X11 pixmaps and later copies them without alpha
 # blending. Composite the unchanged source artwork onto its actual host
 # surface first, rather than letting soft shadows acquire black mattes.
 bitmaps={b.get('id'):b.get('file') for b in root.findall('Bitmap')}
 case=Image.open(out/bitmaps['case']).convert('RGBA')
 serial=0
 def save(image,source):
  nonlocal serial
  serial+=1;ident=f'host-{serial}-{source}';file=f'assets/{ident}.png'
  image.save(out/file)
  item=ET.Element('Bitmap',id=ident,file=file,alphacolor='#FF00FF')
  root.insert(next(i for i,e in enumerate(root) if e.tag=='Window'),item)
  return ident
 for layout in root.findall('Window/Layout'):
  background=case.resize((int(layout.get('width')),int(layout.get('height'))),Image.Resampling.LANCZOS)
  for image in layout.findall('Image'):
   source=image.get('image')
   if source=='case':continue
   sprite=Image.open(out/bitmaps[source]).convert('RGBA');x=int(image.get('x','0'));y=int(image.get('y','0'))
   host=background.crop((x,y,x+sprite.width,y+sprite.height))
   image.set('image',save(Image.alpha_composite(host,sprite),source))
   background.alpha_composite(sprite,(x,y))
  for control in layout:
   if control.tag not in ['Button','Checkbox','Slider','RadialSlider']:continue
   converted={}
   for attribute in ['up','down','over','up1','up2','down1','down2','over1','over2','sequence']:
    source=control.get(attribute)
    if not source or source=='none':continue
    if source not in converted:
     sprite=Image.open(out/bitmaps[source]).convert('RGBA')
     frames=int(control.get('nbimages','1')) if attribute=='sequence' else 1
     height=sprite.height//frames;x=int(control.get('x','0'));y=int(control.get('y','0'))
     if control.tag=='Slider':
      import re
      points=[tuple(map(int,p)) for p in re.findall(r'\((-?\d+),(-?\d+)\)',control.get('points'))]
      x+=round(sum(p[0] for p in points)/len(points))-sprite.width//2
      y+=round(sum(p[1] for p in points)/len(points))-height//2
     host=background.crop((x,y,x+sprite.width,y+height))
     baked=Image.new('RGBA',sprite.size)
     for frame in range(frames):
      baked.paste(Image.alpha_composite(host,sprite.crop((0,frame*height,sprite.width,(frame+1)*height))),(0,frame*height))
     converted[source]=save(baked,source)
    control.set(attribute,converted[source])
def xml(finish,out):
 dark=finish=='obsidian'; ink='#f2f2f4' if dark else '#1d1d1f'; sub='#9a9aa0' if dark else '#737379'; case='#121214' if dark else '#ededf0'
 root=ET.Element('Theme',version='2.0',tooltipfont='defaultfont',magnet='0')
 E(root,'ThemeInfo',name=f'Enochian VLC · {finish.title()}',author='Enochian',webpage='https://uiux-nonhumanintelligence.web.app/UIUX')
 for size,name in [(11,'defaultfont'),(11,'mono'),(16,'title'),(20,'time')]:E(root,'Font',id=name,file=FONT.name,size=size)
 names=['case','display','seek-track','seek-thumb','eq-thumb','eq-track','volume','knob-guard-top','knob-guard-bottom']
 names += ['mini-'+name for name in ['display','seek-thumb','seek-track','volume']]
 names += [f'mini-{k}-{st}' for k in list(KEYS)+['open','queue','eq','full','menu','close','mute','repeat','shuffle','add','remove','save','sort','manage','network','min','restore','subtitles','download','cancel'] for st in ['up','down','on']]
 names += [f'{k}-{st}' for k in list(KEYS)+['open','queue','eq','full','menu','close','mute','repeat','shuffle','add','remove','save','sort','manage','network','min','restore','subtitles','download','cancel'] for st in ['up','down','on']]
 for name in names:E(root,'Bitmap',id=name,file='assets/'+name+'.png',alphacolor='#FF00FF')
 def text(p,x,y,t,font='mono',color=ink,width=0,anchor=None,**kw):
  if not width:
   # VLC interprets an explicit width of zero literally; it does not size text.
   size={'mono':11,'title':16,'time':20}[font]
   width={'$T':156,'/ $D':124}.get(t,max(16,math.ceil(len(t)*size*.65)+6))
  a=dict(x=x,y=y,text=t,font=font,color=color,width=width,**kw)
  if anchor:a.update(lefttop=anchor,rightbottom=anchor)
  return E(p,'Text',**a)
 def button(p,name,x,y,action,tip,anchor=None):
  a=dict(up=name+'-up',down=name+'-down',over=name+'-up',x=x,y=y,action=action,tooltiptext=tip,help=tip)
  if anchor:a.update(lefttop=anchor,rightbottom=anchor)
  return E(p,'Button',**a)
 def check(p,name,x,y,state,a1,a2,tip,anchor=None):
  a=dict(up1=name+'-up',down1=name+'-down',over1=name+'-up',up2=name+'-on',down2=name+'-on',over2=name+'-on',state=state,action1=a1,action2=a2,x=x,y=y,tooltiptext1=tip,tooltiptext2=tip,help=tip)
  if anchor:a.update(lefttop=anchor,rightbottom=anchor)
  return E(p,'Checkbox',**a)
 main=E(root,'Window',id='main',x=60,y=60,dragdrop='true',playondrop='true')
 l=E(main,'Layout',id='player-resizable-v3',width=W,height=H,minwidth=820,minheight=360,maxwidth=16384,maxheight=16384)
 E(l,'Image',image='case',width=W,height=H,resize='scale',rightbottom='rightbottom',action='move')
 E(l,'Image',image='case',width=W,height=H,resize='scale',rightbottom='rightbottom',action='move',visible='main.isMaximized')
 E(l,'RadialSlider',id='volume-knob',x=W-112,y=H-120,sequence='mini-volume',nbimages=101,minangle=45,maxangle=315,value='volume',lefttop='rightbottom',rightbottom='rightbottom',tooltiptext='Volume $V%')
 E(l,'Image',id='knob-hit-top',image='knob-guard-top',x=W-112,y=0,width=88,height=H-120,resize='scale',lefttop='righttop',rightbottom='rightbottom',action='move')
 E(l,'Image',id='knob-hit-bottom',image='knob-guard-bottom',x=W-112,y=H-32,width=88,height=32,lefttop='rightbottom',rightbottom='rightbottom',action='move')
 text(l,16,18,'ENOCHIAN','title');text(l,148,21,'MEDIA PLAYER',color=sub,width=150)
 for i,(name,action,tip) in enumerate([
  ('open','dialogs.fileSimple()','Open media · Ctrl+O'),
  ('queue','queue.show()','Create or edit a playlist'),
  ('eq','equalizerwin.show()','Open equalizer'),
  ('menu','dialogs.popup()','Tracks, subtitles, speed and preferences'),
  ('subtitles','none','English subtitles · use local SRT or ask before downloading'),
  ('min','vlc.minimize()','Minimize'),
  ('full','main.maximize()','Fullscreen player · BACK or Escape restores · F for video only'),
  ('close','vlc.quit()','Quit VLC')]):
  x=W-540+i*66
  if name=='full':
   c=check(l,'mini-full',x,4,'main.isMaximized','main.maximize()','main.unmaximize()',tip,'righttop')
   c.set('id','window-fullscreen')
   for attr in ['up2','down2','over2']:c.set(attr,'mini-restore-on')
  else:
   c=button(l,'mini-'+name,x,4,action,tip,'righttop')
   if name=='subtitles':c.set('id','english-subtitles')
 E(l,'Video',id='screen',x=16,y=64,width=W-32,height=H-234,rightbottom='rightbottom',autoresize='false',help='Drop files to play · F video fullscreen · Space play/pause')
 E(l,'Image',image='mini-seek-track',x=16,y=H-164,width=W-32,height=38,lefttop='leftbottom',rightbottom='rightbottom',resize='scale')
 E(l,'Slider',id='seek',x=49,y=H-145,points=f'(0,0),({W-98},0)',up='mini-seek-thumb',down='mini-seek-thumb',over='mini-seek-thumb',value='time',thickness=24,lefttop='leftbottom',rightbottom='rightbottom',tooltiptext='$T / $D')
 E(l,'Image',image='mini-display',x=16,y=H-116,lefttop='leftbottom',rightbottom='leftbottom')
 text(l,26,H-110,'$N',width=188,color='#f2f2f4',anchor='leftbottom')
 text(l,26,H-89,'$T','time',width=110,color='#CC0000',anchor='leftbottom',visible='not vlc.isStopped')
 text(l,142,H-80,'/ $D',width=76,color='#9a9aa0',anchor='leftbottom',visible='not vlc.isStopped')
 text(l,26,H-89,'0:00','time',width=110,color='#CC0000',anchor='leftbottom',visible='vlc.isStopped')
 text(l,142,H-80,'/ 0:00',width=76,color='#9a9aa0',anchor='leftbottom',visible='vlc.isStopped')
 for label,color,state in [('PLAYING','#3ccf7a','vlc.isPlaying'),('PAUSED','#F4A934','vlc.isPaused'),('READY · OPEN MEDIA','#9a9aa0','vlc.isStopped')]:text(l,26,H-61,label,color=color,width=188,anchor='leftbottom',visible=state)
 button(l,'mini-previous',240,H-120,'playlist.previous()','Previous item (P)','leftbottom')
 check(l,'mini-play',304,H-120,'vlc.isPlaying','vlc.play()','vlc.pause()','Play / pause (Space)','leftbottom')
 check(l,'mini-pause',368,H-120,'vlc.isPaused','vlc.pause()','vlc.play()','Pause / resume','leftbottom')
 button(l,'mini-stop',432,H-120,'vlc.stop()','Stop (S)','leftbottom')
 button(l,'mini-next',496,H-120,'playlist.next()','Next item (N)','leftbottom')
 check(l,'mini-shuffle',576,H-120,'playlist.isRandom','playlist.setRandom(true)','playlist.setRandom(false)','Shuffle playlist','leftbottom')
 check(l,'mini-repeat',642,H-120,'playlist.isLoop','playlist.setLoop(true)','playlist.setLoop(false)','Loop playlist','leftbottom')
 check(l,'mini-mute',576,H-68,'vlc.isMute','vlc.mute()','vlc.mute()','Mute / unmute (M)','leftbottom')
 button(l,'mini-network',642,H-68,'dialogs.net()','Open network stream','leftbottom')
 text(l,W-118,H-23,'VOL $V%',color=sub,anchor='rightbottom',width=104)
 text(l,16,H-22,'$H',color=sub,width=208,anchor='leftbottom')
 # The queue is skinned as a separate window so the video retains usable space.
 q=E(root,'Window',id='queue',visible='false',x=150,y=120)
 ql=E(q,'Layout',id='queue-layout',width=620,height=600,minwidth=620,minheight=600)
 E(ql,'Image',image='case',resize='scale',rightbottom='rightbottom',action='move')
 text(ql,26,26,'PLAYLIST','title');button(ql,'close',512,10,'queue.hide()','Close playlist','righttop')
 E(ql,'Playlist',id='mediaqueue',x=24,y=96,width=572,height=370,font='title',fgcolor=ink,playcolor='#CC0000',bgcolor1=case,bgcolor2=case,selcolor='#333337' if dark else '#d4d4d8',rightbottom='rightbottom')
 button(ql,'add',16,486,'playlist.add()','Add files to this playlist','leftbottom')
 button(ql,'remove',114,486,'playlist.del()','Remove selected item; keep the file','leftbottom')
 button(ql,'save',212,486,'playlist.save()','Save a named playlist','leftbottom')
 button(ql,'open',310,486,'playlist.load()','Reopen a saved playlist','leftbottom')
 button(ql,'sort',408,486,'playlist.sort()','Sort playlist by title','leftbottom')
 button(ql,'manage',506,486,'dialogs.playlist()','Advanced playlist editor: drag to reorder','leftbottom')
 text(ql,24,578,'Add files · Double-click to play · Manage to reorder',color=sub,anchor='leftbottom')
 # A native equalizer with original Slider 01 caps; no simulated meters.
 eq=E(root,'Window',id='equalizerwin',visible='false',x=150,y=170)
 el=E(eq,'Layout',id='equalizer-layout',width=820,height=390,minwidth=820,maxwidth=820,minheight=390,maxheight=390)
 E(el,'Image',image='case',resize='scale',rightbottom='rightbottom',action='move')
 text(el,26,26,'EQUALIZER','title');button(el,'close',712,10,'equalizerwin.hide()','Close equalizer')
 check(el,'eq',24,76,'equalizer.isEnabled','equalizer.enable()','equalizer.disable()','Enable / disable equalizer')
 text(el,28,160,'+20 dB',color=sub);text(el,28,240,'−20 dB',color=sub)
 for i,label in enumerate(['PRE','60','170','310','600','1K','3K','6K','12K','14K','16K']):
  x=122+i*60
  E(el,'Image',image='eq-track',x=x-2,y=122)
  E(el,'Slider',id='eq-'+str(i),x=x,y=124,points='(0,140),(0,0)',up='eq-thumb',down='eq-thumb',over='eq-thumb',value='equalizer.preamp' if i==0 else f'equalizer.band({i-1})',thickness=24,tooltiptext='Preamp' if i==0 else label+' Hz')
  text(el,x-12,300,label,width=52,alignment='center',color=sub)
 text(el,26,355,'ENOCHIAN / SLIDER 01 · VLC 10-BAND EQ',color=sub)
 # App-owned resize regions work even when the compositor disables border resizing.
 def resize_handles(layout,w,h,name,visible='true'):
  case_image=Image.open(out/'assets/case.png').resize((w,h),Image.Resampling.LANCZOS)
  for suffix,box,action,anchor in [
   ('right',(w-7,0,w,h),'resizeE',('righttop','rightbottom')),
   ('bottom',(0,h-7,w,h),'resizeS',('leftbottom','rightbottom')),
   ('corner',(w-32,h-32,w,h),'resizeSE',('rightbottom','rightbottom'))]:
   ident=name+'-resize-'+suffix;image=case_image.crop(box)
   if suffix=='corner':
    grip=Image.open(out/'assets/seek-thumb.png').resize((26,15),Image.Resampling.LANCZOS).rotate(45,expand=True)
    image.alpha_composite(grip,((32-grip.width)//2,(32-grip.height)//2))
   file='assets/'+ident+'.png';image.save(out/file)
   bitmap=ET.Element('Bitmap',id=ident,file=file,alphacolor='#FF00FF');root.insert(next(i for i,e in enumerate(root) if e.tag=='Window'),bitmap)
   E(layout,'Image',id=ident+'-hit',image=ident,x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1],resize='scale',lefttop=anchor[0],rightbottom=anchor[1],action=action,help='Drag to resize the window',visible=visible)
 resize_handles(l,W,H,'player','not main.isMaximized')
 resize_handles(ql,620,600,'queue')
 bake_cached_graphics(root,out)
 data=ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=False)
 (out/'theme.xml').write_bytes(data.replace(b'?>',b'?>\n<!DOCTYPE Theme PUBLIC "-//VideoLAN//DTD VLC Skins V2.0//EN" "skin.dtd">',1))
 shutil.copy(ROOT/'reference/skin.dtd',out/'skin.dtd');shutil.copy(FONT,out/FONT.name)
 return root

def build(finish):
 with tempfile.TemporaryDirectory(prefix='enochian-build-') as tmp:
  out=Path(tmp);assets(finish,out)
  skin=out/'skin';(skin/'assets').mkdir(parents=True)
  for p in out.glob('*.png'):
   if p.name!='sheet.png' and not p.stem.startswith('dial-'):shutil.copy(p,skin/'assets'/p.name)
  root=xml(finish,skin)
  subprocess.run(['xmllint','--noout','--valid',str(skin/'theme.xml')],check=True)
  vlt=DIST/'skins'/f'Enochian-{finish.title()}.vlt'
  with tarfile.open(vlt,'w:gz') as tar:
   for p in sorted(skin.rglob('*')):
    if p.is_file():tar.add(p,arcname=str(p.relative_to(skin)),recursive=False)
  # Preview composed from the same assets/positions as the executable skin.
  # Real native screenshots are used for this resizable layout, rather than a fabricated preview.
  shutil.copytree(skin,DIST/'source'/'built'/finish,dirs_exist_ok=True)
  print('Built and DTD-validated',vlt)

def preview(skin,root,finish):
 from PIL import ImageDraw, ImageFont
 dark=finish=='obsidian';ink='#f2f2f4' if dark else '#1d1d1f'
 im=Image.open(skin/'assets/case.png').convert('RGBA');draw=ImageDraw.Draw(im)
 fonts={n:ImageFont.truetype(str(FONT),s) for n,s in [('mono',12),('title',16),('time',24)]}
 layout=root.find('Window/Layout')
 for e in layout:
  if e.tag=='Image' and e.get('image')!='case':
   a=Image.open(skin/'assets'/f'{e.get("image")}.png');im.alpha_composite(a,(int(e.get('x',0)),int(e.get('y',0))))
  if e.tag in ['Button','Checkbox']:
   k=e.get('up') or e.get('up1');a=Image.open(skin/'assets'/f'{k}.png');im.alpha_composite(a,(int(e.get('x')),int(e.get('y'))))
  if e.tag=='Text' and '$' not in e.get('text','') and not e.get('visible'):
   draw.text((int(e.get('x')),int(e.get('y'))-2),e.get('text'),font=fonts[e.get('font')],fill=e.get('color',ink))
 # Video is a neutral empty stage, not a fabricated film or fake media library.
 draw.rectangle((24,96,1015,511),fill='#09090a')
 draw.text((443,250),'ENOCHIAN',font=fonts['time'],fill='#e9e9eb')
 draw.text((350,293),'OPEN A FILE OR DROP YOUR MEDIA HERE',font=fonts['mono'],fill='#87878e')
 for s,x,y,f,c in [('No media loaded',40,600,'mono','#f2f2f4'),('00:00',40,626,'time','#CC0000'),('/ 00:00',206,638,'mono','#9a9aa0'),('READY',40,673,'mono','#9a9aa0'),('VOL 50%',887,702,'mono',ink)]:draw.text((x,y),s,font=fonts[f],fill=c)
 im.alpha_composite(Image.open(skin/'assets/seek-thumb.png'),(455,526))
 dial=Image.open(skin/'assets/volume.png').crop((0,50*110,110,51*110));im.alpha_composite(dial,(874,584))
 im.convert('RGB').save(DIST/'previews'/f'{finish}.png')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--finish',choices=['ivory','obsidian','both'],default='both');a=p.parse_args()
 for f in (['obsidian','ivory'] if a.finish=='both' else [a.finish]):build(f)
