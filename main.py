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

    labels = readData('labels.csv',
                                debug = False,
                                label_index = 0,
                                variable_index = (0,0),
                                separator=',',load_all=True)

    mntc = MalNetTraffClass(labels=labels.y, pickle=True)

    training_paths = mntc.constructPaths('TestData/Training/set1', [])
    test_paths = mntc.constructPaths('ISCX/Test', [])

    (tconn, tssl, tx509) = mntc.preProcess(training_paths)
    # (teconn, tessl,tex509) = test.preProcess(test_paths)

    training_features = mntc.constructFeatures(tconn, tssl, tx509, log_dir = training_paths)
    # test_features = test.constructFeatures(teconn, tessl, tex509, log_dir = test_paths)


    training = Training(training_features, x_index=(1,29),y_index=29)
    print training.y
    # test = Test(test_features, x_index=(1,29), y_index=30)
    
if __name__ == "__main__":
    main()