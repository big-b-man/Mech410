#Author- Bennett Steers
#Description- Makes a hull loft from 2 imported CSV files that describe the 2D hull curves
#imported curves must only contain the positive half of the y points for each profile
#if the x points are negative, the profile must be mirrored so that they are positive
#imported CSV's must be arranged with the X values going from lowest to highest value

import adsk.core, adsk.fusion, adsk.cam, traceback, csv, math
import scipy
import numpy as np
from scipy.interpolate import CubicSpline

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        # Get the root component of the active design.
        rootComp = design.rootComponent
        
        #import hull profiles
        # Set styles of file dialog.
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        
        # Show file open dialog for horizontal profile
        fileDlg.title = 'Select Horizontal Profile'
        fileDlg.filter = "comma separated values(*.csv);;All files(*.*)"
        dlgResult = fileDlg.showOpen()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            #exit script if windows is closed
            ui.messageBox("Error: file selected, program terminated")
            return
        
        #parse horizontal profile and load into memory
        with open(fileDlg.filename, 'r') as file:
            reader = csv.reader(file)
            # Insert X,Y and Z columns into list
            XYdata = [[float(x) for x in row[:2]] for row in reader]

        # Show file open dialog for vertical profile
        fileDlg.title = 'Select Verical Profile'
        fileDlg.filter = "comma separated values(*.csv);;All files(*.*)"
        dlgResult = fileDlg.showOpen()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            #exit script if windows is closed
            ui.messageBox("Error: file selected, program terminated")
            return
        
        #parse vertical profile and load into memory
        with open(fileDlg.filename, 'r') as file:
            reader = csv.reader(file)
            # Insert X,Y and Z columns into list
            YZdata = [[float(x) for x in row[:2]] for row in reader]

        #convert to numpy arrays so I don't loose my mind (IDC that they're slower)
        XYdata = np.array(XYdata)*2.54
        YZdata = np.array(YZdata)*2.54

        if XYdata[-1,0] < YZdata[-1,0]:
            xMax = XYdata[-1,0]
        else:
            xMax = YZdata[-1,0]

        #create a cubic spline from both the imported CSV files
        horizontalSpline = CubicSpline(XYdata[:,0],XYdata[:,1],)
        verticalSpline = CubicSpline(YZdata[:,0],YZdata[:,1],)
        
        #calculate the derivative spline of the vertical spline
        vertPrime = verticalSpline.derivative()

        # Create loft feature object
        loftFeats = rootComp.features.loftFeatures
        loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSectionsObj = loftInput.loftSections

        #create sketch for loft
        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
        #single point to represent bow
        bowPoint = sketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        loftSectionsObj.add(bowPoint)

        #draw loft ovals based on rate of curvature of the vertical hull profile
        slopeLast = 100
        slope = 100
        xVal = 0
        while xVal < xMax:
            if(abs(math.atan(slope)-math.atan(slopeLast))) > 0.035: #0.035 radians ~ 2deg of curvature
                centerPoint = adsk.core.Point3D.create(0,xVal,0)
                verticalPoint = adsk.core.Point3D.create(0,xVal,float(verticalSpline(xVal)))
                horizontalPoint = adsk.core.Point3D.create(float(horizontalSpline(xVal)),xVal,0)
                loftOval = sketch.sketchCurves.sketchEllipses.add(centerPoint,verticalPoint,horizontalPoint)
                loftSectionsObj.add(loftOval)
                slopeLast = slope
            xVal = xVal + 0.01
            slope = float(vertPrime(xVal))

        #hide the sketch
        sketch.isVisible = False
        #loft parameters
        loftInput.isSolid = False
        loftInput.isClosed = False
        loftInput.isTangentEdgesMerged = False

        # Create loft feature
        loftFeats.add(loftInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))