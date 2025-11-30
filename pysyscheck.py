import argparse
import json
import datetime
import sys


from src.probes.cpu import CpuProbe
from src.probes.memory import MemoryProbe
from src.probes.disk import DiskProbe
from src.probes.network import NetworkProbe
from src.probes.usb import UsbProbe
from src.probes.gpu import GpuProbe
from src.probes.os_probe import OsProbe

class PySysCheck:
    def __init__(self):
        # init the initial json data
        self.report = {
            'timestamp': str(datetime.datetime.now()),
            'report_name': 'PySysCheck Hardware Report',
            'device_info': {}
        }

        # probes map
        self.probes = {
            'cpu': CpuProbe(),
            'memory': MemoryProbe(),
            'disk': DiskProbe(),
            'network': NetworkProbe(),
            'usb': UsbProbe(),
            'gpu': GpuProbe(),
            'os': OsProbe()
        }

    def perform_health_checks(self):
        """
        analyzes gathered data to generate PASS/FAIL results
        """
        checks = {
            'usb_subsystem_active' : 'FAIL',
            'gpu_detected': 'FAIL',
            'network_connectivity': 'FAIL',
            'ssd_present': 'FAIL'
        }


        dev_info = self.report.get('device_info', {})

        # hotplug and usb check
        try:
            hotplug_data = self.probes['usb'].get_hotplug_events()
            self.report['device_info']['hotplug_analysis'] = hotplug_data
            
            is_hotplug_active = hotplug_data.get('status') == 'Active'
        except:
            is_hotplug_active = False

        usb_list = dev_info.get('usb', [])
        
        # error handling
        has_usb_devices = usb_list and isinstance(usb_list, list) and 'error' not in str(usb_list[0]).lower()

        if has_usb_devices or is_hotplug_active:
            checks['usb_subsystem_active'] = 'PASS'

        # GPU check
        gpus = dev_info.get('gpu', [])
        if gpus and isinstance(gpus, list) and "error" not in str(gpus[0]).lower():
            checks['gpu_detected'] = "PASS"

        # network check
        net_info = dev_info.get('network', {})
        if isinstance(net_info, dict) and "error" not in net_info:
            for iface, details in net_info.items():
                if details.get('state') == 'up':
                    checks['network_connectivity'] = "PASS"
                    break

        # SSD check
        disk_info = dev_info.get('disk', {})
        if isinstance(disk_info, dict) and "error" not in disk_info:
            for disk, details in disk_info.items():
                if details.get('type') == 'SSD':
                    checks['ssd_present'] = "PASS"
                    break
        
        
        self.report['test_results'] = checks

    def run_check(self, check_type='all'):
        """
        executes selected probes
        """
        if check_type == 'all':
            print("[*] Running all checks...")
            for name, probe in self.probes.items():
                try:
                    self.report['device_info'][name] = probe.run_probe()
                except Exception as e:
                    self.report['device_info'][name] = {'error': str(e)}

        elif check_type in self.probes:
            print(f"[*] Running {check_type.upper()} check...")
            try:
                self.report['device_info'][check_type] = self.probes[check_type].run_probe()
            except Exception as e:
                self.report['device_info'][check_type] = {'error': str(e)}
        else:
            print(f"[!] Unknown check type: {check_type}")

        
        if check_type == 'all':
            print('[*] Performing health analysis...')
            self.perform_health_checks()

    def save_report(self, filename):
        """
        saves JSON report to file.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.report, f, indent=4)
            print(f'[*] Report saved successfully: {filename}')
        except Exception as e:
            print(f'[!] Error saving report: {e}')

    def print_stdout(self):
        """
        prints JSON to console
        """
        print(json.dumps(self.report, indent=4))


def main():
    parser = argparse.ArgumentParser(description='PySysCheck: Linux Hardware Probing Tool')

    # CLI Arguments
    parser.add_argument('--check', '-c', 
                        choices=['all', 'cpu', 'memory', 'disk', 'network', 'usb', 'gpu', 'os'], 
                        default='all', 
                        help="Specific hardware to check (default: all)")

    parser.add_argument('--output', '-o', 
                        help="Custom output filename", 
                        default=f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    parser.add_argument('--no-file', action='store_true', 
                        help="Don't save to file, print to console only")
    
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help="Print output to console even if saving to file")
    
    args = parser.parse_args()


    # application logic
    app = PySysCheck()
    app.run_check(args.check)

    if args.no_file:
        app.print_stdout()
    else:
        app.save_report(args.output)
        if args.verbose:
            app.print_stdout()


if __name__ == '__main__':
    main()