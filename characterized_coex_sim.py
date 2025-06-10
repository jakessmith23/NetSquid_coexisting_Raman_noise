import import_coexisting_direct_transmission as direct
import import_coexisting_entanglement as ent
import import_coexisting_teleportation as tele
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Constants
DETECTION_WINDOW = 5e-10  # 500 ps
RBW = 0.5  # OSA Resolution Bandwidth in nm
FIBER_LENGTHS = [20, 40]  # km
WAVELENGTHS = [1510, 1554, 1563.4, 1566.6]

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

def calculate_rho(P_BW, alpha_np, L, P_in, RBW, kpol=2):
    k_Pin = P_in * np.exp(-alpha_np * L)
    k_sinh = np.sinh(alpha_np * L) / alpha_np
    return kpol * (P_BW / k_Pin / k_sinh / RBW)

def calc_raman_photons(P_launch, rho, alpha_np, wavelengths, detection_window, RBW, kpol=2):
    photons = {wl: {20: [], 40: []} for wl in wavelengths}
    for p in P_launch:
        for L in FIBER_LENGTHS:
            k_Pin = p * np.exp(-alpha_np * L)
            for wl in wavelengths:
                idx = np.where(np.isclose(data['wavelengths'], wl))[0][0]
                power_fw = k_Pin[idx] * kpol * L * rho[idx] * RBW * 1e-3  # W
                energy_photon = get_photon_energy(wl)
                photon_count = (power_fw / energy_photon) * detection_window
                photons[wl][L].append(photon_count)
    return photons

def simulate_entanglement_distr(photons, hardware_params):
    fidelities = {wl: {20: [], 40: []} for wl in WAVELENGTHS}
    for wl in WAVELENGTHS:
        for L in FIBER_LENGTHS:
            for p in photons[wl][L]:
                hardware_params['alice_fibre_raman_photons_per_det_window'] = 0
                hardware_params['bob_fibre_raman_photons_per_det_window'] = p
                visibility, _ = tele.calc_visibility(hardware_params)
                fidelity, _, _ = ent.run_coex_ent_experiment(
                    random_seed=1,
                    bell_state="phi+",
                    noisy_visibility=visibility,
                    verbose=False
                )
                fidelities[wl][L].append(fidelity)
    return fidelities

if __name__ == "__main__":
    # Load data
    data = read_measurement_data('RAMAN_Charact.xlsx', 'Meas_1565_HP_DP')

    # Use max input power to estimate rho
    max_power = np.max(data['P_TX'])
    rho = calculate_rho(
        data['P_BW'],
        data['alpha_np'],
        L=20,
        P_in=max_power,
        RBW=RBW
    )

    # Raman photon calculation
    launch_powers_mW = np.linspace(0, 10, 100)
    raman_photons = calc_raman_photons(launch_powers_mW, rho, data['alpha_np'], WAVELENGTHS, DETECTION_WINDOW, RBW)

    # Hardware parameters (defined elsewhere in full code)
    from entangled_hardware_config import hardware_params  
    

    # Fidelity simulation
    fidelities = simulate_entanglement_distr(raman_photons, hardware_params)

    colors = ['blue', 'orange', 'green', 'red']
    wavelength_labels = ['1510 nm', '1554 nm', '1563.4 nm', '1566.6 nm']

    for i, wl in enumerate(WAVELENGTHS):
        plt.plot(launch_powers_mW, fidelities[wl][20], label=wavelength_labels[i], color=colors[i])
        plt.plot(launch_powers_mW, fidelities[wl][40], linestyle='dashed', color=colors[i])

    plt.axvline(x=0.25, color='black', linestyle=':', linewidth=1.5)
    plt.xlabel("Launch Power (mW)")
    plt.ylabel("Fidelity")
    plt.title("Coexisting Entanglement Fidelity vs Launch Power")
    plt.legend(title="Wavelength")
    plt.grid(True)
    plt.show()
