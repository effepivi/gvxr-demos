#!/usr/bin/env python3

import os, copy
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))

import math
from skimage.transform import iradon, iradon_sart
import SimpleITK as sitk

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

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
gvxr.setMonoChromatic(33, "keV", 1);

# Set up the detector
print("Set up the detector");
gvxr.setDetectorPosition(40.0, 0.0, 0.0, "cm");
gvxr.setDetectorUpVector(0, 0, -1);
gvxr.setDetectorNumberOfPixels(641, 320);
spacing_in_mm = 0.5;
gvxr.setDetectorPixelSize(spacing_in_mm, spacing_in_mm, "mm");



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

# The model is made of silicon carbide

# Silicon carbide total mass attenuation at 33 keV is 0.855 cm2.g-1.
# Its density is 3.2 g.cm-3.
# The theoretical linear attenuation coefficient is obtained as follows:  0.855 x 3.2 = 2.736 cm-1.

gvxr.setCompound("male_model", "SiC");

gvxr.setDensity("male_model",
                3.2,
                "g/cm3");

# Add the mesh to the simulation
gvxr.addPolygonMeshAsInnerSurface("male_model");

# Compute an X-ray image, update the 3D visualisation, and rotate the object
#gvxr.renderLoop();

projections = [];
theta = [];

number_of_angles = 360;
rotation_angle = 180 / number_of_angles;

for i in range(number_of_angles):
    # Compute an X-ray image and add it to the list of projections
    projections.append(gvxr.computeXRayImage());

    # Update the 3D visualisation
    gvxr.displayScene();

    # Rotate the model by 1 degree
    gvxr.rotateNode("male_model", rotation_angle, 0, 0, -1);

    theta.append(i * rotation_angle);

# Convert the projections as a Numpy array
projections = np.array(projections);

# Retrieve the total energy
energy_bins = gvxr.getEnergyBins("MeV");
photon_count_per_bin = gvxr.getPhotonCountEnergyBins();

total_energy = 0.0;
for energy, count in zip(energy_bins, photon_count_per_bin):
    print(energy, count)
    total_energy += energy * count;

# Perform the flat-field correction of raw data
dark = np.zeros(projections.shape);
flat = np.ones(projections.shape) * total_energy;
projections = (projections - dark) / (flat - dark);

# Calculate  -log(projections)  to linearize transmission tomography data
projections = -np.log(projections)

volume = sitk.GetImageFromArray(projections);
sitk.WriteImage(volume, 'projections-skimage.mhd');

# Resample as a sinogram stack
sinograms = np.swapaxes(projections, 0, 1);

# Perform the reconstruction
# Process slice by slice
recon_fbp = [];
recon_sart = [];
slice_id = 0;
for sinogram in sinograms:
    slice_id+=1;
    print("Reconstruct slice #", slice_id, "/", number_of_angles);
    recon_fbp.append(iradon(sinogram.T, theta=theta, circle=True));

    # Two iterations of SART
    # recon_sart.append(iradon_sart(sinogram.T, theta=theta));
    # recon_sart[-1] = iradon_sart(sinogram.T, theta=theta, image=recon_sart[-1]);

recon_fbp = np.array(recon_fbp);
# recon_sart = np.array(recon_sart);

# Plot the slice in the middle of the volume
plt.figure();
plt.title("FBP")
plt.imshow(recon_fbp[int(projections.shape[1]/2), :, :])
# plt.figure();
# plt.title("SART")
# plt.imshow(recon_sart[int(projections.shape[1]/2), :, :])
plt.show()

# Save the volume
volume = sitk.GetImageFromArray(recon_fbp);
volume.SetSpacing([spacing_in_mm, spacing_in_mm, spacing_in_mm]);
sitk.WriteImage(volume, 'recon-fbp-skimage.mhd');

# volume = sitk.GetImageFromArray(recon_sart);
# volume.SetSpacing([spacing_in_mm, spacing_in_mm, spacing_in_mm]);
# sitk.WriteImage(volume, 'recon-sart-skimage.mhd');

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
