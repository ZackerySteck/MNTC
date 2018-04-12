import pandas as pd
from utils import *
import datetime, time, os

class MalNetTraffClass:
    def __init__(self,log_dir = None, labels = None, debug = False, pickle = False):
        self.log_dir = log_dir
        self.log_paths = []
        self.debug = debug
        self.labels = labels
        self.pickle = pickle
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
    
    def parseLog(self, log, cols, skiprows):
        if self.pickle and os.path.isfile('./pickle/'+log.replace('/','%')+'.pkl'):
                pickle = './pickle/'+log.replace('/','%')+'.pkl'
                print 'Pickle found for %s! Loading.' % (bcolors.UNDERLINE+log+bcolors.ENDC)
                return pd.read_pickle(pickle)
        print('Processing %s' % (bcolors.UNDERLINE+log+bcolors.ENDC))
        return pd.read_csv(log,delimiter='\t',
                header=6,skiprows=skiprows,
                index_col=None,usecols=cols,
                low_memory=False).head(-1)

    def preProcess(self, log_dir = None):
        print bcolors.WARNING+"Loading log files. This can take a some time depending on file size."+bcolors.ENDC
        print '-'*40
        conn, ssl, x509 = None,None,None
        if self.log_paths is None:
            return
        elif log_dir is None:
            log_dir = self.log_paths
        for log in log_dir:
            current = None
            start = time.time()
            if 'conn.log' in log:
                conn = self.parseLog(log, [0,1,2,4,5,7,8,9,10,16,18], [7, -1])
                conn.columns = ['ts', 'uid', 'id.orig_h','id.resp_h','id.resp_p','service',
                                'duration','orig_bytes','resp_bytes','orig_pkts','resp_pkts']
                current = conn
            elif 'ssl.log' in log:
                ssl = self.parseLog(log, [0,1,2,4,5,6,14], [7, -1])
                ssl.columns = ['ts', 'uid', 'id.orig_h','id.resp_h','id.resp_p','version','cert_chain_fuids']
                current = ssl
            else:
                x509 = self.parseLog(log, range(20), [7, -1])
                x509.columns = ['ts','id','certificate.version',
                               'certificate.serial','certificate.subject',
                               'certificate.issuer','certificate.not_valid_before',
                               'certificate.not_valid_after','certificate.key_alg',
                               'certificate.sig_alg','certificate.key_type',
                               'certificate.key_length','certificate.exponent',
                               'certificate.curve','san.dns','san.uri','san.email','san.ip',
                               'basic_constraints.ca','basic_constraints.path_len']
                current = x509
            if current is not None:
                elapsed = time.time() - start
                print('File processing completed in %0.4f seconds' % (elapsed))
                print(bcolors.OKBLUE+'Dimensions after processing: %d x %d' % current.shape)
                print bcolors.ENDC
                if self.pickle and not os.path.isfile('./pickle/'+log.replace('/','%')+'.pkl'):
                    start = time.time()
                    print('Pickling dataset...')
                    current.to_pickle('./pickle/'+log.replace('/','%')+'.pkl')
                    elapsed = time.time() - start
                    print('File pickled in %0.4f seconds' % (elapsed))
                print '-'*40
        self.constructFeatures(conn,ssl,x509)
    
    def constructFeatures(self,conn,ssl,x509):
        # conn.set_index('uid', inplace=True)
        ssl.set_index('uid', inplace=True)
        # x509.set_index('id', inplace=True)
        
        aggregate_data = {}
        for id,ssl_record in ssl.iterrows():
            conn_record = conn.loc[id]
            if conn_record is not None:
                # Get connection record of SSL session (if it exists)
                conn_tuple = (conn_record['id.orig_h'], conn_record['id.resp_h'], conn_record['id.resp_p'],conn_record['service'])
                # Label 4-tuple
                label = 'Normal'
                if self.labels is not None and (conn_tuple[0] in self.labels or conn_tuple[1] in self.labels):
                    label = 'Malicous'
                # Get certs for SSL session (If they exist)
                cert_key = ssl_record['cert_chain_fuids'].split(',')[0]
                certs = None
                if cert_key !=  '-':
                    certs = x509.loc[cert_key]
                # Create the SSL Aggregation
                ssl_agg = [conn_record, ssl_record] if certs is None else [conn_record,ssl_record, certs]
                
                # If the connection is already stored, append the SSL Aggregation. Otherwise, create new entry
                if conn_tuple in aggregate_data:
                    aggregate_data[conn_tuple][1].append(ssl_agg)
                else:
                    # features[conn_tuple] = [0.0 for x in xrange(28)]
                    aggregate_data[conn_tuple] = [[],[ssl_agg], label]
            
                # features[conn_tuple][4] += connection_record[1]['orig_bytes']
                # features[conn_tuple][5] += connection_record[1]['resp_bytes']
                # features[conn_tuple][8] += connection_record[1]['orig_pkts']
                # features[conn_tuple][9] += connection_record[1]['resp_pkts']
        
