"""
Offline analysis by replaying logs
"""

# from mobile_insight.monitor import SatOfflineReplayer
from mobile_insight.monitor import OfflineMonitor 

if __name__ == '__main__':
    src = OfflineMonitor()
    src.set_input_path('Southeast_gate_ping.txt')
    # TODO: bind to analyzer
    src.run()
    pass