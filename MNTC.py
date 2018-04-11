from bat import bro_log_reader, log_to_dataframe
import pandas as pd
import numpy as np
from forest import Forest
import os
import datetime

class MNTC:
    def __init__(self,log_dir = None, labels = None, debug = False):
        self.log_dir = log_dir
        self.log_paths = []
        self.debug = debug
        self.labels = labels
        if log_dir is not None:
            self.constructPaths(log_dir)
            self.loadLogs(log_dir)

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
    
    def loadLogs(self, log_dir = None):
        print "Loading log files. This can take a few minutes depending on file size."
        raw_logs = {'conn':{},'ssl':{},'x509':{}}
        for log in self.log_paths:
            reader = bro_log_reader.BroLogReader(log)
            for row in reader.readrows():
                if 'conn.log' in log:
                    raw_logs['conn'][row['uid']] = ((row['id.orig_h'],
                                                    row['id.resp_h'],
                                                    row['id.resp_p'],
                                                    row['service']),
                                                    {'duration':row['duration'],
                                                    'orig_bytes':row['orig_bytes'],
                                                    'resp_bytes':row['resp_bytes'],
                                                    'orig_pkts':row['orig_pkts'],
                                                    'resp_pkts':row['resp_pkts'],
                                                    'ts':row['ts'],
                                                    'conn_state':row['conn_state']})
                    # if len(raw_logs['conn']) == 1000000:
                    #     break
                elif 'ssl.log' in log:
                    raw_logs['ssl'][row['uid']] = row
                else:
                    raw_logs['x509'][row['id']] = row
        # print raw_logs['conn'].items()[0]
        self.interpretLogs(raw_logs)
    

    # --- Connection 4-Tuple ---
    # 1. 4-tuple (srcip, dstip, dstport, protocol) - Acts as UID for each Conn 4-tuple
        # 2. SSL Aggregations
        # 3. Connection Records
        # .... OTHER FEATURES ....

        # --- SSL Aggregation ---
        # 1. SSL Record
        # 2. Connection Record
        # 3. x509 certs
    def interpretLogs(self, logs = None):
        if logs is None:
            return
        conn = logs['conn']
        ssl = logs['ssl']
        x509 = logs['x509']
        logs.clear()

        data = {}
        features = {}
        print 'Interpreting Logs...'
        for id,ssl_record in ssl.items():
            if id in conn:
                # Get connection record of SSL session (if it exists)
                connection_record = conn[id]
                conn_tuple = connection_record[0]
                # Label 4-tuple
                conn_label = 'Normal'
                if self.labels is not None and (conn_tuple[0] in self.labels or conn_tuple[1] in self.labels):
                    conn_label = 'Malicous'
                # Get certs for SSL session (If they exist)
                cert_key = ssl_record['cert_chain_fuids'].split(',')[0]
                certs = None
                if cert_key !=  '-':
                    certs = x509[cert_key]
                # Create the SSL Aggregation
                ssl_aggregation = [connection_record[1], ssl_record] if certs is None else [connection_record[1],ssl_record, certs]
                
                # If the connection is already stored, append the SSL Aggregation. Otherwise, create new entry
                if conn_tuple in data:
                    data[conn_tuple][1].append(ssl_aggregation)
                else:
                    features[conn_tuple] = [0.0 for x in xrange(28)]
                    data[conn_tuple] = [[],[ssl_aggregation], conn_label]
            
                features[conn_tuple][4] += connection_record[1]['orig_bytes']
                features[conn_tuple][5] += connection_record[1]['resp_bytes']
                features[conn_tuple][8] += connection_record[1]['orig_pkts']
                features[conn_tuple][9] += connection_record[1]['resp_pkts']

        for id,record in conn.items():
            conn_tuple = record[0]
            record = record[1]
            if conn_tuple in data:
                found = False
                for agg in data[conn_tuple][1]:
                    if record in agg:
                        found = True
                if record not in data[conn_tuple][0] and ~found:
                    data[conn_tuple][0].append(record)
                    # For each connection record, add the corresponding byte values
                    features[conn_tuple][4] += record['orig_bytes']
                    features[conn_tuple][5] += record['resp_bytes']
                    features[conn_tuple][8] += record['orig_pkts']
                    features[conn_tuple][9] += record['resp_pkts']
                del conn[id]

        print 'now here'
        for id,record in data.items():
            conn_records = record[0]
            ssl_aggs = record[1]
            label = record[2]
            ssl_conn_records = [agg[0] for agg in ssl_aggs]

            # conn_records.sort(key=lambda r: r['ts'])
            # ssl_conn_records.sort(key=lambda r: r['ts'])

            combined = conn_records + ssl_conn_records
            combined.sort(key=lambda r: r['ts'])

            durations = [x['duration'].total_seconds() for x in combined]
            durations_squared = [pow(x['duration'].total_seconds(), 2) for x in combined]

            # ---------------- Calculate Connection Features --------------------------
            features[id][0] = len(combined)
            if len(conn_records) > 0:
                features[id][1] = mean(durations)
                features[id][2] = pow( mean(durations_squared) - pow(features[id][2], 2), 0.5)

                lb = features[id][1] - features[id][2]
                ub = features[id][1] + features[id][2] 

                features[id][3] = len([x for x in conn_records if (x['duration'].total_seconds() < lb or x['duration'].total_seconds() > ub)]) / float(len(durations))
                features[id][6] = features[id][5] / (features[id][5] + features[id][4])

                e_states = ['SF', 'S1', 'S2', 'S3', 'RSTO', 'RSTR']
                # non_e_states = ['OTH', 'SO', 'REJ', 'SH', 'SHR', 'RSTOS0', 'RSTRH']
                e = len([x for x in combined if (x['conn_state'] in e_states)])
                n = len(combined) - e

                features[id][7] = e / (e+n)

                ts = [x['ts'] for x in combined]
                interval_1 = []
                periodicity = []
                for i in range(len(ts)-1):
                    t1 = ts[i]
                    t2 = ts[i+1]
                    interval_1.append((t2 - t1).total_seconds())
                for i in range(len(interval_1)-1):
                    p1 = interval_1[i]
                    p2 = interval_1[i+1]
                    periodicity.append(abs(p2-p1))
                features[id][10] = mean(periodicity)

                periodicity_squared = [pow(x,2) for x in periodicity]
                features[id][11] = pow( mean(periodicity_squared) - pow(features[id][10], 2), 0.5)

            # ------------------ Calculate SSL Features ----------------------------
            features[id][13] = len(conn_records) / len(ssl_aggs)
            del data[id]
        print features



def mean(L):
    return 0 if len(L) == 0 else sum(L) / len(L)
