# from forest import Forest
import matplotlib.pyplot as plt
import sys
from MNTC import MNTC
from forest import Forest
from utils import *
import matplotlib.pyplot as plt


def main():
    debug = False
    threshold = 1
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

    # mntc = MNTC(['Data'])
    (data, training, test) = readData(
                filename = 'whitewine.csv',
                debug = False,
                label_index = 11,
                variable_index = (0,10),
                separator= ';')

    forest = Forest(filename = 'whitewine.csv',
                    label_index = 11,
                    variable_index = (0,10),
                    separator=';',
                    mse_threshold= 0.02,
                    debug = debug)
    forest.build()

    # print test.y
    # forest.forest[0].printTree()
    best = forest.predict(test)
    print best
    # train0, = plt.plot(forest.forest[0].node_perf, forest.forest[0].train_perf,'k',label='Tree 1 - Training')
    # test0, = plt.plot(forest.forest[0].node_perf, forest.forest[0].test_perf, 'k--',label='Test 1 - Test')
    # train1, = plt.plot(forest.forest[1].node_perf, forest.forest[1].train_perf,'r',label='Tree 2 - Training')
    # test1, = plt.plot(forest.forest[1].node_perf, forest.forest[1].test_perf, 'r--',label='Test 2 - Test')
    # train2, = plt.plot(forest.forest[2].node_perf, forest.forest[2].train_perf,'g',label='Tree 3 - Training')
    # test2, = plt.plot(forest.forest[2].node_perf, forest.forest[2].test_perf, 'g--',label='Test 3 - Test')
    # train3, = plt.plot(forest.forest[3].node_perf, forest.forest[3].train_perf,'y',label='Tree 4 - Training')
    # test3, = plt.plot(forest.forest[3].node_perf, forest.forest[3].test_perf, 'y--',label='Test 4 - Test')
    # train4, = plt.plot(forest.forest[4].node_perf, forest.forest[4].train_perf,'b',label='Tree 5 - Training')
    # test4, = plt.plot(forest.forest[4].node_perf, forest.forest[4].test_perf, 'b--',label='Test 5 - Test')
    # plt.xlabel('Number of Nodes')
    # plt.ylabel('Mean Square Error')
    # plt.legend(handles=[train0,test0,train1,test1,train2,test2,train3,test3,train4,test4])
    # plt.title('White Wine Regression Tree')
    # plt.show()
if __name__ == "__main__":
    main()