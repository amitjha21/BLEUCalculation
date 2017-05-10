## BLEU; Spring 2017
## Author : Amit Jha; amitjha@usc.edu
##
import sys
import math
import codecs
import os

def read_file(filename):
    dataSet = []
    c = 1
    f = codecs.open(filename, encoding='utf-8')
    for line in f:
        data = line.strip()
        #data = data.replace(':','')
        #data = data.replace('.', '')
        #data = data.replace('?', '')
        #data = data.replace('-', '')
        #data = data.replace(',', '')
        dataSet.append(data)
        #c+=1
    f.close()
    return dataSet
def write_output(sc):
    f = codecs.open('bleu_out.txt','w+')
    f.write(str(sc))
    f.close()
def create2dList(width,height):
    w, h = width, height
    twoDList = [[0 for x in range(w)] for y in range(h)]
    return twoDList

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def createCanNgram(candidateFile,N):
    canNGramList = []
    for line in candidateFile:
        lineN = line.split(' ')
        ngList = []
        #list(filter(lambda a: a != '', lineN))
       # lineN = list(filter((' ').__ne__, lineN))
        lineN = remove_values_from_list(lineN,'')
        lineNLen = len(lineN)
        if N==1:
            canNGramList.append(lineN)
            continue
        elif N==2:
            for l in range(0,lineNLen-1):
                ngList.append(lineN[l]+' '+lineN[l+1])

        elif N==3:
            for l in range(0,lineNLen-2):
                ngList.append(lineN[l] + ' ' + lineN[l + 1]+' '+lineN[l+2])
        elif N==4:
            for l in range(0,lineNLen-3):
                ngList.append(lineN[l] + ' ' + lineN[l + 1]+' '+lineN[l+2]+' '+lineN[l+3])
        else:
            return canNGramList
        canNGramList.append(ngList)
    return canNGramList

def createRefNgram(refMatrixp,N,nref,ncanl):
    refMatrixGram = create2dList(nref, ncanl)
    for i in range(0, len(refMatrixp)):
        for j in range(0, len(refMatrixp[i])):
            line = refMatrixp[i][j].split(' ')

            ngList = []

            lineN = remove_values_from_list(line, '')
            lineNLen = len(lineN)
            if N == 1:
                refMatrixGram[i][j] = lineN
                continue
            elif N == 2:
                for l in range(0, lineNLen - 1):
                    ngList.append(lineN[l] + ' ' + lineN[l + 1])

            elif N == 3:
                for l in range(0, lineNLen - 2):
                    ngList.append(lineN[l] + ' ' + lineN[l + 1] + ' ' + lineN[l + 2])
            elif N == 4:
                for l in range(0, lineNLen - 3):
                    ngList.append(lineN[l] + ' ' + lineN[l + 1] + ' ' + lineN[l + 2] + ' ' + lineN[l + 3])
            else:
                return refMatrixGram
            refMatrixGram[i][j] = ngList
    return refMatrixGram


if __name__ == "__main__":
    #if len(sys.argv)<3:
    #    print("Parameters missing")
    #    exit(1)
    refFileList = []
    candidate_file = []
    temprefdict = []
    reference_files = {}
    candidate_sent_len = []
    best_match_len = []
    r_parameter = 0
    c_parameter = 0
    BP_parameter = 0
    precision = {}
    totalNG = 4
    bscore = 0.0
    #canFN = sys.argv[1]
    #refFN = sys.argv[2]
    canFN = 'candidate-3.txt'
    refFN =  'reference-3.txt'#'engRef/'

    if os.path.isdir(refFN):
        refFileList = os.listdir(refFN)
        for i,k in enumerate(refFileList):
            refFileList[i] = refFN+refFileList[i]
    else:
        refFileList.append(refFN)

    candidate_file = read_file(canFN)
    no_of_can_line = len(candidate_file)
    no_of_ref_file = len(refFileList)
    refMatrix = create2dList(no_of_ref_file,no_of_can_line)
    for i in range(0,no_of_ref_file):
        temprefdict = read_file(refFileList[i])
        for t in range(0,len(temprefdict)):
            refMatrix[t][i] = temprefdict[t]

    #can len
    for b in candidate_file:
        btest = b.split(' ')
        spcount = btest.count('')
        candidate_sent_len.append(len(btest)-spcount)
    #ref len
    ref_sen_len = create2dList(no_of_ref_file, no_of_can_line)
    for i in range(0, no_of_can_line):
        for t in range(0, len(refMatrix[i])):
            ttest = refMatrix[i][t].split(' ')
            spcount = ttest.count('')
            ref_sen_len[i][t] = len(ttest)-spcount

    #best_match_len
    for a,b in enumerate(candidate_sent_len):
        minv = float('Inf')
        bml = b
        for noRef in ref_sen_len[a]:

            if minv> abs(b-noRef):
                bml = noRef
                minv = abs(b-noRef)

        best_match_len.append(bml)
    r_parameter = sum(best_match_len)
    c_parameter = sum(candidate_sent_len)
    if c_parameter > r_parameter:
        BP_parameter = 1
    else:
        BP_parameter = math.exp(1-(r_parameter/c_parameter))


    #clipcount
    for ng in range(1,totalNG+1):
        clipCountDictTemp = {}
        canNG = createCanNgram(candidate_file,ng)

        refNG = createRefNgram(refMatrix,ng,no_of_ref_file,no_of_can_line)
        candidateNGramLen = 0
        totalClipCount = 0
        for canIdx, canLine in enumerate(canNG):
            candidateNGramLen+=len(canLine)
            totalClipCountTemp = 0
            for canWord in canLine:
                canWordCount = 0
                clipCount = 0
                if canWord not in clipCountDictTemp.keys():
                    canWordCount = canLine.count(canWord)
                    maxRefCount = 0
                    for refCol in range(0,len(refNG[canIdx])):
                        refLine = refNG[canIdx][refCol]
                        refWordCount = refLine.count(canWord)
                        maxRefCount = max(maxRefCount,refWordCount)
                    clipCount = min(canWordCount,maxRefCount)
                    clipCountDictTemp[canWord] = clipCount
            totalClipCountTemp = sum(clipCountDictTemp.values())
            clipCountDictTemp = {}
            totalClipCount += totalClipCountTemp
        if candidateNGramLen <= 0:
            continue
        precision[ng] =  totalClipCount / candidateNGramLen
        #print('P('+str(ng)+') = '+str(totalClipCount)+' / '+str(candidateNGramLen) + ' = '+ str(precision[ng]))

    #calculate BLEU
    W = 0.25#0.575646273248 #0822
    pSum = 0.0
    prod = 0.0
    logVal = 0.0
    ns = 1
    for key,val in precision.items():
        ns*=val
        if val>0:
            #print(val)
            logVal = (math.log(val))
        else:
            logVal = 0.0
        pSum+=logVal
    prod = W * pSum
    bscore = BP_parameter * (math.exp(prod))
    bscore = round(bscore, 12)
    write_output(bscore)
    newB = BP_parameter*math.pow((precision[1]*precision[2]*precision[3]*precision[4]),0.25)
    newB = round(newB,13)
    print('BP: '+str(BP_parameter))
    print('BLEU: '+str(bscore))
    print('BLEU: '+str(newB))



