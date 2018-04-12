# from forest import Forest
import sys
from MNTC import MalNetTraffClass
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
                                debug = False,
                                label_index = 0,
                                variable_index = (0,0),
                                separator=',',load_all=True)
                                
    # mntc = MNTC(['TestData'], training.y)
    test = MalNetTraffClass(['TestData'], training.y, pickle=True)
    test.preProcess()

    
if __name__ == "__main__":
    main()