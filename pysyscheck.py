import os
import subprocess
import json
import datetime
import decimal

class PySysCheck:
    def __init__(self):
        # init the initial json data
        self.system_data = {
            "timestamp": str(datetime.datetime.now()),
            "report_name": "PySysCheck Hardware Report",
            "device_info": {}
        }


    # read file util function
    # returns content of the file
    def _read_file(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return content

    def _parse_cpu_data(self, content):
        # init a cpu_data
        cpu_data = {
                "vendor": "Unknown",
                "model_name": "Unknown",
                "topology": {"physical_cores": 0, "logical_threads": 0},
                "virtualization_support": False,
                "cpu_family": "Unknown",
                "cpu_model": "Unknown",
                "cache": "Unknown"
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
            if "vendor_id" in key:
                cpu_data['vendor'] = value
            
            elif "model name" in key:
                cpu_data['model_name'] = value

            elif key=="model":
                if value.isdigit():
                    cpu_data['cpu_model'] = int(value)

            
            elif "siblings" in key:
                if value.isdigit():
                    cpu_data['topology']['logical_threads'] = int(value)

            elif "cpu cores" in key:
                if value.isdigit():
                    cpu_data['topology']['physical_cores'] = int(value)

            elif "cache size" in key:
                cpu_data['cache'] = value

            elif "cpu family" in key:            
                if value.isdigit():
                    cpu_data['cpu_family'] = int(value)
                    

            elif "flags" in key:
                if "svm" in value or "vmx" in value:
                    cpu_data['virtualization_support'] = True
                
        return cpu_data

    def _map_memory_key(self, key):
        if key == "MemTotal":
            return "mem_total"
        elif key == "MemAvailable":
            return "mem_available"
        elif key == "SwapTotal":
            return "swap_total"
        
    def _parse_memory_data(self, content):
        mem_data = {}

        for line in content.split("\n"):
            if ": " not in line: continue

            # Parsing
            key,value = line.split(":",1)
            value = value.strip()
            key = key.strip()

            if key in ["MemTotal","MemAvailable", "SwapTotal"]:
                clean_value = value.split("kB")[0].strip()

                base = decimal.Decimal(int(clean_value))
                divisor = decimal.Decimal(1024*1024)

                result_gb = base / divisor


                mem_data[self._map_memory_key(key)] = f"{result_gb:.2f} GB"

        return mem_data

    def get_cpu_info(self):
        try:
            content = self._read_file("/proc/cpuinfo")
            if not content:
                self.system_data['device_info']['cpu'] = f"error: cpuinfo is empty"
            
            cpu_data = self._parse_cpu_data(content)
            self.system_data['device_info']['cpu'] = cpu_data

        # if /proc/cpuinfo doesn't exist
        except FileNotFoundError:
            self.system_data['device_info']['cpu'] = {"error": "/proc/cpuinfo not found"}

        # any unknown exception
        except Exception as e:
            self.system_data['device_info']['cpu'] = {"error": f"Parsing error: {str(e)}"}
    

    def get_memory_info(self):
        try:
            content = self._read_file("/proc/meminfo")
            if not content:
                self.system_data['device_info']['memory'] = f"error: meminfo is empty"
            
            mem_data = self._parse_memory_data(content)
            self.system_data['device_info']['memory'] = mem_data

        # if /proc/meminfo doesn't exist
        except FileNotFoundError:
            self.system_data['device_info']['memory'] = {"error": "/proc/meminfo not found"}

        # any unknown exception
        except Exception as e:
            self.system_data['device_info']['memory'] = {"error": f"Parsing error: {str(e)}"}







if __name__ == "__main__":
    psc = PySysCheck()
    psc.get_cpu_info()
    psc.get_memory_info()
    print(json.dumps(psc.system_data, indent=4))