import os
import subprocess
import json
import datetime
import decimal

class PySysCheck:
    def __init__(self):
        # init the initial json data
        self.system_data = {
            'timestamp': str(datetime.datetime.now()),
            'report_name': 'PySysCheck Hardware Report',
            'device_info': {}
        }


    # read file util function
    # returns content of the file
    def _read_file(self, file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return content

    def _run_command(self, command_list):
        output = subprocess.run(command_list, capture_output=True, text=True)
        if output.returncode == 0:
            return output.stdout
        return None

    def _parse_cpu_data(self, content):
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

    def _map_memory_key(self, key):
        if key == 'MemTotal':
            return 'mem_total'
        elif key == 'MemAvailable':
            return 'mem_available'
        elif key == 'SwapTotal':
            return 'swap_total'
        
    def _parse_memory_data(self, content):
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
    
    def _parse_usb_data(self, content):
        usb_list = []

        for line in content.split("\n"):
            if not line: continue

            if 'ID' in line:
                parts = line.split('ID')
                if len(parts) > 1:

                    raw_info = parts[1].strip()

                    # ID Fomrat: "XXXX:XXXX" 
                    # skip the first 9 char and 1 whitespace
                    device_name = raw_info[10:].strip()

                    if not device_name:
                        device_name = raw_info
                
                usb_list.append(device_name)
        return usb_list

    # third line is kernel version 

    def _parse_kernel_info(self, content):
        kernel_data = {"version": "Unknown", "build_date": "Unknown", "smp_support": False}
        if not content: return kernel_data

        if "SMP" in content:
            kernel_data['smp_support'] = True


        parts = content.split()
        if len(parts) > 2:
            kernel_data['version'] = parts[2].strip()

        if "#" in content:
            parts = content.split('#')
            if len(parts) > 1:
                right_parts = parts[1].split()[3:]
                build_date = ' '.join(right_parts)
                kernel_data['build_date'] = build_date
        
        return kernel_data
    

    def _parse_distro_info(self, content):
        distro_name = "Unknown Linux"
        if not content: return distro_name
        
        for line in content.split("\n"):
            if line.startswith('PRETTY_NAME='):
                distro_name = line.split('=',1)[1].replace('"', '').strip()
                break

        return distro_name


    def get_cpu_info(self):
        try:
            content = self._read_file('/proc/cpuinfo')
            if not content:
                self.system_data['device_info']['cpu'] = {'error' : 'cpuinfo is empty'}
            
            cpu_data = self._parse_cpu_data(content)
            self.system_data['device_info']['cpu'] = cpu_data

        # if /proc/cpuinfo doesn't exist
        except FileNotFoundError:
            self.system_data['device_info']['cpu'] = {'error': '/proc/cpuinfo not found'}

        # any unknown exception
        except Exception as e:
            self.system_data['device_info']['cpu'] = {'error': f'Parsing error: {str(e)}'}
    

    def get_memory_info(self):
        try:
            content = self._read_file('/proc/meminfo')
            if not content:
                self.system_data['device_info']['memory'] = {'error': 'meminfo is empty'}
            
            mem_data = self._parse_memory_data(content)
            self.system_data['device_info']['memory'] = mem_data

        # if /proc/meminfo doesn't exist
        except FileNotFoundError:
            self.system_data['device_info']['memory'] = {'error': '/proc/meminfo not found'}

        # any unknown exception
        except Exception as e:
            self.system_data['device_info']['memory'] = {'error': f'Parsing error: {str(e)}'}


    def get_usb_info(self):
        try:
            content = self._run_command(['lsusb'])
            
            if not content:
                self.system_data['device_info']['usb'] = {'error' : 'lsusb command failed or returned empty'}
                return
            
            usb_data = self._parse_usb_data(content)
            self.system_data['device_info']["usb"] = usb_data

        except FileNotFoundError:
             self.system_data['device_info']['usb'] = {'error': 'lsusb command not found'}
        except Exception as e:
            self.system_data['device_info']['usb'] = {'error': f'{str(e)}'}

    def get_network_info(self):
        self.system_data['device_info']['network'] = {}
        net_path = '/sys/class/net'
        
        try:
            if not os.path.exists(net_path):
                self.system_data['device_info']['network'] = {'error': '/sys/class/net not found'}
                return

            for iface in os.listdir(net_path):
                # skip the localhost
                if iface == 'lo': continue 
                
                # init interface dict
                iface_info = {'mac': 'Unknown', 'state': 'Unknown'}
                
                # create folder paths
                mac_path = os.path.join(net_path, iface, 'address')
                state_path = os.path.join(net_path, iface, 'operstate')
                
                # read the mac address files
                try:
                    mac = self._read_file(mac_path).strip()
                    if mac: iface_info['mac'] = mac
                except: pass

                # read the state files
                try:
                    state = self._read_file(state_path).strip()
                    if state: iface_info['state'] = state
                except: pass
                
                self.system_data['device_info']['network'][iface] = iface_info

        except Exception as e:
            self.system_data['device_info']['network'] = {'error': f'Network scan error: {str(e)}'}
        

    def get_os_info(self):
        self.system_data['device_info']['os'] = {}
        
        try:
            kernel_content = self._read_file('/proc/version')

            kernel_data = self._parse_kernel_info(kernel_content)


            self.system_data['device_info']['os'] = kernel_data
        except Exception as e:
            self.system_data['device_info']['os'] = {'error': f'Kernel parse error: {e}'}
        

        try:
            distro_content = self._read_file('/etc/os-release')
            distro_name = self._parse_distro_info(distro_content)
            self.system_data['device_info']['os']['distro'] = distro_name
        except:
            self.system_data['device_info']['os']['distro'] = "Unknown"


    def save_report(self):
        self.get_cpu_info()
        self.get_memory_info()
        self.get_network_info()
        self.get_usb_info()
        self.get_os_info()
        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(self.system_data,f, indent=4)
            print(f'Report saved successfully: {filename}')
        except Exception as e:
            print(f'Error saving report: {e}')


if __name__ == '__main__':
    psc = PySysCheck()
    psc.save_report()