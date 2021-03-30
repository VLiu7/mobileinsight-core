"""
Offline analysis by replaying logs
"""

# from mobile_insight.monitor import SatOfflineReplayer
from mobile_insight.monitor import OfflineMonitor 
from mobile_insight.analyzer import SatRlcAnalyzer

if __name__ == '__main__':
    src = OfflineMonitor()
    src.set_input_path('Southeast_gate_ping.txt')
    analyzer = SatRlcAnalyzer()
    analyzer.set_source(src)
    src.run()
    pass