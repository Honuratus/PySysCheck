from src.core.utils import run_command
from .base import Probe

class UsbProbe(Probe):
    def _parse_usb_data(self, content):
        """
        parsing the content and extracting the usb names
        """
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
    
    def get_hotplug_events(self):
        """
        parses dmesg for recent USB activity.
        returns a dict with status and events.
        """
        hotplug_data = {'status': 'Inactive', 'recent_events': []}
        try:
            output = run_command(['dmesg'])
            # sudo privaliges not granted
            # or dmesg failed
            if not output:
                hotplug_data['status'] = 'Permission Denied / Empty'
                return hotplug_data

            lines = output.split('\n')
            found_events = []


            # just look the last 10 events
            for line in  reversed(lines):
                if len(found_events) > 10: break
                    
                line_lower = line.lower()
                if 'usb' in line and ('new' in line or 'disconnect' in line):
                    found_events.append(line.strip())
            if found_events:
                hotplug_data['status'] = 'Active'
                hotplug_data['recent_events'] = found_events 

        except Exception as e:
            hotplug_data['error'] = f'Error parsing dmesg: {str(e)}'

        return hotplug_data

    def run_probe(self):
        """
        collects usb list via command "lsusb"
        """
        try:
            content = run_command(['lsusb'])
            
            if not content:
                return [{'error' : 'lsusb command failed or returned empty'}]
            
            return self._parse_usb_data(content)

        except Exception as e:
             return [{'error': f'USB Probe Error: {str(e)}'}]
    
