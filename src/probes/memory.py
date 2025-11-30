import decimal
from src.core.utils import read_file
from .base import Probe


class MemoryProbe(Probe):
    def _map_memory_key(self, key):
        """Helper to standardize memory keys."""
        if key == 'MemTotal': return 'mem_total'
        elif key == 'MemAvailable': return 'mem_available'
        elif key == 'SwapTotal': return 'swap_total'
        return key.lower()

    def _parse_memory_data(self, content):
        """
        parses /proc/meminfo content
        """
        mem_data = {}

        for line in content.split("\n"):
            if ": " not in line: continue

            # Parsing
            key,value = line.split(":",1)
            value = value.strip()
            key = key.strip()

            if key in ['MemTotal','MemAvailable', 'SwapTotal']:
                clean_value = value.split("kB")[0].strip()

                base = decimal.Decimal(int(clean_value))
                divisor = decimal.Decimal(1024*1024)

                result_gb = base / divisor


                mem_data[self._map_memory_key(key)] = f"{result_gb:.2f} GB"

        return mem_data
    

    def run_probe(self):
        """
        main execution method for the Memory probe
        returns a dictionary with data or error
        """
        try:
            content = read_file('/proc/meminfo')
            if not content:
                return {'error': 'meminfo is empty'}
            
            return self._parse_memory_data(content)

        # if /proc/meminfo doesn't exist
        except FileNotFoundError:
            return {'error': '/proc/meminfo not found'}

        # any unknown exception
        except Exception as e:
            return {'error': f'Memory Probe Error: {str(e)}'}