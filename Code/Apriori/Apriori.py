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


    # pprint(FSet)
    # exit(0)
    return data

def getFrequentItemSets(data):
    # print(len(data))
    for key, value in FSet.items():
        if ((value*100)/float(len(data))) < support*100 :
            FSet.pop(key, None)
        else:
            # print key,value,(value/float(len(data))),(value/float(len(data))) < support,support
            main_data[key] = value
            # FSet[frozenset([key])] = value

def getSupport(data, items):
    count=0
    # for row in data:
    #     count += 1&items.issubset(row)
    return ([items.issubset(row) for row in data]).count(True)


def joinItemSets(data):
    global FSet
    # itemList=list(sorted(FSet.keys(), key = lambda x: int("".join(re.findall("\d+",x)))))
    # item1List=list(sorted(F1Set.keys(), key = lambda x: int("".join(re.findall("\d+",x)))))
    itemList = list(FSet.keys())

    # print len(itemList)
    FSet = {}
    items=[]
    # for item in list(it.combinations(itemList,2)):
    for item in itemList:
        for elem in itemList:
            if item == elem:
                continue

        # if ",".join(item[0].split(",")[:-1]) == ",".join(item[1].split(",")[:-1]):
            # item_str=",".join([item,elem])
            # order = [int(i) for i in re.findall("\d+",item_str)]
            order = frozenset(list(item) + list(elem))
            # if order != sorted(order) or len(set(order)) != len(order):
            if len(order) != len(item) + 1:
                continue
            # print item_str,order
            count = getSupport(data,order)
            # print count,order
            if ((count*100)/float(len(data))) >= support*100 :
                # print order
                FSet[order] = count
                main_data[order] = count
                # print order


def generateRules(data, elem, confidence):
    # result = []
    if len(elem) > 1:
        length = len(elem) - 1
        # print elem
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

    # else:
    #     # print elem

    #     if main_data[elem] >= confidence * 100:
    #         rule.append(elem)
    #         head.append(elem)
    #         body.append([])
    #         conf.append(main_data[elem]/len(data))
    #         supp.append(main_data[elem])

def template1(checkType, countType, elems):
    checkArea = eval(checkType.lower())
    trueRetData = []
    falseRetData = []    
    tempCount = 0

    for i in xrange(len(checkArea)):
        # print item, elems
        storeItem = '{%s} -> {%s}' % (", ".join(body[i]), ", ".join(head[i]))
        tempCount = ([frozenset([j]).issubset(checkArea[i]) for j in elems]).count(True)
        if tempCount > 0:
            flag = True
            # print storeItem,tempCount
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
        if len(checkArea[i]) == countType:
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

        # for arg in funcArgs:
        #     print repr(arg)

        del kwargs[:(argsCount)]

        tempCall = '''template%s(%s)''' % (number, ", ".join(map(str,funcArgs)))

        # print tempCall

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
    # print('Input file is ', inputfile)
    #print('Output file is ', outputfile)
    #print('Confidence is ', confidence)
    # print('support is ' , support)
    data = readFile(inputfile)
    getFrequentItemSets(data)
    # print len(main_data)
    for i in xrange(len(data[0])-1):
        prev_len = len(main_data)
        joinItemSets(data)
        # print len(main_data)
        if prev_len == len(main_data):
            break

    print 'Support is set to %s%%' % (support * 100)
    items = {}
    for rul in main_data:
        length = len(rul)
        if length not in items:
            items[length] = 0
        items[length] += 1

    # print main_data

    for item in sorted(items):
        print 'Number of length-%s frequent itemsets: %s' % (item, items[item])

    print 'Total number of frequent sets: %s' % (len(main_data))

    for elem in main_data:
        # print elem
        generateRules(data, elem, confidence)


    (result,cnt) = template1("BODY", "ANY", ['G10_Down'])
    print '''*******************template1("BODY", "ANY", ['G10_Down']) check**************************'''

    for res in result:
        print res
    print cnt

    (result,cnt) = template2('HEAD',2)
    print '''*******************template2('HEAD',2) check**************************'''

    for res in result:
        print res
    print cnt

    (result,cnt) = template3("1and2", "BODY", "ANY", ['G10_Down'], "HEAD", 2)
    print '''*******************template3("1and2", "BODY", "ANY", ['G10_Down'], "HEAD", 2) check**************************'''

    for res in result:
        print res
    print cnt

    # for i in xrange(len(rule)):
        # print ", ".join(rule[i])
        # print rule[i]
        # print '{%s} -> {%s} , confidence = %s, support = %s' % (", ".join(body[i]), ", ".join(head[i]), conf[i], supp[i])

    # for i in main_data:
        # print i

    # print(FSet)

if __name__ == "__main__":
    main(sys.argv[1:])

    