import import_coexisting_direct_transmission as direct
import import_coexisting_entanglement as ent
import import_coexisting_teleportation as tele
from entangled_hardware_config import hardware_params  


# Citations:
# [1] Thomas, Jordan; Yeh, Fei; Chen, Jim; Mambretti, Joe; Kohlert, Scott; Kanter, Gregory; et al. (2024). Supplementary document for Quantum Teleportation Coexisting with Classical Communications in Optical Fiber - 7260233.pdf. Optica Publishing Group. Journal contribution.

if __name__ == "__main__":
  ###### >> To run coexisting direct transmission experiment
  depolarized_fidelity, depolarized_state = direct.run_coex_direct_transm_experiment(incident_raman_photons_per_s=0, quantum_photons_incident_per_s=1, detector_gate_time_s=1, random_seed = 1, ket_state="0", verbose=True)


  ###### >> To run coexisting entanglement distribution experiment
  # >> Note: this can be used for teleportation  experiment too
  #vis_ent, _ = tele.calc_visibility(hardware_params)
  #depolarized_fidelity, depolarized_q1, depolarized_q2  = ent.run_coex_ent_experiment(random_seed = 1, bell_state="psi-", noisy_visibility=vis_ent, verbose=True)


  ####### >> To calculate noisy visibility of hardware from hardware_params
  # >> Note: this can be used for entanglement distribution experiment too
  #vis_ent, vis_alice_qubit = tele.calc_visibility(hardware_params)
  
  # >> To run coexisting teleportation experiment
  #depolarized_fidelity, noisy_ent_output_1, noisy_ent_output_2, depolarized_alice_qubit = tele.run_coex_tele_experiment(random_seed = 1, bell_state="psi-", alice_qubit_state="0", noisy_ent_visibility=vis_ent, alice_qubit_noisy_visibility=vis_alice_qubit, verbose=True)
