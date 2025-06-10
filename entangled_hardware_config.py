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
