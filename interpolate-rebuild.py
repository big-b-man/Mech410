import numpy as np
import csv
import gc
from scipy.interpolate import CubicSpline
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib import cm

#program to extrapolate a data set and plots the results
#Known bugs: Program fails if there is only one corresponding yz data point for a unique x point

inputFile = "exampleData.csv" #Input parameter for CSV file being used for data
precision = 0.1 #distance between points in final plot.

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

del tempY#delete this as we don't need it anymore
gc.collect()

#Array used to store points in the Y vs Z splines
splineCtrPoints = []

#parses data file and separates data by X values and stores it in the splineCtrPoints list
#spline Control Points is a 3D array, where dimension 0 is the unique X point, dimension 1 is the Y or Z column,
#dimension 2 is a specific Y or Z value.
for i in range(uniqueXCount):
    tempArray = []
    for j in range (data.shape[0]):
        if data[j][0] == uniqueX[i]:
            tempArray.append(data[j,1:])
    tempArray  = np.array(sorted(tempArray, key=lambda x: x[0]))#ensures Y values are ordered as CubicSpline() will fail if first input isn't sequential
    spline = CubicSpline(np.transpose(tempArray[:,0]),np.transpose(tempArray[:,1]))#creates cubic spline using Y and Z values in one of the uniqueX arrays
    tempY = np.arange(yMin, yMax+precision, precision)#creates Y values for spline interpolation given specified precision at start
    tempZ = spline(tempY)#creates Z values for associated Y values
    tempArray = np.transpose(np.array([tempY,tempZ]))# Stores interpolated Y and Z values in numpy array
    splineCtrPoints.append(tempArray)# Appeds the data to the splineCtrPoints array

splineCtrPoints = np.array(splineCtrPoints)#convert to np array so we can create a for loop using it's shape

#arrays used to store data points from second spline interpolation
plotPointsX = []
plotPointsY = []
plotPointsZ = []

for i in range (splineCtrPoints.shape[1]):
    spline = CubicSpline(uniqueX,splineCtrPoints[:,i,1])#creates cubic spline with X and Z values for given Y value of previous spline interpolation
    tempX = np.arange(uniqueX[0],uniqueX[-1]+precision,precision)#Array of X values defined by precision variable
    tempZ = spline(tempX)#Z values created from X values
    tempY = np.repeat(splineCtrPoints[0][i][0],tempX.shape[0])#Array of Y values which is constant
    plotPointsX.append(tempX)
    plotPointsY.append(tempY)
    plotPointsZ.append(tempZ)

#flatten the arrays since the append method just adds the arrays together as a list of 1d arrays
plotPointsX = np.array(plotPointsX).flatten()
plotPointsY = np.array(plotPointsY).flatten()
plotPointsZ = np.array(plotPointsZ).flatten()

# Create meshgrid for surface plot
X_grid, Y_grid = np.meshgrid(np.unique(plotPointsX), np.unique(plotPointsY))
# Interpolating Z values to fit the meshgrid, want to reword this as a function of x,y at some point
Z_grid = griddata((plotPointsX, plotPointsY), plotPointsZ, (X_grid, Y_grid), method='linear')

# Plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#reverse color map
orig_map=cm.jet
reversed_map = orig_map.reversed()

# Surface plot
surf = ax.plot_surface(X_grid, Y_grid, Z_grid, cmap=reversed_map, linewidth=0, antialiased=False)

# Set color range limits
# surf.set_clim(-1.7340416, 4.5)

# Labels
ax.set_xlabel(titles[0])
ax.set_ylabel(titles[1])
ax.set_zlabel(titles[2])
ax.view_init(elev=30, azim=45, roll=0)

# Add a color bar which maps values to colors
fig.colorbar(surf)

# Show plot
plt.show()