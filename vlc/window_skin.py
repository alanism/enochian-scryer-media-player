#!/usr/bin/env python3
"""Fit the initial player to one quarter of the active screen, retaining anchors.
Only bundled artwork and XML are copied. No desktop configuration is modified.
"""
from __future__ import annotations
import argparse,ctypes,hashlib,io,json,os,re,subprocess,tarfile,tempfile
from pathlib import Path
import xml.etree.ElementTree as ET


def workarea():
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        try:
            monitors=json.loads(subprocess.check_output(['hyprctl','-j','monitors'],timeout=2,stderr=subprocess.DEVNULL))
            m=next((m for m in monitors if m.get('focused')),monitors[0]);scale=float(m.get('scale',1));r=m.get('reserved',[0,0,0,0])
            width,height=float(m['width'])/scale,float(m['height'])/scale
            if m.get('transform',0)%2:width,height=height,width
            return (int(m['x']+r[0]),int(m['y']+r[1]),int(width-r[0]-r[2]),int(height-r[1]-r[3]))
        except (OSError,ValueError,KeyError,IndexError,subprocess.SubprocessError):pass
    try:
        x=ctypes.CDLL('libX11.so.6');x.XOpenDisplay.argtypes=[ctypes.c_char_p];x.XOpenDisplay.restype=ctypes.c_void_p
        x.XDefaultScreen.argtypes=[ctypes.c_void_p];x.XDisplayWidth.argtypes=[ctypes.c_void_p,ctypes.c_int];x.XDisplayHeight.argtypes=[ctypes.c_void_p,ctypes.c_int];x.XCloseDisplay.argtypes=[ctypes.c_void_p]
        display=x.XOpenDisplay(None)
        if display:
            try:
                screen=x.XDefaultScreen(display);return (0,0,x.XDisplayWidth(display,screen),x.XDisplayHeight(display,screen))
            finally:x.XCloseDisplay(display)
    except OSError:pass
    return (0,0,1920,1080)


def fit_main(root,width,height,x,y):
    window=root.find("Window[@id='main']");layout=window.find('Layout')
    width=max(int(layout.get('minwidth')),width);height=max(int(layout.get('minheight')),height)
    dx=width-int(layout.get('width'));dy=height-int(layout.get('height'))
    for e in layout:
        lt=e.get('lefttop','lefttop');rb=e.get('rightbottom','lefttop')
        if lt.startswith('right'):e.set('x',str(int(e.get('x','0'))+dx))
        if lt.endswith('bottom'):e.set('y',str(int(e.get('y','0'))+dy))
        if e.tag=='Slider' and e.get('id')=='seek':
            points=re.findall(r'\((-?\d+),(-?\d+)\)',e.get('points',''))
            if len(points)==2:e.set('points',f'({points[0][0]},{points[0][1]}),({int(points[1][0])+dx},{points[1][1]})')
        if e.get('width') and lt.startswith('left') and rb.startswith('right'):e.set('width',str(int(e.get('width'))+dx))
        if e.get('height') and lt.endswith('top') and rb.endswith('bottom'):e.set('height',str(int(e.get('height'))+dy))
    layout.set('width',str(width));layout.set('height',str(height));window.set('x',str(x));window.set('y',str(y))
    return width,height


def prepare(skins,finish,size,cache,area=None):
    area=workarea() if area is None else area;left,top,screen_w,screen_h=area
    if screen_w<=0 or screen_h<=0:raise ValueError('Invalid screen dimensions')
    width,height=screen_w//2,screen_h//2
    standard=skins/f'Enochian-{finish.title()}.vlt'
    with tarfile.open(standard) as archive:root=ET.fromstring(archive.extractfile('theme.xml').read())
    layout=root.find("Window[@id='main']/Layout")
    compact=size=='compact' or (size=='auto' and (width<int(layout.get('minwidth')) or height<int(layout.get('minheight'))))
    source=standard.with_name(standard.stem+'-Compact.vlt') if compact else standard
    with tarfile.open(source) as archive:
        root=ET.fromstring(archive.extractfile('theme.xml').read());layout=root.find("Window[@id='main']/Layout")
        width=max(width,int(layout.get('minwidth')));height=max(height,int(layout.get('minheight')))
        x=left+max(0,(screen_w-width)//2);y=top+max(0,(screen_h-height)//2)
        fit_main(root,width,height,x,y)
        key=hashlib.sha256(source.read_bytes()+str((width,height,x,y)).encode()).hexdigest()[:24]
        folder=cache/key;folder.mkdir(parents=True,exist_ok=True);target=folder/source.name
        if target.is_file():return target
        data=ET.tostring(root,encoding='utf-8',xml_declaration=True,short_empty_elements=False)
        data=data.replace(b'?>',b'?>\n<!DOCTYPE Theme PUBLIC "-//VideoLAN//DTD VLC Skins V2.0//EN" "skin.dtd">',1)
        with tempfile.NamedTemporaryFile(dir=folder,suffix='.vlt',delete=False) as file:temp=Path(file.name)
        try:
            with tarfile.open(temp,'w:gz') as output:
                for item in archive:
                    if not item.isfile():continue
                    payload=data if item.name=='theme.xml' else archive.extractfile(item).read()
                    info=tarfile.TarInfo(item.name);info.mode=item.mode;info.size=len(payload);output.addfile(info,io.BytesIO(payload))
            temp.replace(target)
        finally:temp.unlink(missing_ok=True)
    return target


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('skins',type=Path);p.add_argument('--finish',choices=['ivory','obsidian'],required=True);p.add_argument('--size',choices=['auto','standard','compact'],default='auto');a=p.parse_args()
    cache=Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))/'enochian-vlc/skins'
    print(prepare(a.skins,a.finish,a.size,cache))
if __name__=='__main__':main()
