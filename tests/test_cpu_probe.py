import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.probes.cpu import CpuProbe


class TestCpuProbe(unittest.TestCase):

    # CPU TESTSs
    @patch('src.probes.cpu.read_file')
    def test_cpu_probe_success(self, mock_read_file):
        """
        tests if CPU probe correctly parses standard /proc/cpuinfo content
        """

        # mock data
        mock_read_file.return_value = """
        processor	: 0
        vendor_id	: AuthenticAMD
        cpu family	: 25
        model		: 80
        model name	: AMD Ryzen 5 5600H
        siblings	: 12
        cpu cores	: 6
        cache size	: 512 KB
        flags		: fpu vme svm
        """

        probe = CpuProbe()
        result = probe.run_probe()

        # Validating
        self.assertEqual(result['vendor'], 'AuthenticAMD')
        self.assertEqual(result['model_name'], 'AMD Ryzen 5 5600H')
        self.assertEqual(result['topology']['physical_cores'], 6)
        self.assertEqual(result['topology']['logical_threads'], 12)
        self.assertTrue(result['virtualization_support']) 
    
    @patch('src.probes.cpu.read_file')
    def test_cpu_probe_file_not_found(self,mock_read_file):
        """
        tests error handling when cpuinfo is missing
        """
        mock_read_file.side_effect = FileNotFoundError

        probe = CpuProbe()
        result = probe.run_probe()

        self.assertIn('error', result)
        self.assertIn('/proc/cpuinfo not found', result['error'])

    @patch('src.probes.cpu.read_file')
    def test_cpu_probe_missing_info(self, mock_read_file):
        """
        tests if CPU probe correctly parses missing /proc/cpuinfo content
        """
        # mock data
        mock_read_file.return_value = """
        processor       : 0
        cpu cores       : 4
        siblings        : 8
        cache size      : 8192 KB

        processor       : 1
        cpu cores       : 4
        siblings        : 8
        """

        probe = CpuProbe()
        result = probe.run_probe()

        self.assertEqual(result['vendor'], 'Unknown')
        self.assertEqual(result['model_name'], 'Unknown')
        self.assertEqual(result['topology']['physical_cores'], 4)
        self.assertEqual(result['topology']['logical_threads'], 8)
        self.assertEqual(result['cache'], "8192 KB")
        self.assertFalse(result['virtualization_support']) 
        
    @patch('src.probes.cpu.read_file')
    def test_cpu_probe_corrupt_info(self, mock_read_file):
        mock_read_file.return_value = """
        processor :: 0
        vendor_id- GenuineIntel
        model name  Intel(R) Core(TM) Something
        cpu cores : abc
        siblings : ??
        cache size : notanumber
        cpu family : ??
        flags :

        weird_line_without_colon
        another bad line
        """

        probe = CpuProbe()
        result = probe.run_probe()

        self.assertEqual(result['vendor'], 'Unknown')
        self.assertEqual(result['model_name'], 'Unknown')
        self.assertEqual(result['topology']['physical_cores'], 0)
        self.assertEqual(result['topology']['logical_threads'], 0)
        self.assertEqual(result['cache'], "Unknown")
        self.assertEqual(result['cpu_family'], "Unknown")
        self.assertEqual(result['cpu_model'], "Unknown")
        self.assertFalse(result['virtualization_support']) 



if __name__ == '__main__':
    unittest.main()

