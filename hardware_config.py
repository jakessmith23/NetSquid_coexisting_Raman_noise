# [1] Thomas, J. M., Yeh, F. I., Chen, J. H., Mambretti, J. J., Kohlert, S. J., Kanter, G. S., 
# & Kumar, P. (2024). Quantum teleportation coexisting with classical communications in optical fiber. 
# Optica, 11(12), 1700-1707.

hardware_params = {
  # setup assumes 2 single photon detectors: d0, d1
  # and two links, 0 and 1
  # 0 is the coexisting link, with fibre, receiver optics, and detector 0
  # 1 is the heralding arm, with receiver optics, detector 1, and no fibre

  'raman_photons_per_det_window' : None, # [photons / det_window]
  'fibre_attenuation' : -0.2, # -0.2 dB / km
  'coexisting_fibre_loss' : None, # dB. overwritten in characterized_coex_sim.simulate()
  'dark_counts_per_det_window' : 50 * 1e-9 , # 50 * 1e-9
  'mean_noise_photons_per_interval_d1' : 0, # no noise beyond source noise at heralding arm
  'detection_eff_d0' : -6, # -6 detector 0 detection efficiency [dB],
  'detection_eff_d1' : -6, # detector 1 detection efficiency [dB],
  'mean_photons_per_pulse' : .013, # .013
  'mean_noise_photons_per_pulse' : .0022, # .0022
  'receiver_transmittance_d0' : 0, # transmittance of optical elements at receiver 0 [dB]
  'receiver_transmittance_d1' : 0, # transmittance of optical elements at receiver 1 [dB]
  'detection_window': 5e-10  # 5e-10 500 ps
}
