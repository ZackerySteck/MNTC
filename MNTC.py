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
        raw_logs = {'conn':[],'ssl':[],'x509':[]}
        for log in self.log_paths:
            reader = bro_log_reader.BroLogReader(log)
            for row in reader.readrows():
                if 'conn.log' in log:
                    raw_logs['conn'].append(row)
                    break
                if 'ssl.log' in log:
                    raw_logs['ssl'].append(row)
                else:
                    raw_logs['x509'].append(row)
        print raw_logs['conn'][0]
        print raw_logs['ssl'][0]
    
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