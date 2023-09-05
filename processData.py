import csv
import numpy as np 
np.seterr(divide='ignore', invalid='ignore')

def takeFirst(elem):
    return int(elem[0])

def mergeAnnotation(strategyId, fileName, tweetNums, annotationNums):
    ansList = []
    megAnoList = []
    with open(fileName, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for row in data:
            if(str(row[1]) == str(strategyId)):
                ansList.append(row)

    ansList.sort(key=takeFirst)
    ansList = [[int(elem) for elem in item[6:]] for item in ansList]
    if(len(ansList) != tweetNums * annotationNums):
        return "error"
    else:
        for i in range(tweetNums):
            elem = np.sum(ansList[i*annotationNums:(i+1)*annotationNums], axis=0) / annotationNums
            megAnoList.append(elem)
    return megAnoList # merge annotation for same tweet


def processData(strategyId, questionId, fileName, typeNums, tweetNums, annotationNums): # 10, 90, 3
    megAnoList = mergeAnnotation(strategyId, fileName, tweetNums, annotationNums)
     
    megAnoList = [item[questionId - 1] for item in megAnoList]
    tweetPerType = tweetNums // typeNums
    megTypTList = []
    for i in range(typeNums):
        megTypTList.append(sum(megAnoList[i*tweetPerType:(i+1)*tweetPerType]) /tweetPerType)
    meanValue = sum(megTypTList)/typeNums
    return megAnoList, megTypTList , meanValue # merge annotation for same type


def getDifference1(var1, var2):
    var1 = np.array(var1)
    var2 = np.array(var2)
    influence = np.subtract(var2, var1)
    return influence, np.sum(influence) / var1.size

def getDifference2(var1, var2):
    var1 = np.array(var1)
    var2 = np.array(var2)
    influence = np.abs(np.subtract(var2, var1))
    return influence, np.sum(influence) / var1.size


def calculateCorralation(var1, var2):
    var1 = np.array(var1)
    var2 = np.array(var2)
    return np.corrcoef(var1, var2)[1,0]

# 2 strategies , 4 tweets consists of two types, each tweet has two annotation
# 1,1,1,2022-12-25 20:17:03,2022-12-25 20:17:18,zJbA6noP9YAO5yPi,-1,-1,-1,-1,-1,-1,-1,-1,4
# 1,1,2,2022-12-25 20:17:23,2022-12-25 20:17:28,CepDU4Bl6LZqdn9x,-1,-1,-1,-1,-1,-1,-1,-1,3
# 1,2,1,2022-12-25 20:17:33,2022-12-25 20:17:49,sx6w5a7CrI9AcIr7,5,4,5,4,-1,-1,-1,-1,5
# 1,2,2,2022-12-25 20:17:54,2022-12-25 20:18:08,HbAiZMkUjNQ0ZidT,3,5,5,4,-1,-1,-1,-1,5
# 2,1,1,2022-12-25 20:18:13,2022-12-25 20:18:21,aFxeBm6hjA4b8cOZ,-1,-1,-1,-1,-1,-1,-1,-1,4
# 2,1,2,2022-12-25 20:18:27,2022-12-25 20:18:32,xFYdkgu2vJQd36sX,-1,-1,-1,-1,-1,-1,-1,-1,4
# 2,2,1,2022-12-25 20:19:01,2022-12-25 20:19:14,NoqnjjsMGZa5SRVH,4,3,3,4,-1,-1,-1,-1,3
# 2,2,2,2022-12-25 20:19:19,2022-12-25 20:20:17,CY4zmzWwfqhcA5Z3,2,2,1,2,-1,-1,-1,-1,3
# 3,1,1,2022-12-25 20:20:30,2022-12-25 20:20:41,Kq7wclv3QrdUlh7X,-1,-1,-1,-1,-1,-1,-1,-1,1
# 3,1,2,2022-12-25 20:20:46,2022-12-25 20:20:51,Lht9rlLGM7PKOwOT,-1,-1,-1,-1,-1,-1,-1,-1,2
# 3,2,1,2022-12-25 20:20:55,2022-12-25 20:21:09,Wip33W0JvsxhgO3E,5,5,4,5,-1,-1,-1,-1,2
# 3,2,2,2022-12-25 20:21:15,2022-12-25 20:21:28,HRUHOZFhUGXdnBlu,4,4,3,5,-1,-1,-1,-1,3
# 4,1,1,2022-12-25 20:21:32,2022-12-25 20:21:38,5DGNJH7998DCyE5k,-1,-1,-1,-1,-1,-1,-1,-1,1
# 4,1,2,2022-12-25 20:21:42,2022-12-25 20:21:46,fRNWOiDnHhjcw8tN,-1,-1,-1,-1,-1,-1,-1,-1,1
# 4,2,1,2022-12-25 20:21:51,2022-12-25 20:22:05,sxr2mGvAYY0d2dGt,2,1,2,1,-1,-1,-1,-1,1
# 4,2,2,2022-12-25 20:22:10,2022-12-25 20:22:31,dDufiIVgYNHZKUYi,1,2,1,2,-1,-1,-1,-1,1


hatefulness1, _, _ =  processData(1, 9, "questionAnswer/submitted.csv", 2, 4, 2)
hatefulness2, _, _ =  processData(2, 9, "questionAnswer/submitted.csv",  2, 4, 2)
fluency, _, _ =  processData(2, 1, "questionAnswer/submitted.csv",  2, 4, 2)
informativeness, _, _ =  processData(2, 2, "questionAnswer/submitted.csv",  2, 4, 2)
persuasiveness, _, _ =  processData(2, 3, "questionAnswer/submitted.csv",  2, 4, 2)
soundness, _, _ =  processData(2, 4, "questionAnswer/submitted.csv",  2, 4, 2)



print(processData(1, 9, "questionAnswer/submitted.csv", 2, 4, 2)) # strategy 1 WO exp
# hatefulness: ([3.5, 4.0, 1.5, 1.0],   [3.75, 1.25],  2.5)
print(processData(2, 9, "questionAnswer/submitted.csv", 2, 4, 2)) # strategy 2 with hate exp
# hatefulness: ([5.0, 3.0, 2.5, 1.0],   [4.0, 1.75],   2.875)

influenceVector1, influence1 = getDifference1(hatefulness1, hatefulness2) # no absolutie
# [ 1.5 -1.   1.   0. ]
influenceVector2, influence2 = getDifference2(hatefulness1, hatefulness2) # take absolute at tweet level
print(influence1, influence2)
# 0.375 0.875

print(processData(2, 1, "questionAnswer/submitted.csv",  2, 4, 2))
# fluency ([4.0, 3.0, 4.5, 1.5], [3.5, 3.0], 3.25)
print(processData(2, 2, "questionAnswer/submitted.csv",  2, 4, 2))
# informativeness ([4.5, 2.5, 4.5, 1.5], [3.5, 3.0], 3.25)
print(processData(2, 3, "questionAnswer/submitted.csv",  2, 4, 2))
# persuasiveness ([5.0, 2.0, 3.5, 1.5], [3.5, 2.5], 3.0)
print(processData(2, 4, "questionAnswer/submitted.csv",  2, 4, 2))
# soundness ([4.0, 3.0, 5.0, 1.5], [3.5, 3.25], 3.375)


print(calculateCorralation(fluency, hatefulness2))
print(calculateCorralation(informativeness, hatefulness2))
print(calculateCorralation(persuasiveness, hatefulness2))
print(calculateCorralation(soundness, hatefulness2))  
# 0.6673024957731987
# 0.7230210236376228
# 0.8613853567506401
# 0.5659098667749684

print(calculateCorralation(fluency, influenceVector1))
print(calculateCorralation(informativeness, influenceVector1))
print(calculateCorralation(persuasiveness, influenceVector1))
print(calculateCorralation(soundness, influenceVector1))             
# 0.5966005392134929
# 0.776700895602923
# 0.8556888393747509
# 0.5915343423571165








