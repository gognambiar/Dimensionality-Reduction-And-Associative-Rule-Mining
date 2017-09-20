import numpy, os, sys, getopt, itertools as it
import re

confidence = 70
# support = .30 #40, 50, 60, 70
FSet={}
F1Set = {}
main_data = {}
rule=[]
head=[]
tail=[]
conf=[]
supp=[]

def readFile(fileName):
    data = open(fileName).read().split("\n")[:-1]
    data = [i.replace("\r","").split("\t") for i in data]
    for i in xrange(len(data)):
        for j in xrange(len(data[i])-1):
            data[i][j] = "G%s_%s" % (str(j+1),data[i][j])
            if data[i][j] in F1Set:
                F1Set[data[i][j]] += 1
            else:
                F1Set[data[i][j]] = 1

    # print F1Set
    return data

def getFrequentItemSets(data):
    # print(len(data))
    for key, value in F1Set.items():
        if ((value*100)/float(len(data))) < support*100 :
            F1Set.pop(key, None)
        else:
            # print key,value,(value/float(len(data))),(value/float(len(data))) < support,support
            main_data[frozenset([key])] = value
            FSet[key] = value

def getSupport(data, items):
    count=0
    for row in data:
        flag=True
        for i in items:  
            if i not in row:
                flag= False
                break
        if flag is True: 
            count+=1
    return count


def joinItemSets(data):
    global FSet
    # itemList=list(sorted(FSet.keys(), key = lambda x: int("".join(re.findall("\d+",x)))))
    # item1List=list(sorted(F1Set.keys(), key = lambda x: int("".join(re.findall("\d+",x)))))
    itemList = list(FSet.keys())
    item1List = list(F1Set.keys())

    # print len(itemList)
    FSet = {}
    items=[]
    # for item in list(it.combinations(itemList,2)):
    for item in itemList:
        # end_num = re.findall("\d+",item)[-1]
        end_num = 0
        for elem in item1List[(2*int(end_num)):]:
        # if ",".join(item[0].split(",")[:-1]) == ",".join(item[1].split(",")[:-1]):
            item_str=",".join([item,elem])
            order = [int(i) for i in re.findall("\d+",item_str)]
            # if order != sorted(order) or len(set(order)) != len(order):
            if len(set(order)) != len(order):
                continue
            # print item_str,order
            items=item_str.split(",")
            count = getSupport(data,items)
            if ((count*100)/float(len(data))) >= support*100 :
                FSet[item_str] = count
                main_data[frozenset(item_str.split(","))] = count


def generateRules(data, elem, confidence):
    # result = []
    if len(elem) > 1:
        length = len(elem) - 1
        # print elem
        while length > 0:
            for comb in map(frozenset,it.combinations(elem,length)):
                elemHead = comb
                supportHead = getSupport(data, elemHead)
                elemTail = elem.difference(comb)
                elemConfidence = main_data[elem]/float(supportHead)
                # print '{%s} -> {%s} , confidence = %s, support = %s' % (", ".join(elemHead), ", ".join(elemTail), elemConfidence, main_data[elem])
                if elemConfidence >= confidence:
                    rule.append(elem)
                    head.append(elemHead)
                    tail.append(elemTail)
                    conf.append(elemConfidence)
                    supp.append(main_data[elem])
            length -= 1

    else:
        if main_data[elem] >= confidence * 100:
            rule.append(elem)
            head.append([])
            tail.append(elem)
            conf.append(main_data[elem]/len(data))
            supp.append(main_data[elem])



def main(argv):
    global support
    global confidence
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:s:",["ifile=", "ofile=", "cvalue=", "svalue"])
    except getopt.GetoptError:
        print('Apriori.py -i <inputfile> -o <outputfile> -c <confidence> -s <support>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Apriori.py -i <inputfile> -o <outputfile> -c <confidence> -s <support>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-c", "--cvalue"):
            confidence = float(arg)
        elif opt in ("-s", "--svalue"):
            support = float(arg)
    print('Input file is ', inputfile)
    #print('Output file is ', outputfile)
    #print('Confidence is ', confidence)
    print('support is ' , support)
    data = readFile(inputfile)
    getFrequentItemSets(data)
    print len(main_data)
    for i in xrange(len(data[0])-1):
        prev_len = len(main_data)
        joinItemSets(data)
        print len(main_data)
        if prev_len == len(main_data):
            break

    for elem in main_data:
        generateRules(data, elem, confidence)

    for i in xrange(len(rule)):
        print '{%s} -> {%s} , confidence = %s, support = %s' % (", ".join(sorted(head[i])), ", ".join(sorted(tail[i])), conf[i], supp[i])

    # for i in main_data:
        # print i

    # print(FSet)

if __name__ == "__main__":
    main(sys.argv[1:])

    