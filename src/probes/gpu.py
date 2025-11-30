from src.core.utils import run_command
from .base import Probe

class GpuProbe(Probe):
    def _parse_gpu_data(self, content):
        gpus = []

        for line in content.split("\n"):
            if 'VGA' in line or '3D Controller' in line:
                parts = line.split(':', 2)
                if len(parts) > 2:
                    full_name = parts[2].strip()
                    vendor = full_name.split()[0]
                    if vendor == 'Advanced':
                        vendor = 'AMD'
                    gpus.append({'model': full_name, 'vendor': vendor})
        return gpus
    
    def run_probe(self):
        try:
            content = run_command(['lspci'])
            if not content:
                return [{'error': 'lspci failed'}]
            
            return self._parse_gpu_data(content)
        
        except FileNotFoundError:
            return [{'GPU Probe error': 'lspci not found'}]
        except Exception as e:
            return [{'GPU Probe error': str(e)}]