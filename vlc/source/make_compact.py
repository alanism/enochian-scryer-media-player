#!/usr/bin/env python3
"""Uniformly scale the original skin to 80% for smaller Omarchy tiles."""
from pathlib import Path
import re,tarfile,tempfile,subprocess,xml.etree.ElementTree as ET
from PIL import Image
root=Path(__file__).resolve().parent.parent
for finish in ['Obsidian','Ivory']:
 with tempfile.TemporaryDirectory() as tmp:
  base=Path(tmp)
  with tarfile.open(root/'skins'/f'Enochian-{finish}.vlt') as t:t.extractall(base,filter='data')
  doc=ET.parse(base/'theme.xml')
  for e in doc.iter():
   for k in ['x','y','width','height','minwidth','maxwidth','minheight','maxheight','size','thickness']:
    if k in e.attrib and int(e.get(k))>=0:e.set(k,str(round(int(e.get(k))*.8)))
   if e.get('points'):e.set('points',re.sub(r'-?\d+',lambda m:str(round(int(m[0])*.8)),e.get('points')))
  for p in (base/'assets').glob('*.png'):
   im=Image.open(p);im.resize((round(im.width*.8),round(im.height*.8)),Image.Resampling.LANCZOS).save(p)
  data=ET.tostring(doc.getroot(),encoding='utf-8',xml_declaration=True)
  data=data.replace(b'?>',b'?>\n<!DOCTYPE Theme PUBLIC "-//VideoLAN//DTD VLC Skins V2.0//EN" "skin.dtd">',1)
  (base/'theme.xml').write_bytes(data)
  subprocess.run(['xmllint','--noout','--valid',str(base/'theme.xml')],check=True)
  with tarfile.open(root/'skins'/f'Enochian-{finish}-Compact.vlt','w:gz') as t:
   for p in sorted(base.rglob('*')):
    if p.is_file():t.add(p,arcname=str(p.relative_to(base)),recursive=False)
  print('Built',finish,'Compact:',doc.getroot().find('Window/Layout').get('width'),'×',doc.getroot().find('Window/Layout').get('height'))
