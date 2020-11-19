#!/usr/bin/env python3

import os, copy
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))

import gvxrPython3 as gvxr
import inp2stl

# Define the NoneType
NoneType = type(None);


# Print the libraries' version
print (gvxr.getVersionOfSimpleGVXR())
print (gvxr.getVersionOfCoreGVXR())

# Create an OpenGL context
print("Create an OpenGL context")
gvxr.createWindow();
gvxr.setWindowSize(512, 512);


# Set up the beam
print("Set up the beam")
gvxr.setSourcePosition(-40.0,  0.0, 0.0, "cm");
#gvxr.usePointSource();
gvxr.useParallelBeam();
gvxr.setMonoChromatic(0.08, "MeV", 1000);

# Set up the detector
print("Set up the detector");
gvxr.setDetectorPosition(40.0, 0.0, 0.0, "cm");
gvxr.setDetectorUpVector(0, 0, -1);
gvxr.setDetectorNumberOfPixels(640, 320);
gvxr.setDetectorPixelSize(0.5, 0.5, "mm");



# Load the data
print("Load the data from the INP file");
vertex_set, triangle_index_set, material_set = inp2stl.readInpFile('male_model.inp', True);
inp2stl.writeStlFile("male_model.stl", vertex_set, triangle_index_set[0]);

# Get the bounding box
min_corner = None;
max_corner = None;

vertex_set = np.array(vertex_set).astype(np.float32);

for triangle in triangle_index_set[0]:
    for vertex_id in triangle:


        if isinstance(min_corner, NoneType):
            min_corner = copy.deepcopy(vertex_set[vertex_id]);
        else:
            min_corner[0] = min(min_corner[0], vertex_set[vertex_id][0]);
            min_corner[1] = min(min_corner[1], vertex_set[vertex_id][1]);
            min_corner[2] = min(min_corner[2], vertex_set[vertex_id][2]);

        if isinstance(max_corner, NoneType):
            max_corner = copy.deepcopy(vertex_set[vertex_id]);
        else:
            max_corner[0] = max(max_corner[0], vertex_set[vertex_id][0]);
            max_corner[1] = max(max_corner[1], vertex_set[vertex_id][1]);
            max_corner[2] = max(max_corner[2], vertex_set[vertex_id][2]);

# Compute the bounding box
bbox_range = [max_corner[0] - min_corner[0],
    max_corner[1] - min_corner[1],
    max_corner[2] - min_corner[2]];


# print("X Range:", min_corner[0], "to", max_corner[0], "(delta:", bbox_range[0], ")")
# print("Y Range:", min_corner[1], "to", max_corner[1], "(delta:", bbox_range[1], ")")
# print("Z Range:", min_corner[2], "to", max_corner[2], "(delta:", bbox_range[2], ")")

# Centre the mesh
for vertex_id in range(len(vertex_set)):
    vertex_set[vertex_id][0] -= min_corner[0] + bbox_range[0] / 2.0;
    vertex_set[vertex_id][1] -= min_corner[1] + bbox_range[1] / 2.0;
    vertex_set[vertex_id][2] -= min_corner[2] + bbox_range[2] / 2.0;

gvxr.makeTriangularMesh("male_model",
		np.array(vertex_set).astype(np.float32).flatten(),
		np.array(triangle_index_set).astype(np.int32).flatten(),
	    "m");

# The model is made of Hydrogen
gvxr.setElement("male_model", "H");

# Add the mesh to the simulation
gvxr.addPolygonMeshAsInnerSurface("male_model");

# Compute an X-ray image, update the 3D visualisation, and rotate the object
gvxr.renderLoop();

projections = [];
for i in range(180):
    # Compute an X-ray image and add it to the list of projections
    projections.append(gvxr.computeXRayImage());

    # Save the X-ray image
    gvxr.saveLastXRayImage("male_model_projection_" + '{0:03d}'.format(i) + ".dcm");

    # Update the 3D visualisation
    gvxr.displayScene();

    # Rotate the model by 1 degree
    gvxr.rotateNode("male_model", 1, 0, 0, -1);

# Display the 3D scene (no event loop)
# Run an interactive loop
# (can rotate the 3D scene and zoom-in)
# Keys are:
# Q/Escape: to quit the event loop (does not close the window)
# B: display/hide the X-ray beam
# W: display the polygon meshes in solid or wireframe
# N: display the X-ray image in negative or positive
# H: display/hide the X-ray detector
gvxr.renderLoop();
