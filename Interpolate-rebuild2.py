import numpy as np
import csv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from matplotlib import cm
import time
#program to extrapolate a data set and plots the results
#Known bugs: Program fails if there is only one corresponding yz data point for a unique x point

start_time = time.time()
inputFile = "exampleData.csv" #Input parameter for CSV file being used for data
points = 100 #of points used in data extrapolation per axis'
create2Dplot = False #create 2D plot of YZ splines
create3Dplot = True #create 3D surface plot of XYZ data

#loads data from CSV file, column 0 is X data, 1 is Y data, 2 is Z data
with open(inputFile, newline='') as csvfile:
    reader = csv.reader(csvfile)
    #extracts first row of data which should be data column titles
    titles = next(reader)#reads column titles from first row
    data = np.array([[float(x) for x in row[:3]] for row in reader])#reads data from remaining rows

uniqueX = np.sort(np.unique(data[:,0]))#list of unique X values in dataset
uniqueXCount = uniqueX.shape[0]#number of unique X values in dataset
tempY = np.sort(np.unique(data[:,1]))
yMin = tempY[0]#minimum Y value in dataset
yMax = tempY[-1]#maximum Y value in dataset

# Creates list for YZ splines, each entry is a function, Z(y) that returns a Z value given a y value for a unique x point.
# example: If uniqueX[1] = 2.5, Y=2 and Z=3, YZsplines[1](2) = 3
YZsplines = []

for i in range(uniqueXCount):
    tempArray = []
    for j in range (data.shape[0]):
        if data[j][0] == uniqueX[i]:
            tempArray.append(data[j,1:])
    tempArray  = np.array(sorted(tempArray, key=lambda x: x[0]))#ensures Y values are ordered as CubicSpline() will fail if first input isn't sequential
    spline = CubicSpline(np.transpose(tempArray[:,0]),np.transpose(tempArray[:,1]))#creates cubic spline to find Z as a function of Y for a unique X value
    YZsplines.append(spline)#add spline to array

if (create2Dplot == True):
    #create 2D plot of YZ splines
    handles = []
    labels = []
    fig, ax = plt.subplots()
    for i in range(uniqueXCount):
        y = np.linspace(yMin,yMax,100)
        z = YZsplines[i](y)
        line, = ax.plot(y, z , markeredgewidth=2)
        handles.append(line)  # Add the line handle to the handles list
        labels.append(uniqueX[i])  # Add the corresponding label

    # Add the legend with all handles and labels
    ax.legend(handles, labels, loc='upper right', title = titles[0])

    ax.set_xlabel(titles[1])
    ax.set_ylabel(titles[2])
    plt.show()

def getZ(x, y):
    z_values = np.zeros((y.shape[0], x.shape[0]))  # Initialize an array for z values
    for i, yi in enumerate(y):  # Loop over y values
        tempZ = [YZsplines[j](yi) for j in range(uniqueXCount)]
        spline = CubicSpline(uniqueX, tempZ)
        z_values[i, :] = spline(x)
    return z_values

if (create3Dplot == True):
    xPoints = np.linspace(uniqueX[0],uniqueX[-1],points)
    yPoints = np.linspace(yMin,yMax,points)
    x_grid, y_grid = np.meshgrid(xPoints,yPoints)
    z_grid  = getZ(xPoints, yPoints)

    # Plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #reverse color map
    orig_map=cm.jet
    reversed_map = orig_map.reversed()

    # Surface plot
    surf = ax.plot_surface(x_grid, y_grid, z_grid, cmap=reversed_map, linewidth=0, antialiased=False)

    # Labels
    ax.set_xlabel(titles[0])
    ax.set_ylabel(titles[1])
    ax.set_zlabel(titles[2])
    ax.view_init(elev=30, azim=45, roll=0)

    # Add a color bar which maps values to colors
    fig.colorbar(surf)

    print("--- %s seconds ---" % (time.time() - start_time))
    # Show plot
    plt.show()