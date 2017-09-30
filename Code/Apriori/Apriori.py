import numpy, os, sys, getopt, itertools as it
import re
from pprint import pprint

confidence = 70
# support = .30 #40, 50, 60, 70
FSet={}
F1Set = {}
main_data = {}
rule=[]
head=[]
body=[]
conf=[]
supp=[]

def readFile(fileName):
    data = open(fileName).read().split("\n")[:-1]
    data = [i.replace("\r","").split("\t") for i in data]
    for i in xrange(len(data)):
        for j in xrange(len(data[i])):

            if j < len(data[i]) - 1:
                data[i][j] = "G%s_%s" % (str(j+1),data[i][j])

            if frozenset([data[i][j]]) not in FSet:
                FSet[frozenset([data[i][j]])] = 0

            FSet[frozenset([data[i][j]])] += 1

        data[i] = frozenset(data[i])


    return data

def getFrequentItemSets(data):
    for key, value in FSet.items():
        if ((value*100)/float(len(data))) < support*100 :
            FSet.pop(key, None)
        else:
            main_data[key] = value

def getSupport(data, items):
    count=0
    return ([items.issubset(row) for row in data]).count(True)


def joinItemSets(data):
    global FSet
    itemList = list(FSet.keys())

    FSet = {}
    items=[]
    # for item in list(it.combinations(itemList,2)):
    for item in itemList:
        for elem in itemList:
            if item == elem:
                continue

            order = frozenset(list(item) + list(elem))

            if len(order) != len(item) + 1:
                continue

            count = getSupport(data,order)

            if ((count*100)/float(len(data))) >= support*100 :
                FSet[order] = count
                main_data[order] = count


def generateRules(data, elem, confidence):
    if len(elem) > 1:
        length = len(elem) - 1

        while length > 0:
            for comb in map(frozenset,it.combinations(elem,length)):
                elemBody = comb
                supportHead = getSupport(data, elemBody)
                elemHead = elem.difference(comb)
                elemConfidence = main_data[elem]/float(supportHead)
                # print '{%s} -> {%s} , confidence = %s, support = %s' % (", ".join(elemBody), ", ".join(elemHead), elemConfidence, main_data[elem])
                if elemConfidence >= confidence:
                    rule.append(elem)
                    head.append(elemHead)
                    body.append(elemBody)
                    conf.append(elemConfidence)
                    supp.append(main_data[elem])
            length -= 1


def template1(checkType, countType, elems):
    checkArea = eval(checkType.lower())
    trueRetData = []
    falseRetData = []    
    tempCount = 0

    for i in xrange(len(checkArea)):
        storeItem = '{%s} -> {%s}' % (", ".join(body[i]), ", ".join(head[i]))
        tempCount = ([frozenset([j]).issubset(checkArea[i]) for j in elems]).count(True)

        if tempCount > 0:
            flag = True
            trueRetData.append([storeItem,tempCount])
        else:
            falseRetData.append(storeItem)

    if countType == 'NONE':
        return (falseRetData,len(falseRetData))

    elif countType == 'ANY':
        trueRetData = [i[0] for i in trueRetData]
        return (trueRetData,len(trueRetData))

    else:
        trueRetData = [i[0] for i in trueRetData if i[1] == countType]
        return (trueRetData, len(trueRetData))

def template2(checkType, countType):
    checkArea = eval(checkType.lower())
    retData = []

    for i in xrange(len(checkArea)):
        storeItem = '{%s} -> {%s}' % (", ".join(body[i]), ", ".join(head[i]))
        if len(checkArea[i]) >= countType:
            retData.append(storeItem)

    return (retData,len(retData))

def template3(*kwargs):
    kwargs = list(kwargs)
    checkType = kwargs[0]

    data = []

    del kwargs[0]
    numbers = [int(i) for i in re.findall("\d+",checkType)]
    logicOper = re.findall("[a-zA-Z]+", checkType)[0]

    # print logicOper

    for number in numbers:
        argsCount = 4 - number

        funcArgs = [repr(i) for i in kwargs[:(argsCount)]]

        del kwargs[:(argsCount)]

        tempCall = '''template%s(%s)''' % (number, ", ".join(map(str,funcArgs)))

        (result,cnt) = eval(tempCall)

        data.append(result)

    if logicOper == 'or':
        data = list(set(data[0]).union(set(data[1])))

    else:
        data = list(set(data[0]).intersection(set(data[1])))


    return (data,len(data))


def main(argv):
    global support
    global confidence
    queryfile = None
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:s:q:",["ifile=", "ofile=", "cvalue=", "svalue=", "qfile="])
    except getopt.GetoptError:
        print('Apriori.py -i <inputfile> -o <outputfile> -c <confidence> -s <support> -q <queryfile>')
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
        elif opt in ("-q", "--qfile"):
            queryfile = arg

    data = readFile(inputfile)
    getFrequentItemSets(data)

    for i in xrange(len(data[0])-1):
        prev_len = len(main_data)
        joinItemSets(data)

        if prev_len == len(main_data):
            break

    print 'Support is set to %s%%' % (support * 100)
    print 'Confidence is set to %s%%' % (confidence * 100)
    print
    items = {}
    for rul in main_data:
        length = len(rul)
        if length not in items:
            items[length] = 0
        items[length] += 1

    for elem in main_data:
        generateRules(data, elem, confidence)

    if queryfile is None:

        for item in sorted(items):
            print 'Number of length-%s frequent itemsets: %s' % (item, items[item])

        print 'Total number of frequent sets: %s' % (len(main_data))

    else:
        queries = [i.strip() for i in open(queryfile).read().split("\n") if i != ""]
        for query in queries:
            print query
            exec(query)
            count = eval(query.split(", ")[1].split(")")[0])
            print count

if __name__ == "__main__":
    main(sys.argv[1:])

    