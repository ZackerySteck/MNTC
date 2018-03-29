from tree import Tree
from utils import *
import numpy as np

class Forest:
    def __init__(self,filename = None, label_index = None, variable_index = (0,0), separator=',', mse_threshold = 10, debug=False,  min_size = 1, max_depth=999, num_trees=5):
        self.forest = []
        self.filename = filename
        self.label_index = label_index
        self.variable_index = variable_index
        self.separator = separator
        self.mse_threshold = mse_threshold
        self.debug = debug
        self.min_size = min_size
        self.max_depth = max_depth
        self.num_trees = num_trees
    
    def build(self):
        for i in range(self.num_trees):
            print('Building Tree %d' % (i))
            (data, training, test) = readData(
                filename = self.filename,
                debug = self.debug,
                label_index = self.label_index,
                variable_index = self.variable_index,
                separator= self.separator)
            self.forest.append(
                Tree(
                    data = training,
                    validate= test,
                    debug = self.debug,
                    mse_threshold = self.mse_threshold,
                    min_size= self.min_size,
                    max_depth= self.max_depth
                ).build())
            print '-'*20

    def predict(self, dataset = None):
        if dataset is None:
            return -1
        predictions = [] # List of tuples in form (yhat, misclassified, error)
        for tree in self.forest:
            predictions.append(tree.predict(dataset))
        # print predictions
        best = np.zeros(dataset.size)
        for i in range(dataset.size):
            votes = np.zeros(self.num_trees)
            t = 0
            for yhat, _, _ in predictions:
                votes[t] = yhat[t]
                t += 1
            best[i] = self.getBest(votes)
        return (best, self.calculateMSE(dataset.y, best))

    def getBest(self, votes):
        print votes
        outcomes = np.array(votes, dtype='int64')
        counts = np.bincount(outcomes)

        return np.argmax(counts)

    def calculateMSE(self, y, yhat):
        sse = 0.0
        n = len(y)
        for error in (y-yhat):
            sse += pow(error, 2)
        ret = sse/n
        if ret < 0:
            raise Exception('MSE cannot be negative.')
        return ret