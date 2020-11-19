---
title: "Topic 2 -- Theory about X-ray attenuation: The Beer-Lambert Law"
author: Dr Franck P. Vidal
subtitle: IBSim-4i 2020
date: 13th Aug 2020
---

# X-photons/matter Interactions (1/2)

- X-photons cross matter;
- During their path into any material, they can interact with matter.

![*Illustration of X-ray photon/matter interaction*](img/interactions.png)

1. Directly transmitted photons (no interaction);
2. Absorbed photons;
3. Scattered photons;
4. Absorbed scattered photons.

# X-photons/matter Interactions (2/2)

**For most X-rays imaging modalities, only directly transmitted photons are essential:**

- Scattered photons decrease the image quality;
- Absorbed photons do not reach the detector;
- Scattered photons may be ignored (but not necessarily).

![*Illustration of X-ray photon/matter interaction*](img/interactions.png)

1. Directly transmitted photons (no interaction);
2. Absorbed photons;
3. Scattered photons;
4. Absorbed scattered photons.


# Beer-Lambert Law (Attenuation Law)


![*Illustration of the Beer-Lambert law*](img/attenuation.png)

- N<sub>out</sub>(E) = N<sub>in</sub>(E) e<sup>(-&Sigma;<sub>i</sub> &mu;<sub>i</sub>(E,&rho;,Z) L<sub>p</sub>(i))</sup>
  - N<sub>in</sub>(E) the number of incident photons at energy E;
  - N<sub>out</sub>(E) the number of transmitted photons of energy E;
  - &mu;<sub>i</sub> the linear attenuation coefficient (in cm<sup>-1</sup>) of the i<sup>th</sup> object. It depends on:
    - E the energy of incident photons;
    - &rho; the material density of the object;
    - Z the atomic number of the object material.
  - L<sub>p</sub>(i) the path length of the ray in the i<sup>th</sup> object.
- E<sub>out</sub> = N<sub>out</sub>(E) x E
  - E<sub>out</sub> the energy received by the pixel, i.e. as recorded in the X-ray image.

# Example (monochromatic case)

[http://gvirtualxray.sourceforge.net/validation/validation_03/beer_lambert_law_monochromatic.php](http://gvirtualxray.sourceforge.net/validation/validation_03/beer_lambert_law_monochromatic.php)

# Beer-Lambert Law in the polychromatic case

- There are more than one energy in the incident beam spectrum
- Just iterate over the energy channels:

E<sub>out</sub> = &Sigma;<sub>j</sub> E<sub>j</sub> x N<sub>out</sub>(E<sub>j</sub>)

E<sub>out</sub> = &Sigma;<sub>j</sub> E<sub>j</sub> x N<sub>in</sub>(E<sub>j</sub>) e<sup>(-&Sigma;<sub>i</sub> &mu;<sub>i</sub>(E<sub>j</sub>,&rho;,Z) L<sub>p</sub>(i))</sup>

with j the j-th energy channel


# Example (polychromatic case)

[http://gvirtualxray.sourceforge.net/validation/validation_05/beer_lambert_law_polychromatic.php](http://gvirtualxray.sourceforge.net/validation/validation_05/beer_lambert_law_polychromatic.php)

# Back to main menu

[Click here](../README.html#(2))
