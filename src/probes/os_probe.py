from src.core.utils import read_file
from .base import Probe

class OsProbe(Probe):
    # third line is kernel version 
    def _parse_kernel_data(self, content):
        kernel_data = {'version': 'Unknown', 'build_date': 'Unknown', 'smp_support': False}
        if not content: return kernel_data

        if 'SMP' in content:
            kernel_data['smp_support'] = True


        parts = content.split()
        if len(parts) > 2:
            kernel_data['version'] = parts[2].strip()

        if '#' in content:
            parts = content.split('#')
            if len(parts) > 1:
                try:
                    right_parts = parts[1].split()[3:]
                    build_date = ' '.join(right_parts)
                    kernel_data['build_date'] = build_date
                except: pass
        
        return kernel_data
    
    def _parse_distro_data(self, content):
        distro_name = 'Unknown Linux'
        if not content: return distro_name
        
        for line in content.split("\n"):
            if line.startswith('PRETTY_NAME='):
                distro_name = line.split('=',1)[1].replace('"', '').strip()
                break

        return distro_name
    

    def run_probe(self):
        os_info = {}
        
        try:
            kernel_content = read_file('/proc/version')

            os_info = self._parse_kernel_data(kernel_content)


        except Exception as e:
            return {'error': f'Kernel parse error: {e}'}
        

        try:
            distro_content = read_file('/etc/os-release')
            os_info['distro'] = self._parse_distro_data(distro_content)
        except:
            os_info['distro'] = 'Unknown'
        
        return os_info
