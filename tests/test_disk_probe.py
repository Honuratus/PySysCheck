import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.probes.disk import DiskProbe


class TestDiskProbe(unittest.TestCase):

    @patch('src.probes.disk.read_file')
    @patch('os.listdir')
    @patch('os.path.exists', return_value=True) 
    def test_disk_probe_success(self, mock_exists, mock_listdir, mock_read_file):
        mock_listdir.return_value = ['sda', 'sr0', 'ram0', 'loop0']

        mock_file_content = {
            '/sys/block/sda/device/model': 'Samsung SSD 860 EVO 500GB\n', 
            
            
            '/sys/block/sda/queue/rotational': '0\n', 
            
            
            '/sys/block/sda/size': '976773168\n' 
        }

        def side_effect(path):
            if path in mock_file_content:
                return mock_file_content[path]
            
        mock_read_file.side_effect = side_effect

        probe = DiskProbe()
        result = probe.run_probe()

        # check unwanted disk types is not in dict data
        self.assertNotIn('sr0', result)
        self.assertNotIn('loop0', result)
        self.assertNotIn('ram0', result)

        # check wanted disk type is in dict data
        self.assertIn('sda', result)

        # check dict data
        self.assertEqual('Samsung SSD 860 EVO 500GB', result['sda']['model'])
        self.assertEqual('SSD', result['sda']['type'])
        self.assertEqual('465.76 GB', result['sda']['size'])

    @patch('src.probes.disk.read_file')
    @patch('os.listdir')
    @patch('os.path.exists', return_value=True)
    def test_disk_type_hdd(self, mock_exists, mock_listdir, mock_read_file):
        mock_listdir.return_value = ['sda']

        mock_file_content = {
            '/sys/block/sda/queue/rotational': '1\n', 
        }

        def side_effect(path):
            if path in mock_file_content:
                return mock_file_content[path]
            
        probe = DiskProbe()
        result = probe.run_probe()

        self.assertIn('sda', result)
        self.assertEqual('HDD', result['sda']['type'])

    @patch('src.probes.disk.read_file')
    @patch('os.listdir')
    @patch('os.path.exists', return_value=True)
    def test_disk_probe_io_error(self, mock_exists, mock_listdir, mock_read_file):
        mock_listdir.return_value = ['sda']

        mock_file_content = {
        
        }

        def side_effect(path):
            if path in mock_file_content:
                return mock_file_content[path]
            
        mock_read_file.side_effect = side_effect

        probe = DiskProbe()
        result = probe.run_probe()


        self.assertIn('sda', result)
        self.assertEqual('Unknown', result['sda']['size'])
        self.assertEqual('Unknown', result['sda']['model'])
        self.assertEqual('Unknown', result['sda']['type'])

    @patch('src.probes.disk.read_file')
    @patch('os.listdir')
    @patch('os.path.exists', return_value=True)
    def test_disk_probe_no_disk_found(self, mock_exists, mock_listdir, mock_read_file):
        mock_listdir.return_value = []


        mock_file_content = {
        
        }

        def side_effect(path):
            if path in mock_file_content:
                return mock_file_content[path]
            

        mock_read_file.side_effect = side_effect

        probe = DiskProbe()
        result = probe.run_probe()

        self.assertEqual(0, len(result))