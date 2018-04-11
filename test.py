from bat import bro_log_reader, log_to_dataframe
import pandas as pd
import numpy as np
import datetime, time, cPickle, os


class TEST:
    def __init__(self,log_dir = None, labels = None, debug = False):
        self.log_dir = log_dir
        self.log_paths = []
        self.debug = debug
        self.labels = labels
        if log_dir is not None:
            self.constructPaths(log_dir)

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
    
    def preProcess(self, log_dir = None):
        print "Loading log files. This can take a some time depending on file size."
        if self.log_paths is None:
            return
        elif log_dir is None:
            log_dir = self.log_paths
        for log in log_dir:
            if 'conn.log' in log:
                # df = log_to_dataframe.LogToDataFrame(log)
                reader = bro_log_reader.BroLogReader(log)
                start = time.time()
                i = 0
                for row in reader.readrows():
                    if i == 0:
                        df = pd.DataFrame([{'tuple':(row['id.orig_h'],row['id.resp_h'],row['id.resp_p'],row['service']),
                                'duration':row['duration'],
                                'orig_bytes':row['orig_bytes'],
                                'resp_bytes':row['resp_bytes'],
                                'orig_pkts':row['orig_pkts'],
                                'resp_pkts':row['resp_pkts'],
                                'ts':row['ts'],
                                'conn_state':row['conn_state'],
                                'uid':row['uid']}])
                        # print df.shape
                        df.to_pickle('./Intermediate/conn2.pkl')
                        i+=1
                    else:
                        conn = pd.read_pickle('./Intermediate/conn2.pkl')
                        df = pd.DataFrame([{'tuple':(row['id.orig_h'],row['id.resp_h'],row['id.resp_p'],row['service']),
                                'duration':row['duration'],
                                'orig_bytes':row['orig_bytes'],
                                'resp_bytes':row['resp_bytes'],
                                'orig_pkts':row['orig_pkts'],
                                'resp_pkts':row['resp_pkts'],
                                'ts':row['ts'],
                                'conn_state':row['conn_state'],
                                'uid':row['uid']}])
                        # print conn.shape
                        combined = pd.concat([conn, df])
                        # print combined.shape
                        combined.to_pickle('./Intermediate/conn2.pkl')
                        # print df.shape
                # sup_df = pd.DataFrame(df_lst)
                # del df_lst
                # sup_df.to_pickle('./Intermediate/conn.pkl')
                # print sup_df.shape
                elapsed = time.time() - start
                conn = pd.read_pickle('./Intermediate/conn2.pkl')
                print conn.shape
                print elapsed
                raw_input('Press enter to terminate.')
                # print sup_df
