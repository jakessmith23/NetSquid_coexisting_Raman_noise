# NetSquid_coexisting_Raman_noise

Refer to the **Raman Sim Documentation** file for full documentation of this repo.
Refer to the pre-print, "**Simulating Raman Scattering Impairments with Depolarization Noise in Quantum-Classical Links**" for a full theoretical explanation of the methods employed in the code.

## Overview
This code simulates quantum communication experiments utilizing coexistence with classical signals, such as in fiber optic links carrying both quantum and classical data. This is modelled using the depolarization channel.
For a complete theoretical explanation of the methods employed, read the associated pre-print: “Simulating Raman Scattering Impairments with Depolarization Noise in Quantum-Classical Links” [1].

The main entry point is:
run_raman_depolar_sim.py
This script allows the user to run 3 types of coexistence experiments:
Direct Transmission (import_coexisting_direct_transmission)
Entanglement Distribution (import_coexisting_entanglement)
Teleportation (import_coexisting_teleportation)

Both simulate how Raman noise, modeled as depolarization, affects quantum fidelity, based on input visibility values.

## Guidance on Usage
There are two main use cases for this simulator:
1. *Estimating the coexisting fidelity value of a coexisting link configuration (fibre + detector setup):* The user may be interested in comparing the fidelity difference of two hardware configurations (e.g. wavelength channel selections or launch powers and their respective Raman photons received at the detector), perhaps with respect to a minimum fidelity requirement of the protocol. In this case, the simulator requires no modification and input parameters can be tweaked to output the coexisting fidelity. 

2. *Simulating larger network protocols in NetSquid with coexisting links:* If the user is intending to include coexisting noise in link or network layer protocol simulation, this simulator can be forked, or subsections utilized, to apply the appropriate coexisting noise to the transmitted qubits to yield the appropriate noisy coexisting density matrix. 
Both of these cases will follow a similar workflow:
Provided by the user in the API: Determine the number of incident Raman photons at the detector. This is from experimental measurements, or from an estimated number.
Performed by the simulator: Calculates the mixing probability of the link based on the incident Raman photons. Applies depolarization with this mixing probability to NetSquid qubit objects. 
Note: for teleportation using a midpoint Bell-state Measurement, there will be corresponding mixing probabilities for both fibres utilized (Alice’s qubit to be teleported → BSM, Bob’s entangled signal photon → BSM)

Simulator returns depolarized fidelity and depolarized qubit(s).


