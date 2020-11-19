#!/usr/bin/env python3

# Use Matplotlib
try:
    import matplotlib
    matplotlib.use("TkAgg")

    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    from matplotlib.colors import LogNorm
    from matplotlib.colors import PowerNorm
    use_matplotlib = True;
except ImportError:
    print("Matplotlib is not installed. Try to install it if you want to display and plot data.")
    use_matplotlib = False;

import gvxrPython3 as gvxr


# Print the libraries' version
print (gvxr.getVersionOfSimpleGVXR())
print (gvxr.getVersionOfCoreGVXR())

# Create the subplot first
# If called later, it crashes on my Macbook Pro
if use_matplotlib:
    plt.subplot(131)

# Create an OpenGL context
print("Create an OpenGL context")
gvxr.createWindow();
gvxr.setWindowSize(512, 512);


# Set up the beam
print("Set up the beam")
gvxr.setSourcePosition(-40.0,  0.0, 0.0, "cm");
gvxr.usePointSource();
#gvxr.useParallelBeam();
gvxr.setMonoChromatic(0.08, "MeV", 1000);

# Set up the detector
print("Set up the detector");
gvxr.setDetectorPosition(10.0, 0.0, 0.0, "cm");
gvxr.setDetectorUpVector(0, 0, -1);
gvxr.setDetectorNumberOfPixels(640, 320);
gvxr.setDetectorPixelSize(0.5, 0.5, "mm");

# Load the data
print("Load the data");
gvxr.loadSceneGraph("welsh-dragon-small.stl", "mm");

# Get the label
label = gvxr.getChildLabel('root', 0);

print("Move ", label, " to the centre");
gvxr.moveToCentre(label);

#print("Move the mesh to the center");
#gvxr.moveToCenter(label);

print("Set ", label, "'s Hounsfield unit");
gvxr.setHU(label, 1000);


# Compute an X-ray image
print("Compute an X-ray image");
x_ray_image = gvxr.computeXRayImage();

# Save the last image into a file
print("Save the last image into a file");
gvxr.saveLastXRayImage("my_beautiful_dragon.mhd");
gvxr.saveLastXRayImage("my_beautiful_dragon.mha");
gvxr.saveLastXRayImage("my_beautiful_dragon.txt");

# Display the image with Matplotlib
if use_matplotlib:
    plt.imshow(x_ray_image, cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a linear colour scale");

    plt.subplot(132)
    plt.imshow(x_ray_image, norm=LogNorm(), cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a log colour scale");

    plt.subplot(133)
    plt.imshow(x_ray_image, norm=PowerNorm(gamma=1./2.), cmap="gray");
    plt.colorbar(orientation='horizontal');
    plt.title("Using a Power-law colour scale");

    plt.show();

# Display the 3D scene (no event loop)
gvxr.displayScene();

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
