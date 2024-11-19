#Author-
#Description-

import adsk.core, adsk.fusion, traceback
import csv

def run(context):
    ui = None
    try: 
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = app.activeProduct

        # Prompt the user for location of curve files
        isValid = False
        filepath = 'default value'  # The initial default value.
        while not isValid:
            # Get a string from the user.
            retVals = ui.inputBox('Enter file folder location (use forward)', 'File path', filepath)
            if retVals[0]:
                (filepath, isCancelled) = retVals
            
            # Exit the program if the dialog was cancelled.
            if isCancelled:
                return
            
            isValid = True

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create construction plane
        planes = rootComp.constructionPlanes

        # Create loft
        loftFeats = rootComp.features.loftFeatures
        loftInput = loftFeats.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSectionsObj = loftInput.loftSections

        for i in range (1,21):
            #data parsing
            filename = filepath + 'SectionCurve' + str(i) + '.txt'
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                # Insert X,Y and Z columns into list
                data = [[float(x) for x in row[:3]] for row in reader]
            
            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(data[0][2]*100)
            planeInput.setByOffset(rootComp.xYConstructionPlane, offsetValue)
            plane = planes.add(planeInput)

            # Create a new sketch on offset plane
            sketch = rootComp.sketches.add(plane) 

            # Create an object collection for the points.
            points = adsk.core.ObjectCollection.create()

            for j in range (len(data)):
                # Define the points the spline with fit through.
                points.add(adsk.core.Point3D.create(data[j][0]*100,data[j][1]*100,))


            #points.add(adsk.core.Point3D.create(data[0][0]*100,data[0][1]*100,))
            

            # Create the spline.
            spline = sketch.sketchCurves.sketchFittedSplines.add(points)

            #create profile for loft
            profile = sketch.profiles.item(0)

            #add sketch to loft
            loftSectionsObj.add(profile)
            
        #loft parameters
        loftInput.isSolid = True
        loftInput.isClosed = False
        loftInput.isTangentEdgesMerged = False
        #loftInput.startLoftEdgeAlignment = adsk.fusion.LoftEdgeAlignments.FreeEdgesLoftEdgeAlignment
        #loftInput.endLoftEdgeAlignment = adsk.fusion.LoftEdgeAlignments.FreeEdgesLoftEdgeAlignment
        
        # Create loft feature
        loftFeats.add(loftInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))