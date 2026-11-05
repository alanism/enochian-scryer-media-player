import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[2]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
window=module('window_skin','vlc/window_skin.py');subs=module('subtitles','vlc/subtitles.py')
class PlayerWindows(unittest.TestCase):
 def test_quarter_workarea_accounts_for_bar_and_scale(self):
  value=[{'focused':True,'x':0,'y':0,'width':3840,'height':2160,'scale':2,'reserved':[0,30,0,0]}]
  with patch.dict(window.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(window.subprocess,'check_output',return_value=json.dumps(value).encode()):self.assertEqual(window.workarea(),(0,30,1920,1050))
 def test_adaptive_theme_uses_quarter_and_compact_when_needed(self):
  with tempfile.TemporaryDirectory() as d:
   for finish in ['ivory','obsidian']:
    path=window.prepare(ROOT/'vlc/skins',finish,'auto',Path(d),(0,30,1920,1050))
    with window.tarfile.open(path) as t:root=window.ET.fromstring(t.extractfile('theme.xml').read())
    main=root.find("Window[@id='main']/Layout");self.assertEqual((main.get('width'),main.get('height')),('960','525'))
    small=window.prepare(ROOT/'vlc/skins',finish,'auto',Path(d),(0,0,1366,768));self.assertTrue(small.name.endswith('-Compact.vlt'))
    with window.tarfile.open(small) as t:small_root=window.ET.fromstring(t.extractfile('theme.xml').read())
    small_layout=small_root.find("Window[@id='main']/Layout");seek=small_layout.find("Slider[@id='seek']")
    # The curve must track the fitted layout, rather than keep its source width.
    with window.tarfile.open(ROOT/'vlc/skins'/small.name) as t:source=window.ET.fromstring(t.extractfile('theme.xml').read()).find("Window[@id='main']/Layout")
    original=int(window.re.findall(r'\((-?\d+),(-?\d+)\)',source.find("Slider[@id='seek']").get('points'))[-1][0]);fitted=int(window.re.findall(r'\((-?\d+),(-?\d+)\)',seek.get('points'))[-1][0])
    self.assertEqual(fitted-original,int(small_layout.get('width'))-int(source.get('width')))
 def test_local_english_srt_priority(self):
  with tempfile.TemporaryDirectory() as d:
   video=Path(d)/'Movie.mp4';video.touch();plain=video.with_suffix('.srt');plain.write_text('plain');(Path(d)/'Movie.fr.srt').write_text('French')
   self.assertEqual(subs.english_sidecar(video),plain)
   english=Path(d)/'Movie.EN.srt';english.write_text('English');self.assertEqual(subs.english_sidecar(video),english)
 def test_sparse_proxy_preserves_original_hash_material(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a.mp4';b=Path(d)/'b.mp4';a.write_bytes(bytes(range(256))*4096);subs.hash_proxy(a,b)
   self.assertEqual(a.stat().st_size,b.stat().st_size)
   self.assertEqual(a.read_bytes()[:65536],b.read_bytes()[:65536]);self.assertEqual(a.read_bytes()[-65536:],b.read_bytes()[-65536:]);self.assertEqual(b.read_bytes()[65536:131072],bytes(65536))
 def test_subtitles_never_apply_to_a_changed_video(self):
  player=subs.Player({'password':'test','port':1});player.request=Mock(return_value={'uri':'file:///different.mp4'})
  with self.assertRaisesRegex(ValueError,'video changed'):player.apply(Path('/tmp/test.srt'),'file:///first.mp4')
  player.request.assert_called_once_with()
 def test_embedded_english_track_selection(self):
  self.assertEqual(subs.english_track({'subtitle_ids':[-1,3,4],'subtitle_names':['Disable','Track 1 [English]','French']}),3)
