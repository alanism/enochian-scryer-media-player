#!/usr/bin/env python3
"""Check packaged assets, XML contracts and all rendered control dimensions."""
from pathlib import Path
import tarfile,tempfile,subprocess,xml.etree.ElementTree as ET
from PIL import Image
root=Path(__file__).resolve().parent.parent
for skin in sorted((root/'skins').glob('*.vlt')):
 with tempfile.TemporaryDirectory() as temp:
  with tarfile.open(skin) as t:t.extractall(temp,filter='data')
  base=Path(temp);subprocess.run(['xmllint','--noout','--valid',str(base/'theme.xml')],check=True)
  tree=ET.parse(base/'theme.xml');ids={}
  raw=(base/'theme.xml').read_text()
  assert '</Playlist>' in raw, 'VLC needs an explicit Playlist close before later slider bindings'
  layout=tree.getroot().find('Window/Layout');children=list(layout)
  knob=next(e for e in children if e.get('id')=='volume-knob')
  for guard_id in ['knob-hit-top','knob-hit-bottom']:
   guard=next(e for e in children if e.get('id')==guard_id)
   assert children.index(knob)<children.index(guard), 'Radial input guards must be above the knob'
  full=next(e for e in children if e.get('action')=='vlc.fullscreen()')
  assert children.index(guard)<children.index(full), 'Utility keys must remain above radial guards'
  for elem in tree.iter():
   if elem.tag=='Text':assert int(elem.get('width','0'))>0,'Text must have visible, nonzero width'
   ident=elem.get('id')
   if ident:
    assert ident not in ids, f'Duplicate id: {ident}'
    ids[ident]=elem
   file=elem.get('file')
   if file:assert (base/file).is_file(),f'Missing file: {file}'
  for elem in tree.iter():
   for key in ['up','down','over','up1','up2','down1','down2','over1','over2','sequence','image','font','tooltipfont']:
    val=elem.get(key)
    if val and val!='none':assert val in ids,f'Unknown {key}: {val}'
   if elem.tag=='RadialSlider':
    im=Image.open(base/ids[elem.get('sequence')].get('file'))
    assert im.height==im.width*int(elem.get('nbimages'))
    assert float(elem.get('minangle'))==45 and float(elem.get('maxangle'))==315, 'Dial must match VLC\'s bottom-origin polar convention'
   if elem.tag in ['Font','Bitmap']:
    assert (base/elem.get('file')).stat().st_size>0
  for p in (base/'assets').glob('*.png'):
   im=Image.open(p);im.verify()
  print('PASS',skin.name,len(ids),'unique objects; assets, dial sequence, and DTD valid')
