import scipy.stats
import numpy as np
from node import Node
from utils import *

class Tree:
    def __init__(self, data=None, validate=None, debug=False, mse_threshold = 10, min_size = 1, max_depth=999):
        self.data = data
        self.validate= validate
        self.root = Node(data.x, data.y)
        self.attributes = []
        self.numNodes = 1
        # calc yhat for root
        s = 0.0
        for l in data.y:
            s += l
        self.root.yhat = s/len(data.y)
        print("Root yhat: %0.4f" % (self.root.yhat))
        # Calc inital mses
        self.root.mse = self.calculateMSE(data.y, self.root.yhat)
        self.initial_train_mse = self.root.mse
        self.initial_test_mse = self.calculateMSE(self.validate.y, self.root.yhat)
        print("Root MSE: %0.4f" % (self.root.mse))
        # Set options
        self.debug = debug
        if self.debug:
            self.train_perf = []
            self.test_perf = []
            self.node_perf = []
        self.mse_threshold = mse_threshold
        self.min_size = min_size
        self.max_depth = max_depth
        np.seterr(all='ignore')
        # Split the root to start
        self.split(self.root)
    
    def build(self, node=None, depth=1):
        if node is None:
            node = self.root
        if node.size > self.min_size and depth < self.max_depth and node.mse > self.mse_threshold and node != self.root and np.sum(node.y == node.y[0]) != node.size:
            self.split(node)
        if node.hasChildren():
            self.build(node.children[0], depth+1)
            self.build(node.children[1], depth+1)
        return self

    # def prune(self, node=None):
    #     if node is None:
    #         node = self.root
    #     if node.hasChildren():
    #         c1_purity = self.prune(node.children[0])
    #         c2_purity = self.prune(node.children[1])
    #         print node
    #         score = 0.0
    #         outcomes = np.array(node.y, dtype='int64')
    #         counts = np.bincount(outcomes)
    #         for count in counts:
    #             p = float(count) / len(node.y)
    #             score += p*p

    #         parent_perf = score
    #         child_1 = c1_purity
    #         child_2 = c2_purity
    #         print ("Parent purity: %0.4f" % (parent_perf))
    #         print ("Combine child purity: %0.4f" % (child_1+child_2))
    #         if parent_perf > (child_1+child_2):
    #             node.children = []
    #     else:
    #         outcomes = np.array(node.y, dtype='int64')
    #         counts = np.bincount(outcomes)
    #         score = 0.0
    #         for count in counts:
    #             p = float(count) / len(node.y)
    #             score += p*p
    #         print("Score: %0.4f" % (score))
    #         return score

    def predict(self, dataset=None):
        if dataset is None:
            dataset = self.data
        x = dataset.x
        y = dataset.y
        yhat = []
        for record in x:
            node = self.traverse(self.root, record)
            yhat.append(node.yhat)
        mse = self.calculateMSE(y, yhat, predict=True)
        misclassified = 0.0
        for i in range(0,len(yhat)):
            if yhat[i] != y[i]:
                misclassified += 1.0
        return (yhat, misclassified/len(y), mse)

    def traverse(self, node, record):
        # Traverse tree from node until prediction for record is found
        if node.hasChildren():
            if record[node.splitAttrib] < node.splitValue:
                node = self.traverse(node.getChild(0), record)
            else:
                node = self.traverse(node.getChild(1), record)
        return node

    def test_split(self, index, dataset, labels, value):
        l_data,l_labels, r_data, r_labels = [], [], [], []
        for i in range(0, len(dataset)):
            if dataset[i,index] < value:
                l_data.append(dataset[i,:])
                l_labels.append(labels[i])
            else:
                r_data.append(dataset[i,:])
                r_labels.append(labels[i])
        left, right = Node(l_data, l_labels), Node(r_data, r_labels)
        return left, right

    def split(self, node):
        node.mse = self.calculateMSE(node.y, node.yhat)
        # Find the most closely correlated attribute and split
        bestAttrib, bestScore, splitValue, children = 999, None, None, None
        for attrib in range(0, len(node.x[0, :])):
            value = np.median(node.x[:,attrib])
            potential_children = self.test_split(attrib, node.x, node.y, value) # Children = (left, right)
            if potential_children[0].size <= 0 or potential_children[1].size <= 0:
                continue
            potential_children[0].yhat = self.calc_yhat(potential_children[0])
            potential_children[1].yhat = self.calc_yhat(potential_children[1])
            # To determine the best split, find the set S that maximizes
            # Delta_Error(s,t) = Err(t) - Err(s,t)
            # Where t = node to be split, s = potential child of t in S
            mse = 0.0
            for child in potential_children:
                child.mse = self.calculateMSE(child.y, child.yhat)
                # print("Child mse: %0.4f" % (child.mse))
                mse += child.mse
            if mse < bestScore or bestScore is None:
                bestAttrib, bestScore, splitValue, children = attrib, mse, value, potential_children
            if bestScore < self.mse_threshold:
                break
        if children == None:
            return
        if bestAttrib not in self.attributes:
            self.attributes.append(bestAttrib)
        node.splitValue = splitValue
        node.splitAttrib = bestAttrib
        for child in children:
            node.addChild(child)
            self.numNodes += 1
        if(self.debug):
            (_,_,mse1) = self.predict(self.data)
            (_,_,mse2) = self.predict(self.validate)
            self.train_perf.append(mse1)
            self.test_perf.append(mse2)
            self.node_perf.append(self.numNodes)

    def calculateMSE(self, y, yhat, predict=False):
        sse = 0.0
        n = len(y)
        for error in (y-yhat):
            sse += pow(error, 2)
        ret = sse/n
        if ret < 0:
            raise Exception('MSE cannot be negative.')
        return ret
            
    def printTree(self, node=None):
        if self.root is None:
            print "Error: Cannot display empty tree"
        elif node is None:
            node = self.root
        print '\nDisplaying Tree:\n'
        print 'Root:'
        print '-----'
        print self.root
        
    def calc_yhat(self, node):
        outcomes = np.array(node.y, dtype='int64')
        counts = np.bincount(outcomes)
        return np.argmax(counts)
