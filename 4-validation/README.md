---
title: Quantitative validation of gVirtualXRay
author: Dr Franck P. Vidal
subtitle: Presented as IBSim-4i 2020
date: 13th Aug 2020
institute: Bangor University
---

# Contents


- [Recording of this talk](#Recording-of-this-talk)
- [Quantitative Validation](#Quantitative-Validation)
- [Density for Different Materials (human tissues) from the Literature](#Density-for-Different-Materials-human-tissues-from-the-Literature)
    - [Mass Attenuation Coefficients](#Mass-Attenuation-Coefficients)
    - [Mass Attenuation Coefficients: Tissue, Soft (ICRU-44)](#Mass-Attenuation-Coefficients-Tissue-Soft-ICRU-44)
    - [Mass Attenuation Coefficients: Bone, Cortical (ICRU-44)](#Mass-Attenuation-Coefficients-Bone-Cortical-ICRU-44)
- [More testing](#More-testing)
    - [Test case](#Test-case)
    - [Beer-Lambert Law: Polychromatism Case](#Beer-Lambert-Law-Polychromatism-Case)
    - [Gate vs. gVirtualXRay](#Gate-vs-gVirtualXRay)
        - [Point Source](#Gate-vs-gVirtualXRay-Point-Source)
        - [Uncentered Source](#Gate-vs-gVirtualXRay-Uncentered-Source)
        - [Cube Source](#Gate-vs-gVirtualXRay-Cube-Source)
- [Unit tests](#Unit-tests)

# Recording of this talk

[![Watch the video](https://img.youtube.com/vi/vRYi1dFCqcU/0.jpg)](https://youtu.be/vRYi1dFCqcU "Quantitative validation of gVirtualXRay")

# Quantitative Validation

- Simulating an image relies on a Beer-Lambert law implementation;
- Solving the Beer-Lambert law relies on Linear Attenuation Coefficients; (&mu;)
- &mu; is not known for given incident energies;
- &mu; is computed using Mass Attenuation Coefficients (&mu;/&rho;) and material density (&rho;).
- **Are the values used in gVirtualXRay accurate?**
    - Compare values computed in gVirtualXRay with those from the literature.
- **Are the Beer-Lambert law implementations accurate?**
    - Compare values computed in gVirtualXRay with theoretical ones.
- **Are the simulated images accurate?**
    - Compare images computed using gVirtualXRay with those using a state-of-the-art Monte Carlo software, e.g.

    [![Geant4](img/g4logo-web.png)](https://geant4.web.cern.ch/)


# Density for Different Materials (human tissues) from the Literature
![*Image from  W. Schneider, T. Bortfeld, and W. Schlegel, “Correlation between CT numbers and tissue parameters needed for Monte Carlo simulations of clinical dose distributions,” Physics in Medicine & Biology, vol. 45, no. 2, p. 459, 2000. doi:[10.1088/0031-9155/45/2/314](http://doi.org/10.1088/0031-9155/45/2/314)*](img/rho_reference.png)

# Density for Different Materials (human tissues) computed by gVirtualXRay

![*Image from [http://gvirtualxray.sourceforge.net/validation/validation_02/density.php](http://gvirtualxray.sourceforge.net/validation/validation_02/density.php)*](img/figure5b.png)





# Mass Attenuation Coefficients

- Any tissue can be described by its Hounsfiled Unit (HU):
  - HU(material) = 1000 x (&mu;(material) - &mu;(water)) / &mu;(water)
- Given a HU value for any simulated object;
  - If &mu;(water) is known for any energy,
  - then &mu;(material) for any HU and for any energy can be computed:
    - &mu;(material, E) = &mu;(water, E) x (1 + HU(material)/1000)
- 	Mass attenuation coefficients (&mu;/&rho;) for various human tissues can be found in the literature;
- 	The density (&rho;) for various human tissues can be found in the literature.
- **Linear attenuation coefficients can therefore be computed for various human tissues** and
- **used to solve the Beer-Lambert law**

# Mass Attenuation Coefficients: Tissue, Soft (ICRU-44)

- ![*Image from [https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/tissue.html](https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/tissue.html)*](img/tissue.png)

- &mu;(water) from literature is provided at given energies only: Interpolation needed for missing energies

  - ![*Image computed with gVirtualXRay using linear interpolation*](img/test_soft_tissue_1.png)

  - ![*Image computed with gVirtualXRay using interpolation in the log scale*](img/test_soft_tissue_2.png)


# Mass Attenuation Coefficients: Bone, Cortical (ICRU-44)

- ![*Image from [https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/bone.html](https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/bone.html)*](img/bone.png)

- &mu;(water) from literature is provided at given energies only: Interpolation needed for missing energies

  - ![*Image computed with gVirtualXRay using linear interpolation*](img/test_bone_1.png)

  - ![*Image computed with gVirtualXRay using interpolation in the log scale*](img/test_bone_2.png)

**Not a good match as the peaks are not visible in &mu;(water)**

- ![*Image computed with gVirtualXRay using NIST's XCOM database*](img/test_bone_3.png)

**This is now a good match**


# Going back to previous slide

- Simulating an image relies on a Beer-Lambert law implementation;
- Solving the Beer-Lambert law relies on Linear Attenuation Coefficients; (&mu;)
- &mu; is not known for given incident energies;
- &mu; is computed using Mass Attenuation Coefficients (&mu;/&rho;) and material density (&rho;).
- **Are the values used in gVirtualXRay accurate?**
    - Compare values computed in gVirtualXRay with those from the literature.

# Going back to previous slide

- Simulating an image relies on a Beer-Lambert law implementation;
- Solving the Beer-Lambert law relies on Linear Attenuation Coefficients; (&mu;)
- &mu; is not known for given incident energies;
- &mu; is computed using Mass Attenuation Coefficients (&mu;/&rho;) and material density (&rho;).
- **Are the values used in gVirtualXRay accurate?**
    - Compare values computed in gVirtualXRay with those from the literature.
    - **YES**

# More testing

- **Are the Beer-Lambert law implementations accurate?**
    - Compare values computed in gVirtualXRay with theoretical ones.
- **Are the simulated images accurate?**
    - Compare images computed using gVirtualXRay with those using a state-of-the-art Monte Carlo software, e.g.

    [![Geant4](img/g4logo-web.png)](https://geant4.web.cern.ch/)


# Test case

- Simulated object

  ![*Simulated object*](img/validation_3D_scene.png)

  - Cube: edge length of 3 cm, made of soft tissue (HU = 52).
  - Cylinder: height of 3 m, diameter of 2 cm, made of bone (HU = 1330).
- Incident beam:

| N: number of photons | E: energy (in MeV) |
|----------------------|--------------------|
| 10                   | 0.1                |
| 20                   | 0.2                |
| 10                   | 0.3                |


# Beer-Lambert Law: Polychromatism Case

- Use material properties from the literature;
- The energy, I<sub>out</sub>, (in MeV) transmitted orthogonally throw the middle of cube and cylinder should be:
  - I<sub>out</sub> = I<sub>out</sub>(0.1) + I<sub>out</sub>(0.2) + I<sub>out</sub>(0.3), with
  - I<sub>out</sub>(0.1) =    10 x 0.1 x e<sup>-( 3.346E-01 x 2 + 1.799E-01 x 1)</sup>
  - I<sub>out</sub>(0.2)  =    10 x 0.1 x e<sup>-( 2.361E-01 x 2 + 1.443E-01 x 1)</sup>
  - I<sub>out</sub>(0.3)  =    10 x 0.1 x e<sup>-( 2.008E-01 x 2 + 1.249E-01 x 1)</sup>
  - I<sub>out</sub> = 4.359
- On GPU, the energy, I<sub>out<sub>gpu</sub></sub>, is: 4.353.
   - The relative error is:
   - |I<sub>out</sub> - I<sub>out<sub>gpu</sub></sub>| / I<sub>out</sub> = 0.1&percnt;

# Gate vs. gVirtualXRay

We simulate a test case twice:

- Using a Monte Carlo method for particle physics implemented in [GATE](http://www.opengatecollaboration.org/);
- Using our GPU implementation.

*GATE is an opensource software developed by an international collaboration. Its focus is on Monte Carlo simulation in medical imaging and radiotherapy. GATE makes use of the Geant4 libraries. Geant 4 is CERN's Monte Carlo simulation platform dedicated to particle physics in nuclear research. CERN is the European Organization for Nuclear Research.*

# Gate vs. gVirtualXRay: Point Source

![*Simulation parameters*](img/POINT_SOURCE/scene.png)

![*Image computed with GATE (2 weeks of computations on supercomputer)*](img/POINT_SOURCE/gate_norm.png)

![*Image computed with gVirtualXRay (less than 1 sec. of computations on GPU)*](img/POINT_SOURCE/gpu_norm.png)

Normalised cross-correlation (NCC) = 99.747&percnt;

![*Profiles*](img/POINT_SOURCE/test_profile.png)

# Gate vs. gVirtualXRay: Uncentered Source

The source is translated by a vector: -5.0 0.5 0.5 cm

![*Image computed with GATE (2 weeks of computations on supercomputer)*](img/UNCENTRED_SOURCE/gate_norm.png)

![*Image computed with gVirtualXRay (less than 1 sec. of computations on GPU)*](img/UNCENTRED_SOURCE/gpu_norm.png)

Normalised cross-correlation (NCC) = 99.656&percnt;

![*Profiles*](img/UNCENTRED_SOURCE/test_profile.png)


# Gate vs. gVirtualXRay: Cube Source

The source is a 1x1x1 cm cube.

![*Image computed with GATE (2 weeks of computations on supercomputer)*](img/CUBE_SOURCE/gate_norm.png)

![*Image computed with gVirtualXRay (less than 1 sec. of computations on GPU)*](img/CUBE_SOURCE/gpu_norm.png)

Normalised cross-correlation (NCC) = 99.743&percnt;

![*Profiles*](img/CUBE_SOURCE/test_profile.png)


# Unit tests

- More validation test available, see [http://gvirtualxray.sourceforge.net/validation/validation_tests.php](http://gvirtualxray.sourceforge.net/validation/validation_tests.php)
- To check that your system provides the results you expect,
- Run the unit tests
  - See next topic

# Back to main menu

[Click here](../README.md)
