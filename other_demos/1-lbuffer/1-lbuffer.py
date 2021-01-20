#!/usr/bin/env python3

# coding: utf-8

# # Computing the path length in an object

# This tutorial show you how to compute the path length for 3 objects (here from STL files).
#
# ![3D objects](screenshot.png)
#
# We store the parameters of the scanning geometry using a JSON file (`param.json`):
#
# ```json
# {
#   "WindowSize": [512, 512],
#   "Source": {
#     "Position": [-40.0,  0.0, 0.0, "cm"],
#     "Shape": "ParallelBeam"
#   },
#
#   "Detector": {
#     "Position": [40.0, 0.0, 0.0, "cm"],
#     "UpVector": [0, 0, -1],
#     "NumberOfPixels": [641, 320],
#     "Spacing": [0.25, 0.25, "mm"]
#   },
#
#   "Samples": [
#     {
#       "Label": "cubes",
#       "Path": "cubes.stl",
#       "Unit": "mm"
#     },
#
#     {
#       "Label": "gVXR",
#       "Path": "gVXR.stl",
#       "Unit": "mm"
#     },
#
#     {
#       "Label": "spheres",
#       "Path": "spheres.stl",
#       "Unit": "mm"
#     }
#   ]
# }
# ```

# ## Import packages
import argparse  # Process the cmd line

import json # Load the JSON file
import numpy as np # To save the image in ASCII
import SimpleITK as sitk # To save the image in a binary (optional)

import matplotlib # For plotting (optional)
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import gvxrPython3 as gvxr # Simulate X-ray images



def processCmdLine():
    parser = argparse.ArgumentParser(description='Compute the path length using gVirtualXRay (http://gvirtualxray.sourceforge.net/).')
    parser.add_argument('--config', help='JSON file containing parameters of the scanning geometry', nargs=1, type=str, required=True);
    return parser.parse_args()


if __name__ == '__main__':

    # Load the arguments from the command line
    args = processCmdLine();

    # ## Load the JSON file
    print("Load the config file:", args.config[0])
    with open(args.config[0]) as f:
      params = json.load(f)

    # ## Create an OpenGL context
    print("Create an OpenGL context");
    gvxr.createWindow(0, 1, "OPENGL");

    window_size = params["WindowSize"];
    gvxr.setWindowSize(
        window_size[0],
        window_size[1]
    );

    # ## Set up the beam
    print("Set up the beam");
    source_position = params["Source"]["Position"];
    gvxr.setSourcePosition(
        source_position[0],
        source_position[1],
        source_position[2],
        source_position[3]
    );

    source_shape = params["Source"]["Shape"]

    if source_shape == "ParallelBeam":
        gvxr.useParallelBeam();
    elif source_shape == "PointSource":
        gvxr.usePointSource();
    else:
        raise "Unknown source shape:" + source_shape;


    # ## Set up the detector
    print("Set up the detector");
    detector_position = params["Detector"]["Position"];
    gvxr.setDetectorPosition(
        detector_position[0],
        detector_position[1],
        detector_position[2],
        detector_position[3]
    );

    detector_up = params["Detector"]["UpVector"];
    gvxr.setDetectorUpVector(
        detector_up[0],
        detector_up[1],
        detector_up[2]
    );

    detector_number_of_pixels = params["Detector"]["NumberOfPixels"];
    gvxr.setDetectorNumberOfPixels(
        detector_number_of_pixels[0],
        detector_number_of_pixels[1]
    );

    pixel_spacing = params["Detector"]["Spacing"];
    gvxr.setDetectorPixelSize(
        pixel_spacing[0],
        pixel_spacing[1],
        pixel_spacing[2]
    );


    # ## Load the polygon meshes
    print("Load the polygon meshes");
    colours = list(mcolors.TABLEAU_COLORS);
    colour_id = 0;
    for mesh in params["Samples"]:

        print("\t", mesh["Path"])
        gvxr.loadMeshFile(
            mesh["Label"],
            mesh["Path"],
            mesh["Unit"]
        );

        # Add the mesh to the simulation
        gvxr.addPolygonMeshAsInnerSurface(mesh["Label"]);

        # Change the colour
        colour = mcolors.to_rgb(colours[colour_id]);
        gvxr.setColour(mesh["Label"], colour[0], colour[1], colour[2], 1.0);

        colour_id += 1;
        if colour_id == len(colours):
            colour_id = 0;

    # ## Dummy beam spectrum
    print("Add a dummy beam spectrum");
    gvxr.addEnergyBinToSpectrum(1,"keV",10); # 10 photons of 1 keV


    gvxr.renderLoop();

    # ## Compute the path length for every object
    print("Compute the path length for every object");
    path_length = {};
    for mesh in params["Samples"]:
        print("Process", mesh["Label"]);
        path_length[mesh["Label"]] = gvxr.computeLBuffer(mesh["Label"]);


    # ## Save the path length using Numpy
    print("Save the path length using Numpy");
    for key in path_length:
        print("\t", key, "in", key + "_path_length.txt");
        np.savetxt(key + "_path_length.txt", path_length[key]);


    # ## Save the path length using SITK
    print("Save the path length using SimpleITK");
    for key in path_length:
        print("\t", key, "in", key + "_path_length.mha");
        volume = sitk.GetImageFromArray(path_length[key]);
        volume.SetSpacing([pixel_spacing[0], pixel_spacing[1]]);
        sitk.WriteImage(volume, key + "_path_length.mha", useCompression=True);


    # ## Display the path length using Matplotlib
    print("Display the path length using Matplotlib");
    for key in path_length:
        fig=plt.figure();
        imgplot = plt.imshow(path_length[key], cmap="gray");
        plt.title("Path length (in cm) of " + key);
        plt.colorbar();
        plt.savefig(key + "_path_length.pdf");

    plt.show();
