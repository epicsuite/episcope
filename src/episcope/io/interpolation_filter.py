INTERPOLATION_FILTER_SOURCE = """
import vtk

def RequestData():
    # Get input and output of the programmable filter
    inputPolyData = self.GetInputDataObject(0, 0)
    outputPolyData = self.GetPolyDataOutput()

    # Retrieve points from the input vtkPolyData
    points = inputPolyData.GetPoints()

    # Check if points exist
    if not points or points.GetNumberOfPoints() == 0:
        print("No points found in the input data.")
        return

    # Adjust the number of points to interpolate
    numberOfOutputPoints = 10 * points.GetNumberOfPoints()

    # Spline for each coordinate
    xSpline = vtk.vtkCardinalSpline()
    ySpline = vtk.vtkCardinalSpline()
    zSpline = vtk.vtkCardinalSpline()

    # Add points to the splines
    for i in range(points.GetNumberOfPoints()):
        pt = points.GetPoint(i)
        xSpline.AddPoint(i, pt[0])
        ySpline.AddPoint(i, pt[1])
        zSpline.AddPoint(i, pt[2])

    # Create new vtkPoints for interpolated points
    newPoints = vtk.vtkPoints()
    step = (points.GetNumberOfPoints() - 1) / float(numberOfOutputPoints - 1)
    interpolatedPointsIndexes = []
    for i in range(numberOfOutputPoints):
        t = i * step
        interpolatedPointsIndexes.append(t)
        newPoints.InsertPoint(i, xSpline.Evaluate(t), ySpline.Evaluate(t), zSpline.Evaluate(t))

    # Prepare to copy the point data
    newPointData = vtk.vtkPointData()
    newPointData.CopyStructure(inputPolyData.GetPointData())

    # Allocate memory for the new point data arrays
    for j in range(newPointData.GetNumberOfArrays()):
        arr = newPointData.GetArray(j)
        if arr:
            arr.SetNumberOfTuples(numberOfOutputPoints)
        # Assign values based on the closest original point in 1D parameter space
        for i, t in enumerate(interpolatedPointsIndexes):
            originalPointIndex = int(round(t))
            # Clamp the index to be within bounds
            originalPointIndex = int(max([0, min([originalPointIndex, points.GetNumberOfPoints() - 1])]))          

            for k in range(arr.GetNumberOfComponents()):
                arr.SetComponent(i, k, inputPolyData.GetPointData().GetArray(j).GetComponent(originalPointIndex, k))

    # Create a vtkPolyLine to connect the interpolated points
    polyLine = vtk.vtkPolyLine()
    polyLine.GetPointIds().SetNumberOfIds(numberOfOutputPoints)
    for i in range(numberOfOutputPoints):
        polyLine.GetPointIds().SetId(i, i)

    # Create a vtkCellArray to store the line
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)

    # Set points, cells (lines), and point data to the output vtkPolyData
    outputPolyData.SetPoints(newPoints)
    outputPolyData.SetLines(cells)
    for j in range(newPointData.GetNumberOfArrays()):
        outputPolyData.GetPointData().AddArray(newPointData.GetArray(j))

# Make sure to call the function to execute the code
RequestData()
"""
