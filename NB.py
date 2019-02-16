from __future__ import division
import matplotlib.pyplot as plt
import csv
import math

def readLabels(labelList,fileName, labels, spaceSet, medSet, deleted):
	with open(fileName) as file:
		values = csv.reader(file, delimiter=',')
		count = 0
		for value in values:
			if count not in deleted:
				labelList.append(int(value[0]))
				if value[0] == '0':
					labels['medical'] += 1
					medSet.add(count)
				elif value[0] == '1':
					labels['space'] += 1
					spaceSet.add(count)
			count += 1

def readFeatures(fileName, spaceFeatures, medFeatures, spaceSet, medSet, wordInDocCountSpace, wordInDocCountMed, deleted):
	with open(fileName) as file:
		row = csv.reader(file, delimiter=',')
		count = 0
		for feature in row:
			if count not in deleted:
				if count in spaceSet:
					for x in xrange(len(feature)):
						if feature[x] != '0':
							wordInDocCountSpace[x] += 1
						spaceFeatures[x] += int(feature[x])
				
				elif count in medSet:
					for x in xrange(len(feature)):
						if feature[x] != '0':
							wordInDocCountMed[x] += 1
						medFeatures[x] += int(feature[x])
			count += 1

def train(features, probs, total):
	for x in xrange(len(features)):
		#probs[x] = (features[x]) / (total)
		probs[x] = (features[x] + 1) / (total + len(features) * len(features))

def test(results, trainingProbsSpace, trainingProbsMeds, probs, fileName):
	 with open(fileName) as file:
	 	row = csv.reader(file, delimiter=',')
	 	for feature in row:
	 		spaceRes = 0
	 		medRes = 0
	 		for x in xrange(len(feature)):
	 			spaceRes += int(feature[x]) * math.log(trainingProbsSpace[x]) if trainingProbsSpace[x] != 0 else 0
	 			medRes += int(feature[x]) * math.log(trainingProbsMeds[x]) if trainingProbsMeds[x] != 0 else 0
	 		results.append(1 if spaceRes + math.log(probs['space']) > medRes + math.log(probs['medical']) else 0)

def calculateAccuracy(testResults, spaceSetTesting, medSetTesting, accuracyList):
	correct = 0
	incorrect = 0
	for x in xrange(len(testResults)):
			if x in spaceSetTesting and testResults[x] == 1 or x in medSetTesting and testResults[x] == 0:
				correct += 1
			else: 
				incorrect += 1
	accuracy = 0 if correct + incorrect == 0 else correct / (correct + incorrect)
	accuracyList.append(accuracy)
	print accuracy

def calculateMutualInfo(labelCountTraining, wordInDocCountSpace, wordInDocCountMed, mutualInfo):
	for x in xrange(len(wordInDocCountSpace)):
		N11 = wordInDocCountSpace[x]
		N01 = labelCountTraining['space'] - N11
		N10 = wordInDocCountMed[x]
		N00 = labelCountTraining['medical'] - N10
		N = N11 + N01 + N10 + N00
		one = 0 if N11 == 0 or N11 + N10 == 0 else (N11 / N) * math.log(((N * N11) / ((N11 + N10) * labelCountTraining['space'])),2)
		two = 0 if N01 == 0 or N01 + N00 == 0 else (N01 / N) * math.log(((N * N01) / ((N01 + N00) * labelCountTraining['space'])),2)
		three = 0 if N10 == 0 or N11 + N10 == 0 else (N10 / N) * math.log(((N * N10) / ((N11 + N10) * labelCountTraining['medical'])),2)
		four = 0 if N00 == 0 or N01 + N00 == 0 else (N00 / N) * math.log(((N * N00) / ((N01 + N00) * labelCountTraining['medical'])),2)
		mutualInfo.append((x, one + two + three + four))

labelCountTraining = {'space' : 0, 'medical':0}
labelCountTesting = {'space' : 0, 'medical':0}

trainingLabelsFile = "train-labels.csv"
trainingFeaturesFile = "train-features.csv"
testingLabelsFile = "test-labels.csv"
testingFeaturesFile = "test-features.csv"

spaceSetTraining = set()
medSetTraining = set()

spaceSetTesting = set()
medSetTesting = set()

trainingFeaturesSpace = [0] * 26507
wordInDocCountSpace = [0] * 26507
trainingFeaturesMed = [0] * 26507
wordInDocCountMed = [0] * 26507
trainingProbsSpace = [0] * 26507
trainingProbsMed = [0] * 26507

testingFeaturesSpace = [0] * 26507
testingFeaturesMed = [0] * 26507
testingProbsSpace = [0] * 26507
testingProbsMed = [0] * 26507


trainLabels = []
testLabels = []
testResults = []
mutualInfo = []

deleted = set()

readLabels(trainLabels, trainingLabelsFile, labelCountTraining, spaceSetTraining, medSetTraining, deleted)
readLabels(testLabels, testingLabelsFile, labelCountTesting, spaceSetTesting, medSetTesting, deleted)

readFeatures(trainingFeaturesFile, trainingFeaturesSpace, trainingFeaturesMed, spaceSetTraining, medSetTraining, wordInDocCountSpace, wordInDocCountMed, deleted)

probSpace = labelCountTraining['space'] / (labelCountTraining['space'] + labelCountTraining['medical'])
probMed = labelCountTraining['medical'] / (labelCountTraining['space'] + labelCountTraining['medical'])

probs = {'space' : probSpace, 'medical': probMed}

accuracyList = []

train(trainingFeaturesSpace, trainingProbsSpace, sum(trainingFeaturesSpace))
train(trainingFeaturesMed, trainingProbsMed, sum(trainingFeaturesMed))

test(testResults, trainingProbsSpace, trainingProbsMed, probs, testingFeaturesFile)

calculateMutualInfo(labelCountTraining, wordInDocCountSpace, wordInDocCountMed, mutualInfo)

calculateAccuracy(testResults, spaceSetTesting, medSetTesting, accuracyList) 

print "Mutual Info for the top 10 features"
mutualInfo = sorted(mutualInfo,  key = lambda x: float(x[1]))
for x in xrange(len(mutualInfo) - 1, len(mutualInfo) - 11, -1):
	print "{} : {}".format(mutualInfo[x][0], mutualInfo[x][1])

