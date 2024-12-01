import numpy as np
import gc
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

res1 = 0.1
res2 = int(10)
#gets point data from CSV. CSV should have 3 columns, with column 1 being angle of sideslip, column 2 being speed, column 3 being COP location
data = np.genfromtxt("data.csv", delimiter=",")

#copies each column into a separate array
angles = data[:,0]
speeds = data[:,1]
cop = data[:,2]
print("input data: " ,data)

#determines how many unique angles exist in hte data and what those angles are
uniqueAngles = np.sort(np.unique(angles))
uniqueAngleCount = uniqueAngles.shape[0]

#list used to store the control points for each speed vs COP spline
splineCtrPoints = []

#parses data file and separates data by angle and stores it in the splineCtrPoints list
for i in range(uniqueAngleCount):
    tempArray = []
    for j in range (angles.shape[0]):
        if angles[j] == uniqueAngles[i]:
            tempArray.append(data[j,:])
    tempArray = np.array(tempArray)
    splineCtrPoints.append(tempArray)

#intepolates the data using a cubic spline and creates an array with points on the spline every 0.1 units. Stores that araay to the angleSplines array.
#figures out the highest and lowest flow speed
speedsSorted = np.sort(speeds)
lowSpeed = speedsSorted[0]
highSpeed = speedsSorted[-1]
#deleting this array since it isn't used.
del speedsSorted
gc.collect()
angleSplines = []
for i in range(uniqueAngleCount):
    tempArray = splineCtrPoints[i]
    x = np.transpose(tempArray[:,1])
    y = np.transpose(tempArray[:,2])
    cs = CubicSpline(x, y)
    xs = np.arange(lowSpeed, highSpeed + res1, res1)
    ys=cs(xs)
    tempArray=[np.transpose(xs),np.transpose(ys)]
    txt = "data" + str(i) + ".csv"
    angleSplines.append(tempArray)
    np.savetxt(txt, tempArray,  delimiter = ",", fmt='%f')

angles = []
speeds = []
cop = []

for i in range (int((highSpeed-lowSpeed)*res2+1)):
    x = uniqueAngles
    y = []
    for j in range(uniqueAngleCount):
        y.append(angleSplines[j][1][i])
    cs = CubicSpline(x, y)
    for j in range (int(uniqueAngles[0]*res2),int(uniqueAngles[uniqueAngleCount-1]*res2+1)):
        angles.append(j/res2)
        speeds.append(lowSpeed+(i/res2))
        tempCOP = float(cs(j/res2))
        cop.append(tempCOP)
        j = j + 1

# Create meshgrid for surface plot
angles_grid, speeds_grid = np.meshgrid(np.unique(angles), np.unique(speeds))

# Interpolating Z values to fit the meshgrid
from scipy.interpolate import griddata
x_grid = griddata((angles, speeds), cop, (angles_grid, speeds_grid), method='linear')

# Plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#reverse color map
orig_map=cm.jet
reversed_map = orig_map.reversed()

# Surface plot
surf = ax.plot_surface(angles_grid, speeds_grid, x_grid, cmap=reversed_map, linewidth=0, antialiased=False)

# Set color range limits
# surf.set_clim(-1.7340416, 4.5)

# Labels
ax.set_xlabel('Angle of Sideslip (deg)')
ax.set_ylabel('Speed (knots)')
ax.set_zlabel('Center of Pressure (m)')
ax.view_init(elev=30, azim=45, roll=0)

# Add a color bar which maps values to colors
fig.colorbar(surf)

# Show plot
plt.show()