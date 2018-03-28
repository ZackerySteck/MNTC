import numpy as np

class Node:
    def __init__(self, data=None, y=None):
        self.x = np.array(data)
        self.y = np.array(y)
        self.yhat = None
        self.splitAttrib = None
        self.splitValue = None
        self.mse = None
        self.children = []
        self.size = len(self.y)
        self.gini = 0.0

    def addChild(self, n):
        if len(self.children) < 2:
            self.children.append(n)
        else:
            # Throw - Node can only have 2 children
            raise Exception("Attempt to add child to node with 2 children.")
    
    def getChild(self, index):
        if index < 2:
            return self.children[index]
        else:
            raise Exception('Cannot index empty child list.')

    def hasChildren(self):
        return True if (len(self.children) > 0) else False
    
    def getMSE(self):
        return self.mse

    def __str__(self, level = 0): # Depth first print
        ret = '\t'*level
        if self.hasChildren():
            ret += '[Split: x'+repr(self.splitAttrib)+', '+repr(self.splitValue)+']\n'
        else:
            ret +='[MSE: '+repr(self.mse)+' | yhat: '+repr(self.yhat)+' | # Records: '+repr(self.size)+']\n'
        for child in self.children:
            ret += child.__str__(level+1)
        return ret
    
    def __repr__(self):
        return '<tree node representation>'
