#Author - Bennett Steers
#Description - Takes OpenProp curves, parses them, turns them into splines, lofts 
# the splines into a propeller

import adsk.core, adsk.fusion, traceback
import os.path, csv, math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
            
        msg = ''
            
        # Set styles of file dialog.
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = True
        fileDlg.title = 'Select Propeller Curves'
        fileDlg.filter = "All suggested types(*.txt;*.sldcrv;*.csv);;Text files(*.txt);;Solidworks curve (*.sldcrv);;comma separated values(*.csv);;All files(*.*)"
        
        # Show file open dialog
        dlgResult = fileDlg.showOpen()
        if dlgResult != adsk.core.DialogResults.DialogOK:
            #exit script if windows is closed
            ui.messageBox("Error: No curves selected. Script is terminated")
            return
        #ui.messageBox(str(len(fileDlg.filenames))+" curve files have been selected")

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create construction plane
        planes = rootComp.constructionPlanes

        # Create loft
        loftFeats = rootComp.features.loftFeatures
        loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSectionsObj = loftInput.loftSections
        
        for filename in fileDlg.filenames:
            #parse open prop curves and read points into memory
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                # Insert X,Y and Z columns into list
                data = [[float(x) for x in row[:3]] for row in reader]
            
            #create a new sketch plane according the the Z coordinate in the openprop curve
            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(data[0][2]*100)
            planeInput.setByOffset(rootComp.xYConstructionPlane, offsetValue)
            plane = planes.add(planeInput)
            sketch = rootComp.sketches.add(plane)

            # Create an object collection for the points from the openprop curve.
            points = adsk.core.ObjectCollection.create()
            
            # If fusion 360 reads the points directly from file, it sees that the 
            # start and end points are the same and closes the spline. This 
            # causes the rear of the propeller airfoil to end in an incredibly 
            # small radius instead of a clearly defined edge. This causes 
            # problems later in fluent meshing as it freaks out when it sees the 
            # super small radius. To solve this, we create a fake data point by 
            # linearly interpolating beyond the end of the airfoil using the first,
            # and second coordinate. This makes the spline overlap, but remain open, 
            # giving us an actual edge.
            dirVectorLen = math.sqrt(math.pow(data[0][0]-data[1][0],2)+math.pow(data[0][1]-data[1][1],2))
            dirVector = [(data[0][0]-data[1][0])/dirVectorLen, (data[0][1]-data[1][1])/dirVectorLen]
            startPoint = [data[0][0]+0.0001*dirVector[0],data[0][1]+0.0001*dirVector[1]]

            # point has to be multiplied by 100 because the spline is given in meters,
            # and the Fusion 360 api takes input arguments as centimeters
            points.add(adsk.core.Point3D.create(startPoint[0]*100,startPoint[1]*100))

            #read points from openProp curve into points object
            for j in range (len(data)):
                # Define the points the spline with fit through.
                points.add(adsk.core.Point3D.create(data[j][0]*100,data[j][1]*100,))

            # same linear interpolation as explained above excpet on the last point 
            # instead of the first
            dirVectorLen = math.sqrt(math.pow(data[0][0]-data[len(data)-2][0],2)+math.pow(data[0][1]-data[len(data)-2][1],2))
            dirVector = [(data[0][0]-data[len(data)-2][0])/dirVectorLen, (data[0][1]-data[len(data)-2][1])/dirVectorLen]
            endPoint = [data[0][0]+0.0001*dirVector[0],data[0][1]+0.0001*dirVector[1]]
            points.add(adsk.core.Point3D.create(endPoint[0]*100, endPoint[1]*100))
         

            # Create the spline.
            spline = sketch.sketchCurves.sketchFittedSplines.add(points)

            #create profile for loft using the overlapping region of the spline
            profile = sketch.profiles.item(0)

            #add sketch to loft
            loftSectionsObj.add(profile)

            #hide the sketch
            sketch.isVisible = False

        #loft parameters
        loftInput.isSolid = True
        loftInput.isClosed = False
        loftInput.isTangentEdgesMerged = False
            
        # Create loft feature
        loftFeats.add(loftInput)

        

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))