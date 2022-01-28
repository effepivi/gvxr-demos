#!/usr/bin/env python3
# coding: utf-8

# In[1]:



import GPUtil
from cpuinfo import get_cpu_info
import platform
import psutil


# In[2]:


def printSystemInfo():
    print("OS:")
    print("\t" + platform.system(), platform.release())
    print("\t" + platform.machine() + "\n")

    print("CPU:\n", "\t" + get_cpu_info()["brand_raw"] + "\n")

    print("RAM:\n\t" + str(round(psutil.virtual_memory().total / (1024.0 **3))), "GB")

    print("GPU:")
    for gpu in GPUtil.getGPUs():
        print("\tName:", gpu.name)
        print("\tDrivers:", gpu.driver)
        print("\tVideo memory:", round(gpu.memoryTotal / 1024), "GB")


# # Realistic simulation of X-ray radiographs using gVirtualXRay
# ## With a realistic beam spectrum and taking into account the energy response of the detector
# ### Authors: F. P. Vidal and J. M. Létang
#
# **Purpose:** In this notebook, we aim to demonstrate how to use gVirtualXRay to generate analytic simulations on GPU. We take into account i) a realistic anatomical phantom, ii) a realistic clinical scenario, iii) a realistic beam spectrum,  and iv) the energy response of the detector.
#
# **Material and Methods:** We downloaded the paediatric phantom from the [p**E**diat**R**ic dosimet**R**y personalized platf**OR**m (ERROR) project](https://error.upatras.gr/). It corresponds to the anatomy of a 5 year old boy. We generated surfaces meshes from the segmented data using [VTK](https://www.vtk.org/). We used the definitions of tissue substitutes provided in the [ICRU Report 44](https://www.icru.org/report/tissue-substitutes-in-radiation-dosimetry-and-measurement-report-44/) by the [International Commission on Radiation Units and Measurements](https://www.icru.org/). The material composition is available at [https://physics.nist.gov/PhysRefData/XrayMassCoef/tab2.html](https://physics.nist.gov/PhysRefData/XrayMassCoef/tab2.html).

# In[3]:


# Image(filename="pediatric_model.png", width=800)


# In our simulation the source-to-object distance (SOD) is 1000mm, and the source-to-detector distance (SDD) is 1125mm. The beam spectrum is polychromatic. The voltage is 85 kV. The filteration is 0.1 mm of copper and 1 mm of aluminium. The energy response of the detector is considered. It mimics a 600-micron thick CsI scintillator.

# In[4]:


# Image(filename="pediatric-setup.png")


# **Results:** The calculations were performed on the following platform:

# In[5]:


printSystemInfo()


# ## Import packages

# In[6]:


import os # Locate files

import math
import numpy as np # Who does not use Numpy?
import pandas as pd # Load/Write CSV files

import urllib, zipfile

from time import sleep

import matplotlib

import matplotlib.pyplot as plt # Plotting
from matplotlib.colors import LogNorm # Look up table
from matplotlib.colors import PowerNorm # Look up table

from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

font = {'family' : 'serif',
        #'weight' : 'bold',
         'size'   : 22
       }
matplotlib.rc('font', **font)
matplotlib.rc('text', usetex=True)


from tifffile import imsave # Write TIFF files

import datetime # For the runtime

import SimpleITK as sitk
from stl import mesh

from sitk2vtk import sitk2vtk
import vtk

import gvxrPython3 as gvxr # Simulate X-ray images
import json2gvxr # Set gVirtualXRay and the simulation up


# ## Setting up gVirtualXRay
#
# Before simulating an X-ray image using gVirtualXRay, we must create an OpenGL context.

# In[7]:


json2gvxr.initGVXR("configuration.json", "OPENGL")


# ## X-ray source
#
# We create an X-ray source. It is a point source.

# In[8]:


json2gvxr.initSourceGeometry()


# ## Spectrum
#
# The spectrum is polychromatic.

# In[9]:


spectrum, unit, k, f = json2gvxr.initSpectrum(verbose=0)
energy_set = sorted(spectrum.keys())

count_set = []

for energy in energy_set:
    count_set.append(spectrum[energy])


# Plot the spectrum

# In[10]:


plt.figure(figsize= (20,10))

plt.bar(k, 100 * f / f.sum()) # Plot the spectrum
plt.xlabel('Energy in keV')
plt.ylabel('Probability distribution of photons per keV (in %)')
plt.title('Photon energy distribution')

# plt.xlim(())

plt.tight_layout()


# ## Detector
#
# Create a digital detector

# In[11]:


json2gvxr.initDetector()


# ## Model the energy response of the detector
#
# Load the energy response

# In[12]:


detector_response = np.loadtxt(json2gvxr.params["Detector"]["Energy response"]["File"])


# Display the energy response

# In[13]:


plt.figure(figsize= (20,10))
# plt.title("Detector response")
plt.plot(detector_response[:,0] * 1000, detector_response[:,1] * 1000)
plt.xlabel('Incident energy: E (in keV)')
plt.ylabel('Detector energy response: $\\delta$(E) (in keV)')

plt.tight_layout()


# ## Sample
#
# Download and unzip the phantom

# In[14]:


if not os.path.exists("pediatric_phantom_data"):
    os.mkdir("pediatric_phantom_data")

if not os.path.exists("pediatric_phantom_data/Pediatric phantom.zip"):
    urllib.request.urlretrieve("https://drive.uca.fr/f/384a08b5f73244cf9ead/?dl=1", "pediatric_phantom_data/Pediatric phantom.zip")

    with zipfile.ZipFile("pediatric_phantom_data/Pediatric phantom.zip","r") as zip_ref:
        zip_ref.extractall("pediatric_phantom_data")


# Load the phantom

# In[15]:


phantom = sitk.ReadImage("pediatric_phantom_data/Pediatric phantom/Pediatric_model.mhd")


# Load the labels

# In[16]:


df = pd.read_csv("labels.dat")


# Process every structure of the phantom

# In[17]:


# A function to extract an isosurface from a binary image
def extractSurface(vtk_image, isovalue):

    iso = vtk.vtkContourFilter()
    if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
        iso.SetInputData(vtk_image)
    else:
        iso.SetInput(vtk_image)

    iso.SetValue(0, isovalue)
    iso.Update()
    return iso.GetOutput()

# A function to write STL files
def writeSTL(mesh, name):
    """Write an STL mesh file."""
    try:
        writer = vtk.vtkSTLWriter()
        if vtk.vtkVersion.GetVTKMajorVersion() >= 6:
            writer.SetInputData(mesh)
        else:
            writer.SetInput(mesh)
        writer.SetFileTypeToBinary()
        writer.SetFileName(name)
        writer.Write()
        writer = None
    except BaseException:
        print("STL mesh writer failed")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(
            exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
    return None


# In[18]:


if not os.path.exists("pediatric_phantom_data/meshes"):
    os.mkdir("pediatric_phantom_data/meshes")

if not os.path.exists("pediatric_phantom_data/segmentations"):
    os.mkdir("pediatric_phantom_data/segmentations")

meshes = []

for threshold, organ in zip(df["Label"], df["Organs"]):

    # Ignore air
    if organ != "Air":

        print("Process", organ)

        seg_fname = "pediatric_phantom_data/segmentations/" + organ + ".mha"
        mesh_fname = "pediatric_phantom_data/meshes/" + organ + ".stl"
        meshes.append(mesh_fname)

        # Only create the mesh if it does not exist
        if not os.path.exists(mesh_fname):

            # Threshold the phantom
            binary_image = (phantom == threshold)

            # Smooth the binary segmentation
            smoothed_binary_image = sitk.AntiAliasBinary(binary_image)

            # Create a VTK image
            vtkimg = sitk2vtk(smoothed_binary_image, centre=True)

            vtk_mesh = extractSurface(vtkimg, 0)
            writeSTL(vtk_mesh, mesh_fname)


# Load the samples. `verbose=2` is used to print the material database for Gate. To disable it, use `verbose=0` or `verbose=1`.

# In[19]:


json2gvxr.initSamples(verbose=0)


# Visualise the phantom

# In[20]:



# ## Runing the simulation
#
# Update the 3D visualisation and take a screenshot

# In[22]:


gvxr.enableArtefactFilteringOnGPU()
xray_image = np.array(gvxr.computeXRayImage())


# Save an X-ray image

# In[23]:


if not os.path.exists("output"):
    os.mkdir("output")

imsave('output/projection-raw.tif', xray_image.astype(np.single))


# Flat-field correction

# In[24]:


total_energy_in_MeV = gvxr.getTotalEnergyWithDetectorResponse()


# In[25]:


white = np.ones(xray_image.shape) * total_energy_in_MeV
dark = np.zeros(xray_image.shape)

xray_image_flat = (xray_image - dark) / (white - dark)


# Save the corresponding image

# In[26]:


imsave('output/projection-flat.tif', xray_image_flat.astype(np.single))


# ## Display the X-ray image

# In[27]:


gamma = 2

vmin = xray_image_flat.min()
vmax = xray_image_flat.max()

fig_plot = plt.figure(figsize= (20,10))

plt.suptitle("Image simulated using gVirtualXRay", y=0.95)
ax = plt.subplot(131)
plt.imshow(xray_image_flat, cmap="gray")
plt.colorbar(orientation='horizontal')
ax.set_title("Using a linear colour scale")

ax_img = plt.subplot(132)
plt.imshow(xray_image_flat, norm=PowerNorm(gamma=1./gamma), cmap="gray")
plt.colorbar(orientation='horizontal')
ax_img.set_title("Using a Power-law colour scale")

ax = plt.subplot(133)
plt.imshow(xray_image_flat, norm=LogNorm(vmin=vmin, vmax=vmax), cmap="gray")
plt.colorbar(orientation='horizontal')
ax.set_title("Using a Log scale")


plt.tight_layout()
plt.savefig('xray_image.png')


# ## Visualisation using gVirtualXRay

# In[28]:


gvxr.displayScene()

gvxr.useLighing()
gvxr.useWireframe()
gvxr.setZoom(1549.6787109375)

angle = math.pi / 2.0
rotation_matrix_x = np.array([ 1, 0, 0, 0,
                               0, math.cos(angle), -math.sin(angle), 0,
                               0, math.sin(angle),  math.cos(angle), 0,
                               0, 0, 0, 1])

rotation_matrix_z = np.array([ math.cos(angle), -math.sin(angle), 0, 0,
                               math.sin(angle),  math.cos(angle), 0, 0,
                               0, 0, 1, 0,
                               0, 0, 0, 1])

rotation_matrix_x.shape = [4,4]
rotation_matrix_z.shape = [4,4]

transformation_matrix = np.identity(4)

transformation_matrix = np.matmul(rotation_matrix_x, transformation_matrix)
transformation_matrix = np.matmul(rotation_matrix_z, transformation_matrix)

gvxr.setSceneRotationMatrix(transformation_matrix.flatten())

gvxr.setWindowBackGroundColour(1, 1, 1)

gvxr.displayScene()


# In[29]:


screenshot = (255 * np.array(gvxr.takeScreenshot())).astype(np.uint8)


# In[30]:


fname = 'screenshot.png'

if not os.path.isfile(fname):
    plt.imsave(fname, screenshot)


# In[31]:


# Image(filename="screenshot.png")


# In[32]:


gvxr.setZoom(1549.6787109375)
gvxr.setSceneRotationMatrix([-0.19267332553863525, -0.06089369207620621, 0.9793692827224731,  0.0,
                              0.9809651970863342,  -0.03645244985818863, 0.19072122871875763, 0.0,
                              0.02408679760992527,  0.9974713325500488,  0.06675821542739868, 0.0,
                              0.0,                  0.0,                 0.0,                 1.0])

gvxr.setWindowBackGroundColour(0.5, 0.5, 0.5)

gvxr.useNegative()

gvxr.displayScene()


# In[33]:


plt.figure(figsize= (10,10))
plt.title("Screenshot")
plt.imshow(gvxr.takeScreenshot())
plt.axis('off')

plt.tight_layout()


# In[34]:


fname = 'screenshot-negative.png'

if not os.path.isfile(fname):
    plt.imsave(fname, (255 * np.array(screenshot)).astype(np.uint8))


# Compute an X-ray image 50 times (to gather performance statistics)

# In[ ]:


runtimes = []

for i in range(50):
    start_time = datetime.datetime.now()
    gvxr.computeXRayImage()
    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    runtimes.append(delta_time.total_seconds() * 1000)


# In[ ]:


runtime_avg = round(np.mean(runtimes))
runtime_std = round(np.std(runtimes))


# ## Runtime

# In[ ]:


printSystemInfo()


# In[ ]:


print("Average:", runtime_avg, "ms")
print("Standard deviation:", runtime_std, "ms")


plt.show()


# ## All done
#
# Destroy the window

# In[ ]:


gvxr.destroyAllWindows()
