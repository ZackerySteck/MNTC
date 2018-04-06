from bat import bro_log_reader, log_to_dataframe
from forest import Forest
from pprint import pprint
import os

class MNTC:
    def __init__(self,log_dir = None, labels = None, debug = False):
        self.log_dir = log_dir
        self.raw_logs = None
        self.log_paths = []
        self.debug = debug
        self.labels = labels
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
                    # break
                elif 'ssl.log' in log:
                    raw_logs['ssl'][row['uid']] = row
                else:
                    raw_logs['x509'][row['id']] = row
        # print raw_logs['ssl'].items()[0]
        self.raw_logs = raw_logs
        self.interpretLogs(raw_logs)

    # Recursively construct directory strings from root until files are found
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
    
    def interpretLogs(self, logs = None):
        if logs is None:
            return
        conn = logs['conn']
        ssl = logs['ssl']
        x509 = logs['x509']

        # Items we want:
        # 1. Connection 4-Tuple
        # --- SSL Aggregation ---
        # 1. SSL 4-tuple
        # 2. SSL Record
        # 3. Connection Record
        # 4. x509 certs

        data = []
        for id,ssl_record in ssl.items():
            if id in conn:
                ssl_tuple = ssl_record['id.orig_h'], ssl_record['id.resp_h'], ssl_record['id.resp_p'], ssl_record['version']
                # Get connection record of SSL session
                connection_record = conn[id]
                # Build 4-tuple
                conn_tuple = (SrcIP, DstIp, DstPort,protocol) = connection_record['id.orig_h'], connection_record['id.resp_h'], connection_record['id.resp_p'], connection_record['service']
                # Label 4-tuple
                conn_label = 'Normal'
                if self.labels is not None and (SrcIP in self.labels or DstIp in self.labels):
                    conn_label = 'Malicous'
                # Get certs for SSL session
                cert_key = ssl_record['cert_chain_fuids'].split(',')[0]
                certs = None
                if cert_key !=  '-':
                    certs = x509[cert_key]
                ssl_aggregation = [ssl_record, connection_record] if certs is None else [ssl_record, certs,connection_record]
                data.append([conn_tuple, ssl_aggregation, conn_label])
        print data
        # for id,record in conn.items():
        #     conn_tuple = (SrcIP, DstIp, DstPort,protocol) = connection_record['id.orig_h'], connection_record['id.resp_h'], connection_record['id.resp_p'], connection_record['service']
        #     if conn_tuple in data[0,:] and data



# Find the ssl sessions in the set of connections
# Match these ssl sessions to their respective connection 4-tuple
# For the ssl sessions, aggregate the connection record, SSL record, Certifications, and label
