import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.probes.gpu import GpuProbe


class TestGpuProbes(unittest.TestCase):
    
    @patch('src.probes.gpu.run_command')
    def test_gpu_probe_success(self, mock_run_command):
        mock_run_command.return_value = """
        74:00.5 Multimedia controller: Advanced Micro Devices, Inc. [AMD] ACP/ACP3X/ACP6x Audio Coprocessor (rev 60)
        74:00.6 Audio device: Advanced Micro Devices, Inc. [AMD] Family 17h/19h HD Audio Controller
        75:00.0 USB controller: Advanced Micro Devices, Inc. [AMD] Rembrandt USB4 XHCI controller #8
        75:00.3 USB controller: Advanced Micro Devices, Inc. [AMD] Rembrandt USB4 XHCI controller #5
        75:00.4 USB controller: Advanced Micro Devices, Inc. [AMD] Rembrandt USB4 XHCI controller #6
        75:00.6 USB controller: Advanced Micro Devices, Inc. [AMD] Rembrandt USB4/Thunderbolt NHI controller #2
        74:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Rembrandt [Radeon 680M] (rev c9)
        01:00.0 VGA compatible controller: NVIDIA Corporation GA107M [GeForce RTX 3050 Mobile] (rev a1)
        """

        probe = GpuProbe()
        result = probe.run_probe()

        self.assertIsInstance(result, list)
        self.assertEqual(2, len(result))

        self.assertIsInstance(result[0], dict)
        self.assertIsInstance(result[1], dict)

        self.assertEqual(result[0]['model'], "Advanced Micro Devices, Inc. [AMD/ATI] Rembrandt [Radeon 680M] (rev c9)")
        self.assertEqual(result[0]['vendor'], "AMD")

        self.assertEqual(result[1]['model'], "NVIDIA Corporation GA107M [GeForce RTX 3050 Mobile] (rev a1)")
        self.assertEqual(result[1]['vendor'], "NVIDIA")


        

    @patch('src.probes.gpu.run_command')
    def test_gpu_probe_io_error(self, mock_run_command):        
        mock_run_command.side_effect = FileNotFoundError("lspci not found")
        
        probe = GpuProbe()
        result = probe.run_probe()

        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        

        self.assertIsInstance(result[0], dict)
        self.assertIn('GPU Probe error', result[0])
        self.assertEqual('lspci not found', result[0]['GPU Probe error'])

    @patch('src.probes.gpu.run_command')
    def test_gpu_probe_corrupt_return(self, mock_run_command):
        mock_run_command.return_value = """
        Advanced Mirco asd, Inc. [AMD/ATI] Rembrandt [Radeon 680M] (rev c9)
        NVIIDA CORP [NVIDIA] Rembrandt [GTXX 9080] (rev c9)
        """

        probe = GpuProbe()
        result = probe.run_probe()

        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))


    @patch('src.probes.gpu.run_command')
    def test_gpu_probe_execution_error(self, mock_run_command):
        """Genel bir komut çalıştırma hatasında (Exception) doğru hatayı döndürür."""
        
        # run_command, FileNotFoundError dışındaki bir exception fırlatsın
        mock_run_command.side_effect = PermissionError("İzin reddedildi.")
        
        probe = GpuProbe()
        result = probe.run_probe()

        # Kontrol: Genel hata formatı beklenir.
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertIn('GPU Probe error', result[0])
        self.assertIn('İzin reddedildi.', result[0]['GPU Probe error'])