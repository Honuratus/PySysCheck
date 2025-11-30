import os
import decimal
from src.core.utils import read_file
from .base import Probe

class DiskProbe(Probe):
    
    def _parse_disk_data(self, disk_name):
        """
        extracts model, type (SSD/HDD), and size for a specific disk
        """
        disk_data = {'model': 'Unknown', 'type': 'Unknown', 'size': 'Unknown'}
        base_path = f'/sys/block/{disk_name}'

        # model reading
        try:
            disk_model = read_file(f'{base_path}/device/model')
            if disk_model:
                disk_data['model'] = disk_model.strip()
        except:
            pass # if model file not found it will remian unknown
            
        # type reading
        try:
            disk_type = read_file(f'{base_path}/queue/rotational')
            if disk_type:
                # 0 SSD
                # 1 HDD
                disk_data['type'] = 'SSD' if disk_type.strip() == '0' else 'HDD'
        except:
            pass


        # size calculation
        try:
            size_content = read_file(f'{base_path}/size')

            if size_content:
                disk_size = int(size_content.strip())

                byte_size = disk_size * 512

                base = decimal.Decimal(byte_size)
                divisor = decimal.Decimal(1024**3)

                gb_size = base / divisor
                disk_data['size'] = f'{gb_size:.2f} GB'
        except:
            disk_data['size'] = 'Unknown'
        return disk_data

    def run_probe(self):
        """
        scans /sys/block, filters virtual disks, and probes physical ones.
        """
        disks = {}
        block_path = '/sys/block'

        try:
            if not os.path.exists(block_path):
                return {'error': '/sys/block not found'}

            for block in os.listdir(block_path):
                # loop (virtual disk)
                # ram (ram disk)
                # sr (CD-ROM)
                # skip all the above
                if (block.startswith('loop')) or (block.startswith('ram')) or (block.startswith('sr')):
                    continue

                disks[block] = self._parse_disk_data(block)
            
            return disks

        except Exception as e:
            return {'error' : f'Disk Probe error: {str(e)}'}