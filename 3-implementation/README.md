---
title: How the X-ray attenuation law was implemented on GPU
author: Dr Franck P. Vidal
subtitle: Presented as IBSim-4i 2020
date: 13th Aug 2020
institute: Bangor University
---

# Contents

- [Recording of this talk](#Recording-of-this-talk)
- [Path Length: Naive Approach](#Path-Length:-Naive-Approach)
- [Path Length: L-Buffer](#Path-Length-L-Buffer)
- [L-Buffer Implementation](#L-Buffer-Implementation)
- [Multipass Rendering Pipeline](#Multipass-Rendering-Pipeline)
- [Adding the Beam Spectrum](#Adding-the-Beam-Spectrum)
- [Simulation with Different Source Shapes](#Simulation-with-Different-Source-Shapes)
- [Final Simulation Flowchart](#Final-Simulation-Flowchart)
- [Bibliography (links)](#Bibliography-links)



# Recording of this talk

[![Watch the video](https://img.youtube.com/vi/RLUg9urgzM0/0.jpg)](https://youtu.be/RLUg9urgzM0 "How the X-ray attenuation law was implemented on GPU")

# Path Length: Naive Approach

![*Is finding intersections in the right order important?*](img/intersections.png)

1. Detect every intersection between a ray and the objects;
2. Sort intersection
(Can be handled by GPUs using depth-peeling, a multi-pass rendering technique for semi-transparent polygonal objects without sorting polygons);
3. Compute path length.


# Path Length: L-Buffer

![*Finding intersections in any order does not matter*](img/l-buffer.png)

**Intersection sorting is actually not needed!**

- By convention normals are outward;
- A ray penetrates into an object when the dot product between the view vector (V) and the normal (N<sub>i</sub>) at the intersection point is positive;
- It leaves an object when the dot product is negative.

# L-Buffer Implementation

L<sub>p</sub>=&Sigma;<sub>i</sub> - sng(V &middot; N<sub>i</sub>) x d<sub>i</sub>


- i refers to i<sup>th</sup> intersection in an arbitrary order;
- d<sub>i</sub> distance from X-ray source to intersection point;
- sgn(V &middot; N<sub>i</sub>) stands for the sign of the dot product between V and N<sub>i</sub>;
- In a shader program, compute:
    - sgn(V &middot; N<sub>i</sub>);
    - d<sub>i</sub> the distance between the X-ray source and the intersection;
    - Assign -sng(V &middot; N<sub>i</sub>) x d<sub>i</sub> as the fragment value.
- For each pixel, compute L<sub>p</sub> thanks to high-dynamic range and OpenGL blending function (pixel values may not be between 0 and 1).

*See [http://dx.doi.org/10.2312/LocalChapterEvents/TPCG/TPCG09/025-032](DOI: 10.2312/LocalChapterEvents/TPCG/TPCG09/025-032) for more details.*


# Multipass Rendering Pipeline

pixel = E x N<sub>out</sub>

pixel =  <span style="color:green">E x N<sub>in</sub>(E) e</span><sup>(<span style="color:red">-&Sigma;<sub>i</sub> &mu;<sub>i</sub> </span> <span style="color:blue">  L<sub>p</sub>(i)</span>)</sup>

- Needs 3 FBOs with high-dynamic range capability for off-line rendering:

- For each object of the scene:
  1. Compute L<sub>p</sub>(i);
  2. Update results of &Sigma; &mu;<sub>i</sub> L<sub>p</sub>(i).
- For the final image only:
  1. Compute N<sub>out</sub>;
  2. (Optional when direct display only is needed).

![*OpenGL pipeline to compute the Beer-Lambert law (monochromatic case).*](img/pipeline1.png)

# Adding the Beam Spectrum

- Take into the different energies within the incident beam;
- This is known as *beam hardening*;
- Iterate over several energy channels:
  - pixel = &Sigma;<sub>j</sub> E<sub>j</sub> x N<sub>out</sub>(E<sub>j</sub>)
  - pixel = &Sigma;<sub>j</sub> E<sub>j</sub> x N<sub>in</sub>(E<sub>j</sub>) e<sup>(-&Sigma;<sub>i</sub> &mu;<sub>i</sub>(E<sub>j</sub>,&rho;,Z) d<sub>i</sub>)</sup>

- Example:

![*Simulation parameters*](img/figure3a.png)

![*Polychromatic beam spectrum for 90kV X-ray tube peak voltage*](img/figure3b.png)

![*Intensity profiles, see dash line in image above*](img/figure3c.png)


# Simulation with Different Source Shapes

- Take into account the focal spot of the X-ray source;
- Iterate over several point sources within the volume of the focal spot:
  - pixel = &Sigma;<sub>k</sub> &Sigma;<sub>j</sub> E<sub>j</sub> x N<sub>in</sub>(E<sub>j</sub>) e<sup>(-&Sigma;<sub>i</sub> &mu;<sub>i</sub>(E<sub>j</sub>,&rho;,Z) d<sub>i</sub>(k))</sup>
  - See blur in the corresponding image below.


| Parallel beam             |  Infinitely small point source | 1<sup>3</sup>mm source |
:-------------------------:|:-------------------------:|:-------------------------:
![](img/figure2a_top.png) |   ![](img/figure2b_top.png)  |   ![](img/figure2c_top.png)
![](img/figure2a_bottom.png) | ![](img/figure2b_bottom.png)| ![](img/figure2c_bottom.png)




# Final Simulation Flowchart

- Iterate over several energy channels: Three extra for loops;
- Iterate over several point sources within the volume of the focal spot: One extra for loop.

![*Final OpenGL pipeline*](img/figure4.png)

# Bibliography (links)

- [DOI: 10.2312/LocalChapterEvents/TPCG/TPCG09/025-032](http://dx.doi.org/10.2312/LocalChapterEvents/TPCG/TPCG09/025-032)
- [DOI: 10.1007/s11548-009-0367-1](http://dx.doi.org/10.1007/s11548-009-0367-1)
- [DOI: 10.2312/egp.20101026](http://dx.doi.org/10.2312/egp.20101026)
- [DOI: 10.1016/j.compmedimag.2015.12.002](https://doi.org/10.1016/j.compmedimag.2015.12.002)

# Back to main menu

[Click here](../README.md)
