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
    # read the file and convert it to required format
    # also create 1-length frequent itemset 
    # args: fileName : String : path of the association file
    # output : data : array : array of transactions 

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
    # prune the itemsets based on their support
    # args : data : array : association data array

    for key, value in FSet.items():
        if ((value*100)/float(len(data))) < support*100 :
            FSet.pop(key, None)
        else:
            main_data[key] = value

def getSupport(data, items):
    # get support for the itemset from data
    # args : data : array : association data array
    #        items : frozenset : itemset
    # output : integer : support count

    count=0
    return ([items.issubset(row) for row in data]).count(True)


def joinItemSets(data):
    # join k-1 length itemset to generate k-length itemset
    # prune them as well based on support
    # args : data : association data array

    global FSet
    # get all k-1 length itemsets
    itemList = list(FSet.keys())

    FSet = {}
    items=[]
    # for item in list(it.combinations(itemList,2)):
    # iterate over all combinations
    for item in itemList:
        for elem in itemList:

            if item == elem:
                continue

            # create a set of elements of both itemsets
            order = frozenset(list(item) + list(elem))

            # if length not k then skip
            if len(order) != len(item) + 1:
                continue

            # get support
            count = getSupport(data,order)

            # if support is less than required then prune it 
            if ((count*100)/float(len(data))) >= support*100 :
                FSet[order] = count
                main_data[order] = count


def generateRules(data, elem, confidence):
    # generate all possible rules for the itemset whose confidence is more than 
    # the specified confidence
    # args : data : array : association data array
    #        elem : set : itemset
    #        confidence : float : confidence value

    # if itemset length more than 1 then process
    if len(elem) > 1:
        length = len(elem) - 1

        while length > 0:
            # generate all possible combinations of length more than equal to 1
            for comb in map(frozenset,it.combinations(elem,length)):
                # extract head and body
                elemBody = comb
                supportHead = getSupport(data, elemBody)
                elemHead = elem.difference(comb)

                # generate confidence
                elemConfidence = main_data[elem]/float(supportHead)
                # print '{%s} -> {%s} , confidence = %s, support = %s' % (", ".join(elemBody), ", ".join(elemHead), elemConfidence, main_data[elem])

                # if confidence more than required then store
                if elemConfidence >= confidence:
                    rule.append(elem)
                    head.append(elemHead)
                    body.append(elemBody)
                    conf.append(elemConfidence)
                    supp.append(main_data[elem])
            length -= 1


def template1(checkType, countType, elems):
    # function to process template 1 queries
    # args : checkType : String : part of rule to check on
    #        countType: String/Int : count or ANY or NONE
    #        elems : array : array of items to be checked
    # output : data : array : array of rules
    #           count : integer : number of rules

    # get part of rule to work on 
    checkArea = eval(checkType.lower())
    trueRetData = []
    falseRetData = []    
    tempCount = 0

    # iterate rules
    for i in xrange(len(checkArea)):
        storeItem = '{%s} -> {%s}' % (", ".join(body[i]), ", ".join(head[i]))

        # get count of rules in which any item is present
        tempCount = ([frozenset([j]).issubset(checkArea[i]) for j in elems]).count(True)

        # if present set present flag to true and add to truedata
        # else add to falsedata
        if tempCount > 0:
            flag = True
            trueRetData.append([storeItem,tempCount])
        else:
            falseRetData.append(storeItem)

    if countType == 'NONE':
        # if none to be found then return falsedata
        return (falseRetData,len(falseRetData))

    elif countType == 'ANY':
        # if any then return whole truedata
        trueRetData = [i[0] for i in trueRetData]
        return (trueRetData,len(trueRetData))

    else:
        # return only the rules whose count if equal to countType
        trueRetData = [i[0] for i in trueRetData if i[1] == countType]
        return (trueRetData, len(trueRetData))

def template2(checkType, countType):
    # function to process template 2 queries
    # args : checkType : String : part of rule to check on
    #        countType: String/Int : count or ANY or NONE
    # output : retData : array : array of rules
    #           count : integer : number of rules

    # get part of rule to work on 
    checkArea = eval(checkType.lower())
    retData = []

    # iterate rules
    for i in xrange(len(checkArea)):
        storeItem = '{%s} -> {%s}' % (", ".join(body[i]), ", ".join(head[i]))
        # if count of items is more than countType then add to result array
        if len(checkArea[i]) >= countType:
            retData.append(storeItem)

    # return the results
    return (retData,len(retData))

def template3(*kwargs):
    # function to process template 3 queries
    # args : kwargs : variable number of args 
    # output : data : array : array of rules
    #          count : integer : number of rules

    # get all arguments
    kwargs = list(kwargs)
    # get part of rule to work on 
    checkType = kwargs[0]

    data = []

    del kwargs[0]
    
    # get templates to work on
    numbers = [int(i) for i in re.findall("\d+",checkType)]

    # get relation between the two templates to work on
    logicOper = re.findall("[a-zA-Z]+", checkType)[0]

    # print logicOper
    # iterate each template separately
    for number in numbers:
        argsCount = 4 - number
        # find all arguments for template
        funcArgs = [repr(i) for i in kwargs[:(argsCount)]]

        del kwargs[:(argsCount)]

        tempCall = '''template%s(%s)''' % (number, ", ".join(map(str,funcArgs)))

        # call the template
        (result,cnt) = eval(tempCall)

        # store the result
        data.append(result)

    if logicOper == 'or':
        # if OR then union
        data = list(set(data[0]).union(set(data[1])))

    else:
        # else intersection
        data = list(set(data[0]).intersection(set(data[1])))

    # return results
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

    # process file
    data = readFile(inputfile)
    # generate 1-length itemsets from the file
    getFrequentItemSets(data)

    for i in xrange(len(data[0])-1):
        # generate k itemsets from k-1 itemsets
        prev_len = len(main_data)
        joinItemSets(data)

        if prev_len == len(main_data):
            break

    print 'Support is set to %s%%' % (support * 100)
    print 'Confidence is set to %s%%' % (confidence * 100)
    print
    items = {}
    # get number of rules for all lengths
    for rul in main_data:
        length = len(rul)
        if length not in items:
            items[length] = 0
        items[length] += 1

    # generate all the rules for the itemsets left after pruning
    for elem in main_data:
        generateRules(data, elem, confidence)

    # if no queries then print counts of itemsets
    if queryfile is None:

        for item in sorted(items):
            print 'Number of length-%s frequent itemsets: %s' % (item, items[item])

        print 'Total number of frequent sets: %s' % (len(main_data))

    # print query and count
    else:
        queries = [i.strip() for i in open(queryfile).read().split("\n") if i != ""]
        for query in queries:
            print query
            exec(query)
            count = eval(query.split(", ")[1].split(")")[0])
            print count

if __name__ == "__main__":
    main(sys.argv[1:])

    