import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


class VlcLauncherTests(unittest.TestCase):
    def test_finish_and_size_flags_work_in_either_order(self):
        launcher = Path(__file__).resolve().parents[2] / 'vlc/enochian-vlc'
        if not launcher.is_file(): self.skipTest('Run from the media suite checkout')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stub = root / 'vlc'
            stub.write_text('#!/usr/bin/python3\nimport json,os,sys\nif "--list" in sys.argv: print("  skins2 custom interface")\nelse: open(os.environ["VLC_TEST_ARGS"],"w").write(json.dumps(sys.argv[1:]))\n')
            stub.chmod(0o755)
            capture = root / 'args.json'
            env = {**os.environ, 'PATH': str(root) + ':' + os.environ['PATH'], 'DISPLAY': ':test', 'XDG_CONFIG_HOME': str(root / 'config'), 'VLC_TEST_ARGS': str(capture)}
            for flags in [['--ivory', '--compact'], ['--compact', '--ivory']]:
                with self.subTest(flags=flags):
                    subprocess.run(['bash', str(launcher), *flags, '/tmp/example movie.mp4'], env=env, check=True, capture_output=True)
                    args = json.loads(capture.read_text())
                    self.assertTrue(any(a.endswith('Enochian-Ivory-Compact.vlt') for a in args))
                    self.assertEqual(args[-1], '/tmp/example movie.mp4')
                    self.assertNotIn('--compact', args)
            self.assertIn('--equalizer-bands=0 0 0 0 0 0 0 0 0 0', args)
            profile = root / 'config/enochian-vlc/vlcrc'
            saved = '[equalizer]\nequalizer-bands=  3.0 0 0 0 0 0 0 0 0 -2.0\n'
            profile.write_text(saved)
            subprocess.run(['bash', str(launcher), '/tmp/example movie.mp4'], env=env, check=True, capture_output=True)
            warm_args = json.loads(capture.read_text())
            self.assertFalse(any(a.startswith('--equalizer-bands=') for a in warm_args))
            self.assertEqual(profile.read_text(), saved)
            subprocess.run(['bash', str(launcher), '--ivory', '--', '--compact'], env=env, check=True, capture_output=True)
            args = json.loads(capture.read_text())
            self.assertTrue(any(a.endswith('Enochian-Ivory.vlt') for a in args))
            self.assertEqual(args[-2:], ['--', '--compact'])
