import os
from src.core.utils import read_file
from .base import Probe

class NetworkProbe(Probe):
    def run_probe(self):
        """
        main method of the network probe
        scans /sys/class/net and extracting the mac adress and operation state
        returns dict or error
        """
        network_data = {}
        net_path = '/sys/class/net'
        
        try:
            if not os.path.exists(net_path):
                return {'error': '/sys/class/net not found'}

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
                    mac = read_file(mac_path)
                    if mac: iface_info['mac'] = mac.strip()
                except: pass

                # read the state files
                try:
                    state = read_file(state_path)
                    if state: iface_info['state'] = state.strip()
                except: pass
                
                network_data[iface] = iface_info
            return network_data

        except Exception as e:
            return {'error': f'Network Probe error: {str(e)}'}