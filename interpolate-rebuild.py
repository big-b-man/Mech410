import numpy as np
import csv
from scipy.interpolate import CubicSpline

inputFile = "exampleData.csv" #Input parameter for CSV file being used for data
precision = 0.1 #distance between points in final plot.

#loads data from CSV file, column 0 is X data, 1 is Y data, 2 is Z data
with open(inputFile, newline='') as csvfile:
    reader = csv.reader(csvfile)
    #extracts first row of data which should be data column titles
    titles = next(reader)
    data = np.array([[float(x) for x in row[:3]] for row in reader])

uniqueX = np.sort(np.unique(data[:,0]))#list of unique X values in dataset
uniqueXCount = uniqueX.shape[0]#number of unique X values in dataset
dataPointNum = data.shape[0]#number of datapoints in set

#delete these lines when program is completed
print(uniqueX)
print(uniqueXCount)
print(dataPointNum)
#delete above 3 lines

#Array used to store points in the Y vs Z splines
splineCtrPoints = []

#parses data file and separates data by X value and stores it in the splineCtrPoints list
#spline Control Points is a 3D array, where dimension 0 is the unique X point, dimension 1 is the Y or Z column,
#dimension 2 is a specific Y or Z value.
for i in range(uniqueXCount):
    tempArray = []
    for j in range (data.shape[0]):
        if data[j][0] == uniqueX[i]:
            tempArray.append(data[j,:])
    tempArray = np.array(tempArray)
    splineCtrPoints.append(tempArray)

print(splineCtrPoints[0])
print("\n")
print(splineCtrPoints[1])
print("\n")
print(splineCtrPoints[2])
print("\n")
print(splineCtrPoints[3])
print("\n")

for i in range(uniqueXCount):
    tempArray = np.sort(splineCtrPoints[i],0)
    print(tempArray)