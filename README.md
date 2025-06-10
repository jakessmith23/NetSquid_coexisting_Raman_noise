# NetSquid_coexisting_Raman_noise

Refer to the *Raman Sim Documentation* file for full documentation of this repo.
Refer to the pre-print, "*Simulating Raman Scattering Impairments with Depolarization Noise in Quantum-Classical Links*" for a full theoretical explanation of the methods employed in the code.

Please refer to the *Coexisting Raman Sim Documentation* .pdf for guidance.

## Overview
This code simulates quantum communication experiments utilizing coexistence with classical signals, such as in fiber optic links carrying both quantum and classical data. This is modelled using the depolarization channel.
For a complete theoretical explanation of the methods employed, read the associated pre-print: “Simulating Raman Scattering Impairments with Depolarization Noise in Quantum-Classical Links” [1].

The main entry point is:
*characterized_coex_sim.py*

Raman gain is estimated from experimental measurements, with data available in *RAMAN_Charact.xlsx*.

This script allows the user to run 3 types of coexistence experiments:
Direct Transmission (*import_coexisting_direct_transmission*)
Entanglement Distribution (*import_coexisting_entanglement*)
Teleportation (*import_coexisting_teleportation*)

Both simulate how Raman noise, modeled as depolarization, affects a pure quantum state's fidelity, based on input visibility values. There are also support functions for analytically estimating a hardware setup's visibility from input hardware parameters.



## Citations
1. Smith, J., & Proietti, R. Simulating Raman Scattering Impairments with Depolarization Noise in Quantum-Classical Links. Photonics in Switching and Computing (2025). To Appear.

2. Thomas, J. M., Yeh, F. I., Chen, J. H., Mambretti, J. J., Kohlert, S. J., Kanter, G. S., & Kumar, P. (2024). Quantum teleportation coexisting with classical communications in optical fiber. Optica, 11(12), 1700-1707.

