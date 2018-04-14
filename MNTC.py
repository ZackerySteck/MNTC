import pandas as pd
import cPickle as pickle
from utils import *
import datetime, time, os, math
import multiprocessing as mp

class MalNetTraffClass:
    def __init__(self,labels = None, debug = False, pickle = False, processcount=10):
        # self.log_dir = log_dir
        self.debug = debug
        self.labels = labels
        self.pickle = pickle
        self.processcount = processcount
        self.aggregate_data = {}
        # if log_dir is not None:
        #     self.constructPaths(log_dir)
        #     if self.pickle:
        #         if os.path.isfile('./pickle/'+log_dir.replace('/','%')+str(hash(log_dir))+'cmpl.pkl'):
        #             print 'Pickle of final feature set found. Loading...'
        #             self.features = self.loadPickle('./pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'cmpl.pkl')
                    

    # Recursively construct directory strings from root until files are found
    def constructPaths(self, log_dir = None, arr = []):
        search = ['conn.log', 'ssl.log', 'x509.log']
        if type(log_dir) is str:
            if os.path.isdir(log_dir):
                dir_contents = [name for name in os.listdir(log_dir)]
                for obj in dir_contents:
                    self.constructPaths(log_dir + '/'+obj, arr)
            else:
                for item in search:
                    if item in log_dir:
                        arr.append(log_dir)
                        return arr
        else:
            for item in log_dir:
                if os.path.isdir(item):
                    sub_dirs = [name for name in os.listdir(item)]
                    for obj in sub_dirs:
                        return self.constructPaths(item+'/'+obj, arr)
        return arr
    
    def parseLog(self, log, cols, skiprows, names):
        if self.pickle and os.path.isfile('./pickle/'+log.replace('/','%')+'.pkl'):
                pickle = './pickle/'+log.replace('/','%')+'.pkl'
                print 'Pickle found for %s! Loading.' % (bcolors.UNDERLINE+log+bcolors.ENDC)
                return pd.read_pickle(pickle)
        print('Processing %s' % (bcolors.UNDERLINE+log+bcolors.ENDC))
        return pd.read_csv(log,delimiter='\t',
                header=6,skiprows=skiprows,
                names = names,index_col=None,
                usecols=cols,na_values='-',
                low_memory=False).head(-1)

    def preProcess(self, log_path = None):
        print bcolors.WARNING+"Loading log files. This can take a some time depending on file size."+bcolors.ENDC
        print '-'*40
        sstart = time.time()
        conn, ssl, x509 = None,None,None
        if log_path is None:
            return
        for log in log_path:
            current = None
            start = time.time()
            if 'conn.log' in log:
                conn = self.parseLog(log, [0,1,2,4,5,7,8,9,10,16,18], [7, -1],['ts', 'uid', 'id.orig_h','id.resp_h','id.resp_p','service',
                                'duration','orig_bytes','resp_bytes','orig_pkts','resp_pkts'])      
                # Pandas type inference incorrect for columns the Bro uses '-' as 'NaN' - convert to correct dtype  
                conn.fillna({'ts':0, 'id.resp_p':0,'duration':0,'orig_bytes':0,'resp_bytes':0,'orig_pkts':0,'resp_pkts':0}, inplace=True)
                current = conn
            elif 'ssl.log' in log:
                ssl = self.parseLog(log, [0,1,2,4,5,6,9,14], [7, -1], ['ts', 'uid', 'id.orig_h','id.resp_h','id.resp_p','version','server_name','cert_chain_fuids'])
                # ssl.update(ssl[['uid','id.orig_h','id.resp_h','version','cert_chain_fuids']].fillna('-',inplace=True))
                ssl.fillna({'ts':0, 'id.resp_p':0,'cert_chain_fuids':'-','server_name':'-'}, inplace=True)
                current = ssl
            else:
                x509 = self.parseLog(log, range(20), [7, -1],['ts','id','certificate.version',
                               'certificate.serial','certificate.subject',
                               'certificate.issuer','certificate.not_valid_before',
                               'certificate.not_valid_after','certificate.key_alg',
                               'certificate.sig_alg','certificate.key_type',
                               'certificate.key_length','certificate.exponent',
                               'certificate.curve','san.dns','san.uri','san.email','san.ip',
                               'basic_constraints.ca','basic_constraints.path_len'])
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
            print (bcolors.OKBLUE + 'Log preprocessing completed in %0.4f seconds.' % (time.time() - sstart))
            print bcolors.ENDC
        return (conn, ssl, x509)

    def constructFeatures(self,conn=None,ssl=None,x509=None, log_dir = None):
        if log_dir is None or conn is None or ssl is None or x509 is None:
            print bcolors.FAIL + 'Error: constructFeatures misuse. Correct usage: constructFeatures(conn, ssl, x509, log_path)' + bcolors.ENDC
            return
        conn.set_index('uid', inplace=True)
        ssl.set_index('uid', inplace=True)
        x509.set_index('id', inplace=True)
        print bcolors.WARNING+'Calculating feature set. This can take some time depending on file size.'+bcolors.ENDC
        self.aggregate_data = {}
        if os.path.isfile('./pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int2.pkl'):
            print 'Intermediate file found for interval 2. Loading...'
            aggregate_data = self.loadPickle('./pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int2.pkl')
            del conn
            del ssl
            del x509
            return self.finalizeFeatures(aggregate_data)
        if conn is None or ssl is None or x509 is None:
            return
        if os.path.isfile('./pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int1.pkl'):
            print 'Intermediate file found for interval 1. Loading...'
            aggregate_data = self.loadPickle('./pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int1.pkl')
            aggregate_data = self.intermediate2(conn, ssl,log_dir)
            del conn
            del ssl
            del x509
            return self.finalizeFeatures(aggregate_data)
        self.intermediate1(conn,ssl,x509, log_dir)
        self.intermediate2(conn,ssl,log_dir)
        return self.finalizeFeatures()
        
    
    def savePickle(self, obj, path):
        start = time.time()
        with open(path, 'wb') as fp:
            pickle.dump(obj,fp)
            print 'Pickled in %0.4f seconds' % (time.time() - start)

    def loadPickle(self, path):
        with open(path, 'rb') as fp:
            return pickle.load(fp)


    def intermediate1(self,conn,ssl,x509, log_dir):
        ids = []
        start = time.time()
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
                if conn_tuple in self.aggregate_data:
                    self.aggregate_data[conn_tuple][1][id] = ssl_agg
                else:
                    self.aggregate_data[conn_tuple] = [{},{id:ssl_agg},[0 for x in xrange(28)], label]

                self.aggregate_data[conn_tuple][2][4] += conn_record['orig_bytes']
                self.aggregate_data[conn_tuple][2][5] += conn_record['resp_bytes']
                self.aggregate_data[conn_tuple][2][8] += conn_record['orig_pkts']
                self.aggregate_data[conn_tuple][2][9] += conn_record['resp_pkts']
                ids.append(id)   

        print('Obtained HTTPS records in %0.4f seconds' % (time.time()-start))
        start = time.time()
        print('Dropping %d used connection records...' % (len(ids)))
        conn.drop(ids, inplace=True)
        del ids
        print('Used connection records dropped in %0.4f seconds' % (time.time()-start))
        
        if self.pickle:
            print 'Saving intermediate feature set... (int 1)'
            self.savePickle(self.aggregate_data, './pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int1.pkl')

    def intermediate2(self, conn, ssl, log_dir):
        print 'Checking for dangling connection records...'        
        stime = time.time() 
        # Break the connection records into batches and distribute among worker processes
        total = conn.shape[0]
        batch_size = (total+self.processcount-1) / self.processcount
        jobs = []
        out_q = mp.Queue()
        for i in range(self.processcount):
            start = i*batch_size
            end = (start + batch_size) if (start + batch_size) < total else total

            print ('Creating process %d with range: %d -> %d' % (i,start,end))
            batch = conn.iloc[range(start, end)]
            p = mp.Process(target=self.dangleCheck, args=(batch, start, end, i, out_q))
            jobs.append(p)
            p.start()

        # collect process return values
        resultdict = {}
        for i in range(self.processcount):
            resultdict.update(out_q.get())
        for j in jobs:
            j.join()

        print('All processes returned in %0.4f seconds' % (time.time() - stime))
        print len(resultdict)
        print resultdict
        return

        if self.pickle:
            print 'Saving intermediate feature set... (int 2)'
            self.savePickle(self.aggregate_data, './pickle/'+log_dir[0].replace('/','%')+str(hash(log_dir[0]))+'int2.pkl')

    def dangleCheck(self,conn, start, end, tid, out_q):
        stime = time.time()
        ids = list(conn.index)
        records = {}
        for id in ids:
            record = conn.loc[id]
            conn_tuple = (record['id.orig_h'], record['id.resp_h'], record['id.resp_p'],record['service'])
            if conn_tuple in self.aggregate_data and id not in self.aggregate_data[conn_tuple][1]:
                print '%d adding to conn_tuple' %(tid)
                if conn_tuple not in records:
                    records[conn_tuple] = {'records':{}, '4':0,'5':0,'8':0,'9':0}
                records[conn_tuple]['records'][id] = record
                records[conn_tuple]['4'] += record['orig_bytes']
                records[conn_tuple]['5'] += record['resp_bytes']
                records[conn_tuple]['8'] += record['orig_pkts']
                records[conn_tuple]['9'] += record['resp_pkts']
        elapsed = time.time() - stime
        print('Process %d completed in %0.4f seconds' % (tid, elapsed))
        print records
        ret = {tid:records}
        out_q.put(ret)

    def finalizeFeatures(self, aggregate_data):
        for id,record in aggregate_data.items():
            conn_agg = record[0]
            ssl_aggs = record[1]
            label = record[3]

            ssl_conn_records = [item[0] for key,item in ssl_aggs.items()]
            conn_records = [item for key,item in conn_agg.items()]

            combined = conn_records + ssl_conn_records
            combined.sort(key=lambda r: r['ts'])

            durations = [x['duration'] for x in combined]
            durations_squared = [pow(x['duration'], 2) for x in combined]

            # ---------------- Calculate Connection Features --------------------------
            self.aggregate_data[id][2][0] = len(combined)
            if len(conn_records) > 0:
                self.aggregate_data[id][2][1] = mean(durations)
                self.aggregate_data[id][2][2] = pow( mean(durations_squared) - pow(self.aggregate_data[id][2][2], 2), 0.5)

                lb = self.aggregate_data[id][2][1] - self.aggregate_data[id][2][2]
                ub = self.aggregate_data[id][2][1] + self.aggregate_data[id][2][2] 

                self.aggregate_data[id][2][3] = len([x for x in conn_records if (x['duration'] < lb or x['duration'] > ub)]) / float(len(durations))
                self.aggregate_data[id][2][6] = self.aggregate_data[id][2][5] / (self.aggregate_data[id][2][5] + aggregate_data[id][2][4])

                e_states = ['SF', 'S1', 'S2', 'S3', 'RSTO', 'RSTR']
                # non_e_states = ['OTH', 'SO', 'REJ', 'SH', 'SHR', 'RSTOS0', 'RSTRH']
                e = len([x for x in combined if (x['conn_state'] in e_states)])
                n = len(combined) - e

                aggregate_data[id][2][7] = e / (e+n)

                ts = [x['ts'] for x in combined]
                interval_1 = []
                periodicity = []
                for i in range(len(ts)-1):
                    t1 = ts[i]
                    t2 = ts[i+1]
                    interval_1.append((t2 - t1))
                for i in range(len(interval_1)-1):
                    p1 = interval_1[i]
                    p2 = interval_1[i+1]
                    periodicity.append(abs(p2-p1))
                aggregate_data[id][2][10] = mean(periodicity)

                periodicity_squared = [pow(x,2) for x in periodicity]
                aggregate_data[id][2][11] = pow( mean(periodicity_squared) - pow(aggregate_data[id][2][10], 2), 0.5)

            # ------------------ Calculate SSL Features ----------------------------
            aggregate_data[id][2][13] = len(conn_records) / len(ssl_aggs)

            num_tls = len([x[1] for x in [item for key,item in ssl_aggs.items()] if 'TLS' in x[1]['version']])
            aggregate_data[id][2][14] = num_tls / (num_tls+len(ssl_aggs))
            num_no_sni = len([x[1] for x in [item for key,item in ssl_aggs.items()] if '-' in x[1]['server_name']])
        # self.features = aggregate_data
        # print len(aggregate_data)
        return aggregate_data

def mean(L):
    return 0 if len(L) == 0 else sum(L) / len(L)