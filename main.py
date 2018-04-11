# from forest import Forest
import sys
# from MNTC import MNTC
from test import TEST
# from forest import Forest
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

    training = readData('labels.csv',
                                debug = True,
                                label_index = 0,
                                variable_index = (0,0),
                                separator=',',load_all=True)
                                
    # mntc = MNTC(['Data'], training.y)
    test = TEST(['Data'], training.y)
    test.preProcess()

    
if __name__ == "__main__":
    main()