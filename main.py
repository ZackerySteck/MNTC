import sys
from MNTC import MalNetTraffClass
from forest import Forest
from utils import *


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
    # Load Labels
    labels = readData('labels.csv',
                                debug = False,
                                label_index = 0,
                                variable_index = (0,0),
                                separator=',',load_all=True)
    # Initialize mntc
    # labels = set of labels for supervised learning
    # pickle = Boolean; Whether to use pickling
    # maxprocesses = max number of processes to spawn for computing featureset; Default: 10
    mntc = MalNetTraffClass(labels=labels.y, pickle=True)

    # Recursively Constructs path starting with given directory until conn, ssl, and x509 logs are found
    training_paths = mntc.constructPaths('ISCX/Training', [])
    test_paths = mntc.constructPaths('ISCX/Test', [])

    # Parse and preprocess the logs - return all as tuple
    (tconn, tssl, tx509) = mntc.preProcess(training_paths)
    (teconn, tessl,tex509) = test.preProcess(test_paths)
    # Construct features for the training and test sets.
    training_features = mntc.constructFeatures(tconn, tssl, tx509, log_dir = training_paths)
    test_features = test.constructFeatures(teconn, tessl, tex509, log_dir = test_paths)


    training = Training(training_features, x_index=(1,29),y_index=29)
    test = Test(test_features, x_index=(1,29), y_index=29)

if __name__ == "__main__":
    main()
