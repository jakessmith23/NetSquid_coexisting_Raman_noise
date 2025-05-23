import import_coexisting_direct_transmission as direct
import import_coexisting_entanglement as ent
import import_coexisting_teleportation as tele

# Citations:
# [1] Thomas, Jordan; Yeh, Fei; Chen, Jim; Mambretti, Joe; Kohlert, Scott; Kanter, Gregory; et al. (2024). Supplementary document for Quantum Teleportation Coexisting with Classical Communications in Optical Fiber - 7260233.pdf. Optica Publishing Group. Journal contribution.

# necessary hardware parameters to calculate noisy coexisting visibility
# example parameters from experiment in [1] provided
hardware_params = {
  'alice_fibre_raman_photons_per_det_window' : 10**5 * 1e-9 * .5, # [photons / det_window]
  'bob_fibre_raman_photons_per_det_window' : 10**5 * 1e-9 * .5, # [photons / det_window]
  'dark_counts_per_gate' : 50 * 1e-9 ,# [ns]
  'detection_eff_d0' : -7.41, # detector 0 detection efficiency [dB],
  'mean_noise_photons_per_interval_d0' : 0,
  'mean_noise_photons_per_interval_d3' : 0,
  'detection_eff_d3' : -12.88, # detector 3 detection efficiency [dB],
  'alice_fibre_loss' : -10.81, # loss from Alice's source to beamsplitter [dB]
  'bob_fibre_loss' : -10.64, # loss from Bob's source to beamsplitter [dB]
  'mean_photons_per_pulse_Alice' : .018,
  'mean_photons_per_pulse_Bob' : .013,
  'mean_noise_photons_per_pulse_Alice' : .0027,
  'mean_noise_photons_per_pulse_Bob' : .0022,
  'receiver_transmittance_d0' : -5.1, # transmittance of optical elements at receiver 0 [dB]
  'receiver_transmittance_d3' : -5, # transmittance of optical elements at receiver 3 [dB]
  'total_transmittance_n0' : .19, # total transmittance from Alice --> d0 [%]
  'total_transmittance_n3' : .05, # total transmittance from Bob --> d3 [%]
  'detection_eff_d1' : -5.65, # detector 1 detection efficiency [dB],
  'detection_eff_d2' : -6.71, # detector 2 detection efficiency [dB],
  'insertion_loss_into_bsm' : -1.2, # [dB]
  'total_transmittance_n1' : .07, # total transmittance from Alice --> d1 [%]
  'total_transmittance_n2' : .09, # total transmittance from Bob --> d2 [%]
}


if __name__ == "__main__":
  ###### >> To run coexisting direct transmission experiment
  #depolarized_fidelity, depolarized_state = direct.run_coex_direct_transm_experiment(incident_raman_photons_per_s=0, quantum_photons_incident_per_s=1, detector_gate_time_s=1, random_seed = 1, ket_state="0", verbose=True)


  ###### >> To run coexisting entanglement distribution experiment
  #depolarized_fidelity, depolarized_q1, depolarized_q2  = ent.run_coex_ent_experiment(random_seed = 1, bell_state="psi-", noisy_visibility=1, verbose=True)


  ####### >> To calculate noisy visibility of hardware from hardware_params
  # >> Note: this can be used for entanglement distribution experiment too
  #vis_ent, vis_alice_qubit = tele.calc_visibility(hardware_params)
  
  # >> To run coexisting teleportation experiment
  #depolarized_fidelity, noisy_ent_output_1, noisy_ent_output_2, depolarized_alice_qubit = tele.run_coex_tele_experiment(random_seed = 1, bell_state="psi-", alice_qubit_state="0", noisy_ent_visibility=vis_ent, alice_qubit_noisy_visibility=vis_alice_qubit, verbose=True)