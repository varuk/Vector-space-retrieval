import sys
import string
from pickle import load
def printdict(filename):
    with open(filename, 'rb') as file:
        Dict,N = load(file)
        for indexterm,(df,offset) in Dict.items():
            print(str(indexterm) + ":" + str(df) + ":" + str(offset)) 
            
if __name__=="__main__":
    filename = sys.argv[1]
    printdict(filename)

   
