from src.core.utils import read_file
from .base import Probe

class CpuProbe(Probe):
    
    def _parse_cpu_data(self, content):
        """
        parses /proc/cpuinfo content strings into a dict
        """

        # init a cpu_data
        cpu_data = {
                'vendor': 'Unknown',
                'model_name': 'Unknown',
                'topology': {'physical_cores': 0, 'logical_threads': 0},
                'virtualization_support': False,
                'cpu_family': 'Unknown',
                'cpu_model': 'Unknown',
                'cache': 'Unknown'
        }
        # parse the logical thread and check error
        cpu_groups = content.strip().split("\n\n")
        if not cpu_groups: return

        # just take the first logical thread
        for line in cpu_groups[0].split("\n"):
            if ": " not in line: continue

            # extract the value of each line 
            # example line: "cpuid level     : 16" 
            key,value = line.split(":",1)
            value = value.strip()
            key = key.strip()


            # save each value in their respective position
            if 'vendor_id' in key:
                cpu_data['vendor'] = value
            
            elif 'model name' in key:
                cpu_data['model_name'] = value

            elif key == 'model':
                if value.isdigit():
                    cpu_data['cpu_model'] = int(value)

            
            elif 'siblings' in key:
                if value.isdigit():
                    cpu_data['topology']['logical_threads'] = int(value)

            elif 'cpu cores' in key:
                if value.isdigit():
                    cpu_data['topology']['physical_cores'] = int(value)

            elif 'cache size' in key:
                cpu_data['cache'] = value

            elif 'cpu family' in key:            
                if value.isdigit():
                    cpu_data['cpu_family'] = int(value)
                    

            elif 'flags' in key:
                if 'svm' in value or 'vmx' in value:
                    cpu_data['virtualization_support'] = True
                
        return cpu_data        

    def run_probe(self):
        """
        main execution method for the CPU probe
        returns a dictionary with data or error
        """
        try:
            content = read_file('/proc/cpuinfo')
            if not content:
                return {'error': 'cpuinfo is empty'}
            
            cpu_data = self._parse_cpu_data(content)
            return cpu_data

        # if /proc/cpuinfo doesn't exist
        except FileNotFoundError:
            return {'error': '/proc/cpuinfo not found'}

        # any unknown exception
        except Exception as e:
            return {'error': f'Cpu Probe error: {str(e)}'}