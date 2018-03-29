import pandas as pd
import numpy as np
import random
import math
from datetime import datetime

class training:
    def __init__(self, data, x_index=(0,1), y_index=0, size=0):
        self.data = data
        self.x = np.array(data[:,x_index[0]:x_index[1]])
        self.y = np.array(data[:,y_index])
        self.size = size

class test:
    def __init__(self, data, x_index=(0,1), y_index=0, size=0):
        self.data = data
        self.x = np.array(data[:,x_index[0]:x_index[1]])
        self.y = np.array(data[:,y_index])
        self.size = size

def readData(filename, debug, label_index, variable_index, separator = ',', load_all=False):
    if debug:
        print("\n\nReading data from %s" % (filename))
    df = pd.read_csv(filename, header=None, sep=separator)
    data = df.as_matrix()
    if(load_all):
        return training(data,
                            x_index = variable_index,
                            y_index = label_index,
                            size = len(data))
    if debug:
        print("Data imported!")
        print('-'*40)
    atom_size = test_size = len(data)/3.0
    training_size = int(math.ceil(atom_size*2))
    atom_size = test_size = int(math.floor(atom_size))
    if debug:
        print("Data size: %d" % (len(data)))
    random.seed(datetime.now())
    training_set = None
    ix = []

    if debug:
        ix = [i for i in range(training_size)]
        training_set = training(np.array(data[0:training_size,:]),
                            x_index = variable_index,
                            y_index = label_index,
                            size = training_size)
    else:
        ix = random.sample(range(len(data)), training_size)
        training_set = training(np.array(random.sample(data, training_size)),
                            x_index = variable_index,
                            y_index = label_index,
                            size = training_size)

    test_set = test(np.delete(data, ix, axis=0),
                    x_index = variable_index,
                    y_index = label_index,
                    size = test_size)
    if debug:
        print("Data set size: %d x %d" % (data.shape[0],data.shape[1]))
        print("Training set size: %d x %d" % (training_set.data.shape[0],training_set.data.shape[1]))
        print("Test set size: %d x %d" % (test_set.data.shape[0],test_set.data.shape[1]))
        print("_"*40)
    return (data, training_set, test_set)

def getLabels(superset_attribs, superset_labels, subset_attribs):
    index = []
    for x in subset_attribs:
        index.append(np.where(superset_attribs == x[0])[0][0])

    subset_labels = superset_labels[index]
    return subset_labels