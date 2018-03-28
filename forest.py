from tree import Tree

class Forest:
    def __init__(self,data=None, validate=None, debug=False, mse_threshold = 10, min_size = 1, max_depth=999, num_trees=5):
        self.forest = []
        self.data = data
        self.validate = validate
        self.debug = debug
        self.mse_threshold = mse_threshold
        self.min_size = min_size
        self.max_depth = max_depth
        self.num_trees = num_trees
    
    def build(self):
        for i in range(self.num_trees):
            self.forest.append(
                Tree(
                    data = self.data,
                    validate= self.validate,
                    debug = self.debug,
                    mse_threshold = self.mse_threshold,
                    min_size= self.min_size,
                    max_depth= self.max_depth
                ))

    def predict(self, dataset = None):
        predictions = [] # List of tuples in form (yhat, misclassified, error)
        for tree in self.forest:
            predictions.append(tree.predict(dataset))
        return predictions