import re
import xml.etree.cElementTree as ET
from pickle import HIGHEST_PROTOCOL,dump,load,dumps,loads
import math
from os import listdir
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys
lemmatizer = WordNetLemmatizer()
punctuations = string.punctuation
punctuations = set(punctuations)
stopwordss = set(stopwords.words("english"))
def readdata(path):
    Alldata = []
    N = 0
    files = listdir(path)
    for file in files:
        with open(path+'/'+file) as inputfile:
            File = inputfile.read()
            File = '<root>'+ File + '</root>'
            File = re.sub("[`&\"\']+", '', File)        
            root = ET.fromstringlist(File)
            Docs = root.getchildren()
            for Doc in Docs:
                ID = Doc.find('DOCNO').text
                data = ET.tostring(Doc.find('TEXT'))
                if (len(data.split())<=2):
                    continue
                Alldata.append((ID,data))
                N = N +1 
    return Alldata, N
def getindex(Alldata):
    Dict = {}
    for data in Alldata:
        dat= re.sub("(</PERSON>\s*<PERSON>)|(</LOCATION>\s*<LOCATION>)|(</ORGANIZATION>\s*<ORGANIZATION>)", ' ', data[1].decode("utf-8"))
        Entitylist = re.findall('<PERSON>[\w\s]*</PERSON>|<LOCATION>[\w\s]*</LOCATION>|<ORGANIZATION>[\w\s]*</ORGANIZATION>', dat)
        EL = []
        for E in Entitylist:
            L = E.split()
            idt = L[0][1]
            L.pop(0)
            L.pop(len(L)-1)
            if len(L)>1:
                entity = ""
                for l in L:
                    EL.append(idt+":"+l)
                    entity = entity+l+" "
                entity = idt+":"+entity
                EL.append(entity)
            else:
                EL.append(idt+":"+L[0])
        dat = re.sub("<[/]*\w+>",' ', dat) 
        dat = re.sub("[\-\+\\\?\;\:\*\_!,]+",' ',dat)
        tokens = dat.split()
        tokens = tokens + EL
        tokens = Normalize(tokens)
        tokens = Termfreq(tokens)
        Dict[data[0]] = tokens
    return Dict
def Normalize(tokens):
    processed_tokens = []
    for token in tokens:
        if not re.search('[0-9]+|[\.]{2,}',token) and not token in punctuations and not token in stopwordss:
            token = token.lower().strip()
            if(token[len(token)-1] == '.'):
                token = token[:(len(token)-1)]
            if  len(token)>1 and token[1] != ':' :
                token = lemmatizer.lemmatize(token)   
            processed_tokens.append(token)
    return processed_tokens
def Termfreq(tokens):
    tf = {}
    for token in tokens:
        tf[token]  = tf.get(token,0)+1
    return tf
def invertedindex(Dictionary,N,indexfile):
    Dict = {}
    for ID,TD in Dictionary.items():  
        for term,tf in TD.items():
            if term in Dict:
                Dict[term][ID] = 1+math.log(tf)
            else:
                Dict[term] = {ID:1 +math.log(tf)}
    sum = {}           
    for ID , TD in Dictionary.items():
        for term,tf in TD.items():
            Dict[term][ID] = Dict[term][ID]*math.log(1+(N/len(Dict[term].keys())))
            sum[ID] = sum.get(ID,0)+Dict[term][ID]*Dict[term][ID]  
    Sterms = sorted(Dict.keys())
   
    dic = {}
    with open (indexfile +'.idx','wb') as newf:
        for term in Sterms:
            postings = Dict[term]
            df = len(postings.keys())
            for ID ,wt in postings.items():
               
                postings[ID] = wt/(math.sqrt(sum[ID]))
            off = newf.tell()
            data = dumps(postings)
            newf.write(data) 
            dic[term] = ((df,off))
    with open(indexfile + ".dict",'wb') as Dfile:
        dump((dic,N),Dfile,HIGHEST_PROTOCOL)    
def main(path,indexfile):
    Alldata,N = readdata(path)
    Index = getindex(Alldata)
    invertedindex(Index,N, indexfile)
if __name__=="__main__":
    path = sys.argv[1]
    indexfile = sys.argv[2]
    main(path,indexfile)


