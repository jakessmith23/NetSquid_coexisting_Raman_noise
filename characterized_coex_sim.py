#import import_coexisting_direct_transmission as direct


import import_coexisting_entanglement as ent
#import import_coexisting_teleportation as tele
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import log, e

# [1] Thomas, J. M., Yeh, F. I., Chen, J. H., Mambretti, J. J., Kohlert, S. J., Kanter, G. S., 
# & Kumar, P. (2024). Quantum teleportation coexisting with classical communications in optical fiber. 
# Optica, 11(12), 1700-1707.


# Do not change: constants used for link characterization
RBW = 0.5  # OSA Resolution Bandwidth in nm
L=20
KPOL=2

def calc_visibility(hardware_params):
    dark_counts_per_det_window = hardware_params['dark_counts_per_det_window']

    # this is 0 as it is not co-propagating
    mean_noise_photons_per_interval_d1 = hardware_params['mean_noise_photons_per_interval_d1']

    n_d1_db = hardware_params['detection_eff_d1'] # detector 3 detection efficiency [dB]
    n_d1 = 10**(n_d1_db / 10) # detector 3 detection efficiency [%]

    n_d0_db = hardware_params['detection_eff_d0'] # detector 2 detection efficiency [dB]
    n_d0 = 10**(n_d0_db / 10) # detector 2 detection efficiency [%]

    n_fibre_db = hardware_params['coexisting_fibre_loss'] # # loss from Bob's source to receiver [dB]
    n_fibre = 10**(n_fibre_db / 10) # loss from Bob's source to receiver [%]

    mean_photons_per_pulse = hardware_params['mean_photons_per_pulse']

    mean_noise_photons_per_pulse = hardware_params['mean_noise_photons_per_pulse']

    nr_1_db = hardware_params['receiver_transmittance_d1'] # transmittance of optical elements at receiver 3 [dB]
    nr_1 = 10**(nr_1_db / 10) # transmittance of optical elements at receiver 3 [%]

    nr_0_db = hardware_params['receiver_transmittance_d0'] # transmittance of optical elements at receiver 3 [dB]
    nr_0 = 10**(nr_0_db / 10) # transmittance of optical elements at receiver 3 [%]

    raman_photons_per_det_window = hardware_params['raman_photons_per_det_window']

    total_transmittance_n1 = nr_1 * n_d1  # total transmittance from Bob --> d3 [%]
    total_transmittance_n0 = nr_0 * n_fibre * n_d0  # total transmittance from source --> d0 [%]

    n_sprs_0 = 1 - e**(-nr_0 * n_d0 * raman_photons_per_det_window)
    n_source_0 = 1 - e**(-total_transmittance_n0 * mean_noise_photons_per_pulse)

    n_sprs_1 = 0
    n_source_1 = 1 - e**(-total_transmittance_n1 * mean_noise_photons_per_pulse)

    c_01 = 0
    a_01 = 0

    p_0 = 0
    p_1 = 0
    for n in range(100):
        p_th = (mean_photons_per_pulse**n /
                ((1 + mean_photons_per_pulse)**(1 + n)))

        r_0 = dark_counts_per_det_window + ((1 - dark_counts_per_det_window) * n_sprs_0) + ((1 - dark_counts_per_det_window) * (1 - n_sprs_0) * n_source_0)
        r_1 = dark_counts_per_det_window + ((1 - dark_counts_per_det_window) * n_sprs_1) + ((1 - dark_counts_per_det_window) * (1 - n_sprs_1) * n_source_1)

        p_d0 = 1 - ((1 - r_0) * (1 - total_transmittance_n0)**n)
        p_d1 = 1 - ((1 - r_1) * (1 - total_transmittance_n1)**n)
        
        c_01 += p_th * p_d0 * p_d1

        p_0 += p_th * p_d0   # singles probability at D0
        p_1 += p_th * p_d1   # singles probability at D1


    a_01 = p_0 * p_1

    # visibility of Detectors 2, 3
    v_ent = (c_01 - a_01) / (c_01 + a_01)

    print(f"Ram photons: {raman_photons_per_det_window}")
    print(f"Total trans n2: {total_transmittance_n0}")
    print(f"Total trans n3: {total_transmittance_n1}")
    print(f"c: {c_01}")
    print(f"a: {a_01}")

    print(f"V: {v_ent}")
    print("f: ", (1 + 3 * v_ent) / 4)


    return v_ent # entanglement visibility, Alice visibility



def kumar_approximation(hardware_params):
    # ToDo: cite equation
    # setup assumes 2 single photon detectors: d0, d1
    # and two links, 0 and 1
    # 0 is the coexisting link, with fibre, receiver optics, and detector 0
    # 1 is the heralding arm, with receiver optics, detector 1, and no fibre

    dark_counts_per_det_window = hardware_params['dark_counts_per_det_window']

    # this is 0 as it is not co-propagating
    mean_noise_photons_per_interval_d3 = hardware_params['mean_noise_photons_per_interval_d1']

    n_d1_db = hardware_params['detection_eff_d1'] # detector 3 detection efficiency [dB]
    n_d1 = 10**(n_d1_db / 10) # detector 3 detection efficiency [%]

    n_d0_db = hardware_params['detection_eff_d0'] # detector 2 detection efficiency [dB]
    n_d0 = 10**(n_d0_db / 10) # detector 2 detection efficiency [%]

    n_fibre_db = hardware_params['coexisting_fibre_loss'] # # loss from Bob's source to receiver [dB]
    n_fibre = 10**(n_fibre_db / 10) # loss from Bob's source to receiver [%]

    mean_photons_per_pulse = hardware_params['mean_photons_per_pulse']

    mean_noise_photons_per_pulse = hardware_params['mean_noise_photons_per_pulse']

    nr_1_db = hardware_params['receiver_transmittance_d1'] # transmittance of optical elements at receiver 3 [dB]
    nr_1 = 10**(nr_1_db / 10) # transmittance of optical elements at receiver 3 [%]

    nr_0_db = hardware_params['receiver_transmittance_d0'] # transmittance of optical elements at receiver 3 [dB]
    nr_0 = 10**(nr_0_db / 10) # transmittance of optical elements at receiver 3 [%]


    total_transmittance_n1 = nr_1 * n_d1  # total transmittance from Bob --> d3 [%]

    # [1] Equation S5
    r_1 = (mean_noise_photons_per_interval_d3 * n_d1 * nr_1) + (mean_noise_photons_per_pulse * total_transmittance_n1) + dark_counts_per_det_window

    raman_photons_per_det_window = hardware_params['raman_photons_per_det_window']

    total_transmittance_n0 = nr_0 * n_fibre * n_d0  # total transmittance from source --> d0 [%]

    # [1] Equation S6
    r_0 = (raman_photons_per_det_window * n_d0 * nr_0) + (mean_noise_photons_per_pulse * total_transmittance_n0) + dark_counts_per_det_window
    print("$", raman_photons_per_det_window * n_d0 * nr_0)

    # [1] Equation S13
    s_1 = (total_transmittance_n1 * mean_photons_per_pulse) + r_1

    # [1] Equation S13
    s_0 = (total_transmittance_n0 * mean_photons_per_pulse) + r_0

    # [1] Equation S14
    c = total_transmittance_n0 * total_transmittance_n1 * (mean_photons_per_pulse + mean_photons_per_pulse**2) + (s_0 * s_1)
    # [1] Equation S15
    a = (s_0 * s_1)   

    # visibility of Detectors 2, 3
    v_ent = (c - a) / (c + a)

    print(f"Ram photons: {raman_photons_per_det_window}")
    print(f"Total trans n2: {total_transmittance_n0}")
    print(f"Total trans n3: {total_transmittance_n1}")
    print(f"c: {c}")
    print(f"a: {a}")

    print(f"V: {v_ent}")


    return v_ent # entanglement visibility, Alice visibility

    

# Energy per photon for given wavelength in nm
get_photon_energy = lambda wl_nm: (1240 / wl_nm) * 1.6e-19

def read_measurement_data(filename, sheet_name):
    data_table = pd.read_excel(filename, sheet_name=sheet_name)
    data = data_table.to_numpy()
    return {
        'wavelengths': data[:, 0],
        'P_TX': 10 ** (data[:, 1] * 0.1), # mW
        'P_CT': 10 ** (data[:, 2] * 0.1), # mW
        'P_BW': 10 ** (data[:, 3] * 0.1), # mW
        'P_RX': 10 ** (data[:, 4] * 0.1), # mW
        'alpha_np': (data[:, 5] / 10) * (np.log10(np.exp(1)))  
    }

def calculate_rho(P_BW, alpha_np, P_in, RBW):
    k_Pin = P_in * np.exp(-alpha_np * L)
    k_sinh = np.sinh(alpha_np * L) / alpha_np
    return KPOL * (P_BW / k_Pin / k_sinh / RBW)

def calc_raman_photons(P_launch, rho, alpha_np, wavelengths, fiber_lengths, detection_window):
    ram_photons_per_det_window = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}
    for p in P_launch:
        for l in fiber_lengths:
            k_Pin = p * np.exp(-alpha_np * l)
            for wl in wavelengths:
                idx = np.where(np.isclose(data['wavelengths'], wl))[0][0]
                power_fw = k_Pin[idx] * KPOL * l * rho[idx] * RBW * 1e-3  # W
                energy_photon = get_photon_energy(wl)
                photon_count = (power_fw / energy_photon) * detection_window
                ram_photons_per_det_window[wl][l].append(photon_count)
    return ram_photons_per_det_window

def simulate(ram_photons_per_det_window, hardware_params, fiber_lengths, wavelengths):
    fidelities = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}
    ns_fidelities = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}
    p_mix = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}


    for wl in wavelengths:
        for l in fiber_lengths:
            for p in ram_photons_per_det_window[wl][l]:
                # CONFIGURABLE: since only distributing entanglement, Alice's channel is not utilized so no Raman photons are generated
                hardware_params['raman_photons_per_det_window'] = p
                hardware_params['coexisting_fibre_loss'] = hardware_params['fibre_attenuation'] * l
                print(f"Link length: {l} km. Fibre loss: {hardware_params['coexisting_fibre_loss']} dB")

                # CONFIGURABLE: if visibility already know, you may just use that
                # ReadME: if your hardware setup does not match the configuration file, the calc_visibility() function will need to be modified to model your system
                visibility = calc_visibility(hardware_params)

                fidelity, _, _, depolar_prob = ent.run_coex_ent_experiment(
                    bell_state="phi+",
                    noisy_visibility=visibility,
                    verbose=False
                )
                fidelities[wl][l].append((1 + 3*visibility) / 4)
                ns_fidelities[wl][l].append(fidelity)


    return fidelities, ns_fidelities

if __name__ == "__main__":
    # Load data
    data = read_measurement_data('RAMAN_Charact.xlsx', 'Meas_1565_HP_DP')
    # Use max input power to estimate rho
    max_power = np.max(data['P_TX'])
    rho = calculate_rho(
        data['P_BW'],
        data['alpha_np'],
        P_in=max_power,
        RBW=RBW
    )

    # Raman photon calculation
     # CONFIGURABLE: select your lengths and wavelengths of choice
    fiber_lengths = [50]  # km
    wavelengths = [1510, 1554, 1563.4, 1566.6, 1580]

    # CONFIGURABLE: Select which hardware parameters to use to calculate visibility --> fidelity based on your experiment type
    from hardware_config import hardware_params  


    launch_powers_mW = np.linspace(0, 10, 100)
    ram_photons_per_det_window = calc_raman_photons(launch_powers_mW, rho, data['alpha_np'], wavelengths, fiber_lengths, hardware_params['detection_window'])

    
    # Fidelity simulation
    # CONFIGURABLE: pass the correct hardware_params for your type of experiment
    fidelities, ns_fidelities = simulate(ram_photons_per_det_window, hardware_params, fiber_lengths, wavelengths)

    colors = ['blue', 'orange', 'green', 'red', 'purple']
    wavelength_labels = ['1510 nm', '1554 nm', '1563.4 nm', '1566.6 nm', '1580 nm']

    # CONFIGURABLE link length to graph
    link_length_to_graph = fiber_lengths[-1] # km
    for i, wl in enumerate(wavelengths):
        plt.plot(launch_powers_mW, ns_fidelities[wl][link_length_to_graph], label=wl, color=colors[i])
    
    plt.axhline(y=0.25, linestyle="dotted", color="black")  
    plt.ylim(0.2, 1)
    plt.xlabel("Launch Power (mW)")
    plt.ylabel("Fidelity")
    plt.title(f"Coexisting Entanglement Fidelity at {link_length_to_graph} km")
    plt.legend(title="Wavelength [nm]")
    plt.grid(True)
    plt.show()
