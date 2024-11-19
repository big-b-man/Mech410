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

        # Create a new sketch on the xy plane.
        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)           

        for i in range (1,21):
            #data parsing
            filename = filepath + 'SectionCurve' + str(i) + '.txt'
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                # Insert X,Y and Z columns into list
                data = [[float(x) for x in row[:3]] for row in reader]
            
            # Create an object collection for the points.
            points = adsk.core.ObjectCollection.create()
            lines = sketch.sketchCurves.sketchLines
            #line = lines.addByTwoPoints(adsk.core.Point3D.create(data[1][0]*100,data[1][1]*100,data[1][2]*100), adsk.core.Point3D.create(data[len(data)-2][0]*100,data[len(data)-2][1]*100,data[len(data)-2][2]*100))
            for j in range (len(data)-1):
                # Define the points the spline with fit through.
                points.add(adsk.core.Point3D.create(data[j][0]*100,data[j][1]*100,data[0][2]*100))
            points.add(adsk.core.Point3D.create(data[0][0]*100,data[0][1]*100,data[0][2]*100))

            # Create the spline.
            spline = sketch.sketchCurves.sketchFittedSplines.add(points)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))