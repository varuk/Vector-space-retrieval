import math
import nltk
import string
from nltk.corpus import stopwords
from pickle import load,loads
from nltk.stem import WordNetLemmatizer
import re
import sys
lemmatizer = WordNetLemmatizer()
punctuations = string.punctuation
punctuations = set(punctuations)
stopwordss = set(stopwords.words("english"))
def prefixsearch(token,lis):
    floor=0
    l=0
    r=len(lis)-1
    while(l<=r):
        mid=int(l+(r-l)/2) 
        if (lis[mid]>token):
            r = mid-1     
        else:
            l = mid+1
            floor = mid            
    i = floor+1
    tokens=[]
    if (lis[floor][:len(token)]==token):
        tokens.append(lis[floor])
    while token == lis[i][:len(token)]:
        tokens.append(lis[i])
        i = i+1     
    return tokens
def getqueries(filename):
    queries = {}
    with open(filename, 'r') as f:
        pattern="<title>(?:(?!<>).)+"
        text = f.read()
        queries = re.findall(pattern, text)
        pattern = "<num>(?:(?!<>).)+"
        qids = re.findall(pattern,text)
        queries = {qids[i][15:]:queries[i][15:] for i in range(len(qids))}
    return queries
def process(query,dictionary,N):
    query = re.sub('[\'\-,\+\;<>/\!\"\(\)\{\}]', ' ',query)
    tokens = query.split()
    tokenstf = {}
    dictionarykeys = sorted(list(dictionary.keys()))
    for token in tokens:
        if (token[len(token)-1]=='.'):
                token=token[:(len(token)-1)]
        if not token in punctuations and not token in stopwordss:
                token = token.lower().strip()
                if token[:2] == "n:":
                    if token[len(token)-1] == '*':
                        Nlist = prefixsearch('p ' + token[1:(len(token)-1)], dictionarykeys)+ prefixsearch('l ' + token[1:(len(token)-1)], dictionarykeys) + prefixsearch('o ' + token[1:(len(token)-1)], dictionarykeys)
                        for t in Nlist:
                            tokenstf[t] = tokenstf.get(t, 0) + 1
                    else:
                        tokenstf['p'+token[1:]] = tokenstf.get('p'+token[1:], 0) + 1
                        tokenstf['l'+token[1:]] = tokenstf.get('l'+token[1:], 0) + 1
                        tokenstf['o'+token[1:]] = tokenstf.get('o'+token[1:], 0) + 1
                elif token[:2] == 'o:':
                    if token[len(token)-1] == '*':
                        Plist =  prefixsearch(token[:(len(token)-1)],dictionarykeys)
                        for t in Plist:
                            tokenstf[t] = tokenstf.get(t, 0) + 1
                    else:
                        tokenstf[token] = tokenstf.get(token,0)+1
                elif token[:2] == 'l:':
                    if token[len(token)-1] == '*':
                        Plist =  prefixsearch(token[:(len(token)-1)],dictionarykeys)
                        for t in Plist:
                            tokenstf[t] = tokenstf.get(t, 0) + 1
                    else:
                        tokenstf[token] = tokenstf.get(token,0)+1
                elif token[:2] == 'o:':
                    if token[len(token)-1] == '*':
                        Plist =  prefixsearch(token[:(len(token)-1)],dictionarykeys)
                        for t in Plist:
                            tokenstf[t] = tokenstf.get(t, 0) + 1
                    else:
                        tokenstf[token] = tokenstf.get(token,0)+1
                else:
                    if token[len(token)-1] == '*':
                        Plist =  prefixsearch(token[:(len(token)-1)],dictionarykeys)
                        for t in Plist:
                            tokenstf[t] = tokenstf.get(t, 0) + 1
                    else:
                        token = lemmatizer.lemmatize(token)
                        tokenstf[token] = tokenstf.get(token, 0) + 1
                                
    return gettfidf(tokenstf, dictionary, N)
def gettfidf(wtokens, dictionary, N):
    sum = 0
    for token in wtokens.keys():
        wtokens[token] = (1+math.log(wtokens.get(token)))*math.log(1+N/dictionary.get(token,(1,1))[0])
        sum = sum + wtokens[token]*wtokens[token]
    for token in wtokens.keys():
        wtokens[token] = wtokens[token]/math.sqrt(sum)
    return wtokens
def vecsearch(Queryfile,resultfile,indexfile,dictfile,k=10):
    N = 80000
    dictionary = {}
    with open(dictfile,'rb')as f:
        dictionary,N = load(f)
    queries = getqueries(Queryfile)
    file = open(resultfile,'w+')
    for qID, query in queries.items():
        
        querytokens = process(query,dictionary,N) 
        ans = {}
        termcount = {}
        with open(indexfile, 'rb') as f:
            for token,tf in querytokens.items():
                if token in dictionary: 
                    offset = dictionary[token][1]
                    f.seek(offset)
                    plist = loads(f.read())
                    for ID , wt in plist.items():
                        termcount[ID] = termcount.get(ID,0)+1
                        ans[ID] = ans.get(ID,0)+ wt*tf
        sorteddocs = sorted(ans.keys(), key=lambda x: (termcount[x], ans[x]),reverse= True) 
        for i in range(k):
                if (i>=len(sorteddocs)):  #not enough answers
                    break
                file.write(str(int(qID)) + " " + 'Q0' + " " + str(sorteddocs[i]) + " " + str(i) + " " + str(float(ans[sorteddocs[i]])) + " " + "STANDARD" + "\n")
    file.close()

        
if __name__=="__main__":
    Queryfile = sys.argv[1]
    resultfile = sys.argv[3]
    indexfile = sys.argv[4]
    dictfile = sys.argv[5]
    k = int(sys.argv[2])
    vecsearch(Queryfile,resultfile,indexfile,dictfile,k)
