from bat import bro_log_reader, log_to_dataframe
from forest import Forest
from pprint import pprint
import os

class MNTC:
    def __init__(self,log_dir = None, debug = False):
        self.log_dir = log_dir
        self.log_paths = []
        self.debug = debug
        if log_dir is not None:
            self.constructPaths(log_dir)
            self.loadLogs(log_dir)
    
    def loadLogs(self, log_dir = None):
        print "Loading log files. This can take a few minutes depending on file size."
        if log_dir is None:
            return
        raw_logs = {'conn':{},'ssl':{},'x509':{}}
        for log in self.log_paths:
            reader = bro_log_reader.BroLogReader(log)
            for row in reader.readrows():
                if 'conn.log' in log:
                    raw_logs['conn'][row['uid']] = row
                    break
                if 'ssl.log' in log:
                    raw_logs['ssl'][row['uid']] = row
                    break
                else:
                    raw_logs['x509'][row['id']] = row
                    # print row
                    # raw_logs['x509'].append(row)
                    break
        # print raw_logs['conn']['Cp9zbb41PewMjy5tOe']
        # print raw_logs['conn']['Cp9zbb41PewMjy5tOe']
        # print raw_logs['ssl']
        # raw_logs['ssl']['CyxxK9uoeEsgS6Dz4']['cert_chain_fuids'].split(',')[0]
        self.interpretLogs(raw_logs)
    
    def constructPaths(self, log_dir = None):
        search = ['conn.log', 'ssl.log', 'x509.log']
        if type(log_dir) is str:
            if os.path.isdir(log_dir):
                dir_contents = [name for name in os.listdir(log_dir)]
                for obj in dir_contents:
                    self.constructPaths(log_dir + '/'+obj)
            else:
                for item in search:
                    if item in log_dir:
                        self.log_paths.append(log_dir)
                        return
        else:
            for item in log_dir:
                if os.path.isdir(item):
                    sub_dirs = [name for name in os.listdir(item)]
                    for obj in sub_dirs:
                        self.constructPaths(item+'/'+obj)
    
    def interpretLogs(self, logs):
        conn = logs['conn']
        ssl = logs['ssl']
        x509 = logs['x509']

        for id,record in ssl.items():
            if id in conn:
                target = conn[id]
                (SrcIP, DstIp, DstPort,protocol) = target['id.orig_h'], target['id.resp_h'], target['id.resp_p'], target['service']
                print SrcIP, DstIp, DstPort, protocol
            else:
                print("do something else")
