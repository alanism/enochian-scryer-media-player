"""Installer regression: replace a running Linux executable without truncating it."""
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(shutil.which('sleep'), 'Requires a local sleep executable')
class InstallerTests(unittest.TestCase):
    def test_reinstall_preserves_running_engine_and_quotes_desktop_fields(self):
        source = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / 'bundle'
            (bundle / 'bin').mkdir(parents=True)
            (bundle / 'web').mkdir()
            for name in ['install.sh', 'companion.py', 'icon.png', 'ENGINE-LICENSE.txt']:
                shutil.copy2(source / name, bundle / name)
            shutil.copy2(shutil.which('sleep'), bundle / 'bin/rqbit')
            (bundle / 'web/index.html').write_text('<head></head>')
            data = root / 'data with %percent'
            installed = data / 'enochian-rqbit/bin'
            installed.mkdir(parents=True)
            shutil.copy2(bundle / 'bin/rqbit', installed / 'rqbit')
            process = subprocess.Popen([str(installed / 'rqbit'), '30'])
            try:
                env = {**os.environ, 'XDG_DATA_HOME': str(data), 'ENOCHIAN_RQBIT_PORT': '19492', 'ENOCHIAN_RQBIT_ENGINE_PORT': '19493'}
                result = subprocess.run(['bash', str(bundle / 'install.sh')], env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsNone(process.poll())
                self.assertEqual(hashlib.sha256((installed / 'rqbit').read_bytes()).digest(), hashlib.sha256((bundle / 'bin/rqbit').read_bytes()).digest())
                desktop = data / 'applications/enochian-rqbit.desktop'
                self.assertIn('%%percent', desktop.read_text())
                if shutil.which('desktop-file-validate'):
                    subprocess.run(['desktop-file-validate', str(desktop)], check=True, capture_output=True)
            finally:
                process.terminate()
                process.wait(timeout=5)
