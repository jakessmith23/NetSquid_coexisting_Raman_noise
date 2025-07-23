import import_coexisting_direct_transmission as direct
import import_coexisting_entanglement as ent
import import_coexisting_teleportation as tele
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Do not change: constants used for link characterization
DETECTION_WINDOW = 5e-10  # 500 ps
RBW = 0.5  # OSA Resolution Bandwidth in nm
L=20
KPOL=2


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
        'alpha_np': (data[:, 5] / 10) * np.log10(np.log10(np.exp(1)))  # convert dB/km to np (1/km)
    }

def calculate_rho(P_BW, alpha_np, P_in, RBW, kpol=2):
    k_Pin = P_in * np.exp(-alpha_np * L)
    k_sinh = np.sinh(alpha_np * L) / alpha_np
    return kpol * (P_BW / k_Pin / k_sinh / RBW)

def calc_raman_photons(P_launch, rho, alpha_np, wavelengths, fiber_lengths, kpol=2):
    ram_photons_per_det_window = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}
    for p in P_launch:
        for l in fiber_lengths:
            k_Pin = p * np.exp(-alpha_np * l)
            for wl in wavelengths:
                idx = np.where(np.isclose(data['wavelengths'], wl))[0][0]
                power_fw = k_Pin[idx] * KPOL * l * rho[idx] * RBW * 1e-3  # W
                energy_photon = get_photon_energy(wl)
                photon_count = (power_fw / energy_photon) * DETECTION_WINDOW
                ram_photons_per_det_window[wl][l].append(photon_count)
    return ram_photons_per_det_window

def simulate(ram_photons_per_det_window, tele_hardware_params, fiber_lengths, wavelengths):
    fidelities = {wl: {L: [] for L in fiber_lengths} for wl in wavelengths}
    for wl in wavelengths:
        for l in fiber_lengths:
            for p in ram_photons_per_det_window[wl][l]:
                # CONFIGURABLE: since only distributing entanglement, Alice's channel is not utilized so no Raman photons are generated
                tele_hardware_params['alice_fibre_raman_photons_per_det_window'] = 0
                tele_hardware_params['bob_fibre_raman_photons_per_det_window'] = p
                # CONFIGURABLE: if visibility already know, you may just use that
                # ReadME: if your hardware setup does not match [1], the calc_visibility() function in import_coexisting_teleportation will need to be modified to model your system
                visibility, _ = tele.calc_visibility(tele_hardware_params)
                fidelity, _, _ = ent.run_coex_ent_experiment(
                    bell_state="phi+",
                    noisy_visibility=visibility,
                    verbose=False
                )
                fidelities[wl][l].append(fidelity)
    return fidelities

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
    fiber_lengths = [10, 20, 40]  # km
    wavelengths = [1510, 1554, 1563.4, 1566.6]

    launch_powers_mW = np.linspace(0, 10, 100)
    raman_photons = calc_raman_photons(launch_powers_mW, rho, data['alpha_np'], wavelengths, fiber_lengths)

    for wl in wavelengths:
        for l in fiber_lengths:
            # to access raman photon counts for a certain wavelenth at a certain length 
            print(raman_photons[wl][l])

    # CONFIGURABLE: Select which hardware parameters to use to calculate visibility --> fidelity based on your experiment type
    from entangled_hardware_config import tele_hardware_params  

    
    # Fidelity simulation
    # CONFIGURABLE: pass the correct hardware_params for your type of experiment
    fidelities = simulate(raman_photons, tele_hardware_params, fiber_lengths, wavelengths)

    colors = ['blue', 'orange', 'green', 'red']
    wavelength_labels = ['1510 nm', '1554 nm', '1563.4 nm', '1566.6 nm']

    # CONFIGURABLE link length to graph
    link_length_to_graph = 40 # km
    for i, wl in enumerate(wavelengths):
        plt.plot(launch_powers_mW, fidelities[wl][link_length_to_graph], label=wavelength_labels[i], color=colors[i])

    plt.axvline(x=0.25, color='black', linestyle=':', linewidth=1.5)
    plt.xlabel("Launch Power (mW)")
    plt.ylabel("Fidelity")
    plt.title(f"Coexisting Entanglement Fidelity vs Launch Power at 40 km")
    plt.legend(title="Wavelength")
    plt.grid(True)
    plt.show()
