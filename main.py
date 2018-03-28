from utils import *
from tree import *
import matplotlib.pyplot as plt
import sys

# row[0] = ID
# row[1] = Class
# row[2] = Time
# row[3:33] = Attribs

def main():
    debug = False
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == '-d':
            debug = True
        elif sys.argv[i] == '-t':
            threshold = sys.argv[i+1]
        elif sys.argv[i] == '-h':
            print "Usage: python main.py [OPTIONS]\n"
            print "--------- Options -------------"
            print "'-d' : debug mode"
            print "'-t [VALUE]' : set mean square error threshold to value"
            return
    (data, training_set, test_set) = readData("whitewine.csv",
                                            debug,
                                            label_index=11,
                                            variable_index=(0,10),
                                            separator=';')

    tree = Tree(data=training_set,
                validate=test_set,
                debug=True,
                mse_threshold=0.02,
                min_size=1,
                max_depth=15)

    # tree.printTree()
    tree.build()
    print tree.numNodes
    (training_prediction, training_error, training_mse) = tree.predict(training_set)
    (test_prediction, test_error, test_mse) = tree.predict(test_set)
    tree.printTree()

    print tree.numNodes

    print("Initial training MSE = %0.4f" % (tree.initial_train_mse))
    print("Initial test MSE = %0.4f" % (tree.initial_test_mse))
    print("Training prediction completed with MSE = %0.4f" % (training_mse))
    print("Test prediction completed with MSE = %0.4f\n" % (test_mse))
    # print'Training predictions vs actual'
    # print zip(training_prediction, training_set.y)
    # print('Test predictions vs actual:')
    # print zip(test_prediction, test_set.y)

    train, = plt.plot(tree.node_perf, tree.train_perf,'k',label='Training')
    test, = plt.plot(tree.node_perf, tree.test_perf, 'r--',label='Test')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Mean Square Error')
    plt.legend(handles=[train,test])
    plt.title('White Wine Regression Tree')
    plt.show()
    
    print "Attributes used for prediction:"
    print tree.attributes
if __name__ == "__main__":
    main()