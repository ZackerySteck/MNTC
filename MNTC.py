class MNTC:
    def __init__(self,pcap = None, debug = False):
        self.pcap = pcap
        self.debug = debug
        if pcap is not None:
            self.loadPCAP(pcap)
    
    def loadPCAP(self, pcap = None):
        self.pcap = pcap
        if pcap is None:
            return
        