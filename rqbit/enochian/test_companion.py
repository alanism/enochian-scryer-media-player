"""Desktop handoff tests: run with python3 -m unittest discover -s enochian."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import companion


class DesktopHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.downloads = self.root / 'downloads'
        self.downloads.mkdir()
        self.media = self.downloads / 'Example video.mp4'
        self.media.write_bytes(b'test media')
        self.vlc = self.root / 'enochian-vlc'
        self.vlc.touch()
        self.details = {'output_folder': str(self.downloads), 'files': [
            {'name': self.media.name, 'components': [self.media.name],
             'included': True, 'attributes': {}}
        ]}
        self.stats = {'state': 'paused', 'finished': True, 'error': None}
        self.handler = object.__new__(companion.Handler)
        self.handler.reply = Mock()
        self.engine = self.start_patch('engine_json', side_effect=self.engine_json)
        self.popen = self.start_patch('subprocess.Popen')
        self.run = self.start_patch('subprocess.run')
        self.start_patch('VLC', self.vlc)

    def start_patch(self, name, *args, **kwargs):
        patcher = patch('companion.' + name, *args, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def engine_json(self, path):
        if path == '/torrents/7': return self.details
        if path == '/torrents/7/stats/v1': return self.stats
        raise AssertionError('Unexpected engine request: ' + path)

    def test_completed_card_opens_local_file_in_matching_vlc(self):
        self.handler.play({'torrent_id': 7, 'completed_only': True, 'finish': 'ivory'})
        self.assertEqual(self.popen.call_args.args[0], [str(self.vlc), '--ivory', str(self.media)])
        self.handler.reply.assert_called_once_with(200, {'opened': True, 'torrent_id': 7, 'file_id': 0})
        self.assertEqual(self.stats['state'], 'paused')

    def test_incomplete_card_does_not_launch_vlc(self):
        self.stats['finished'] = False
        with self.assertRaisesRegex(ValueError, 'finish downloading'):
            self.handler.play({'torrent_id': 7, 'completed_only': True})
        self.popen.assert_not_called()

    def test_error_state_does_not_launch_completed_card(self):
        self.stats['error'] = 'Disk unavailable'
        with self.assertRaises(ValueError):
            self.handler.play({'torrent_id': 7, 'completed_only': True})
        self.popen.assert_not_called()

    def test_explicit_play_keeps_streaming_behavior(self):
        self.stats.update(state='live', finished=False)
        self.handler.play({'torrent_id': 7})
        self.assertEqual(self.popen.call_args.args[0], [str(self.vlc), '--obsidian', companion.ORIGIN + '/torrents/7/stream/0'])

    def test_show_file_reveals_media_with_file_manager(self):
        readme = self.downloads / 'README.txt'
        readme.touch()
        self.details['files'].insert(0, {'name': readme.name, 'components': [readme.name], 'included': True})
        self.handler.show_file({'torrent_id': 7})
        args = self.run.call_args.args[0]
        self.assertIn('org.freedesktop.FileManager1.ShowItems', args)
        self.assertIn('array:string:' + self.media.as_uri(), args)
        self.popen.assert_not_called()
        self.handler.reply.assert_called_once_with(200, {'shown': True, 'torrent_id': 7})

    def test_show_file_fallback_opens_folder_not_file(self):
        self.run.side_effect = subprocess.CalledProcessError(1, 'dbus-send')
        self.handler.show_file({'torrent_id': 7})
        self.assertEqual(self.popen.call_args.args[0], ['xdg-open', str(self.downloads)])

    def test_show_file_missing_data_returns_useful_error(self):
        self.media.unlink()
        with self.assertRaisesRegex(ValueError, 'No downloaded files'):
            self.handler.show_file({'torrent_id': 7})
        self.run.assert_not_called()
        self.popen.assert_not_called()

    def test_local_paths_cannot_escape_download_folder(self):
        outside = self.root / 'outside.mp4'
        outside.touch()
        for components in [['..', outside.name], ['/tmp/outside.mp4'], ['sub/../../outside.mp4']]:
            with self.subTest(components=components):
                with self.assertRaises(ValueError):
                    companion.downloaded_file(self.details, {'components': components})
        link = self.downloads / 'link.mp4'
        link.symlink_to(outside)
        with self.assertRaises(ValueError):
            companion.downloaded_file(self.details, {'components': [link.name]})

    def test_excluded_padding_and_symlink_files_are_not_chosen(self):
        self.details['files'][0]['included'] = False
        self.details['files'] += [
            {'name': 'padding.mp4', 'included': True, 'attributes': {'padding': True}},
            {'name': 'link.mp4', 'included': True, 'attributes': {'symlink': True}},
        ]
        with self.assertRaises(ValueError):
            self.handler.play({'torrent_id': 7, 'completed_only': True})
        with self.assertRaises(ValueError):
            self.handler.show_file({'torrent_id': 7})
        self.popen.assert_not_called()
        self.run.assert_not_called()

    def test_invalid_identifiers_and_completed_flags_are_rejected(self):
        for tid in [True, -1, '7', None]:
            with self.subTest(tid=tid):
                with self.assertRaises(ValueError):
                    self.handler.show_file({'torrent_id': tid})
        with self.assertRaises(ValueError):
            self.handler.play({'torrent_id': 7, 'completed_only': 'true'})
        self.engine.assert_not_called()


if __name__ == '__main__':
    unittest.main()
