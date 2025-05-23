import netsquid as ns
from netsquid.protocols import NodeProtocol
from netsquid.protocols import Signals
from netsquid.nodes.connections import Connection
from netsquid.components.qsource import QSource, SourceStatus
from netsquid.qubits.state_sampler import StateSampler
from netsquid.components import QuantumChannel
import netsquid.qubits.ketstates as ks
from netsquid.components import QuantumChannel
from netsquid.components.models import DepolarNoiseModel
from netsquid.components.models import FibreDelayModel
from netsquid.util import DataCollector
from netsquid.protocols import Signals
import pydynaa
from netsquid.qubits.dmtools import DenseDMRepr
from netsquid.nodes import Node
from netsquid.nodes import Network
from netsquid.components import QuantumMemory
from netsquid.qubits.dmtools import DenseDMRepr


# Citations:
# [1] Thomas, Jordan; Yeh, Fei; Chen, Jim; Mambretti, Joe; Kohlert, Scott; Kanter, Gregory; et al. (2024). Supplementary document for Quantum Teleportation Coexisting with Classical Communications in Optical Fiber - 7260233.pdf. Optica Publishing Group. Journal contribution.

FIBRE_LENGTH = 1
C = .0002 # speed of light in NetSquid fiber [km/ns]
DELAY = (FIBRE_LENGTH / C) + 1

def calc_visibility(hardware_params):
    # setup assumes 4 single photon detectors: d0, d1, d2, d3
    # 0 and 3 are the heradling arms
    # 1 and 2 perform interference mixing

    dark_counts_per_gate = hardware_params['dark_counts_per_gate']

    n_d0_db = hardware_params['detection_eff_d0'] # detector 0 detection efficiency [dB]
    n_d0 = 10**(n_d0_db / 10) # detector 0 detection efficiency [%]

    # these are 0 as they are not co-propagating
    mean_noise_photons_per_interval_d0 = hardware_params['mean_noise_photons_per_interval_d0']
    mean_noise_photons_per_interval_d3 = hardware_params['mean_noise_photons_per_interval_d3']

    n_d3_db = hardware_params['detection_eff_d3'] # detector 3 detection efficiency [dB]
    n_d3 = 10**(n_d3_db / 10) # detector 3 detection efficiency [%]

    n_ac_db = hardware_params['alice_fibre_loss'] # loss from Alice's source to beamsplitter [dB]
    n_ac = 10**(n_ac_db / 10) # # loss from Alice's source to beamsplitter [mW]
    n_bc_db = hardware_params['bob_fibre_loss'] # # loss from Bob's source to beamsplitter [dB]
    n_bc = 10**(n_bc_db / 10) # loss from Bob's source to beamsplitter [mW]

    mean_photons_per_pulse_a = hardware_params['mean_photons_per_pulse_Alice']
    mean_photons_per_pulse_b = hardware_params['mean_photons_per_pulse_Bob']

    mean_noise_photons_per_pulse_a = hardware_params['mean_noise_photons_per_pulse_Alice']
    mean_noise_photons_per_pulse_b = hardware_params['mean_noise_photons_per_pulse_Bob']

    nr_0_db = hardware_params['receiver_transmittance_d0'] # transmittance of optical elements at receiver 0 [dB]
    nr_0 = 10**(nr_0_db / 10) # transmittance of optical elements at receiver 0 [%]
    nr_3_db = hardware_params['receiver_transmittance_d3'] # transmittance of optical elements at receiver 3 [dB]
    nr_3 = 10**(nr_3_db / 10) # transmittance of optical elements at receiver 3 [%]

    total_transmittance_n0 = hardware_params['total_transmittance_n0'] # total transmittance from Alice --> d0 [%]
    # [1] Equation S5
    r_0 = (mean_noise_photons_per_interval_d0 * n_d0 * nr_0) + (mean_noise_photons_per_pulse_a * total_transmittance_n0) + dark_counts_per_gate

    total_transmittance_n3 = hardware_params['total_transmittance_n3'] # total transmittance from Bob --> d3 [%]
    # [1] Equation S5
    r_3 = (mean_noise_photons_per_interval_d3 * n_d3 * nr_3) + (mean_noise_photons_per_pulse_b * total_transmittance_n3) + dark_counts_per_gate


    n_d1_db = hardware_params['detection_eff_d1'] # detector 1 detection efficiency [dB]
    n_d1 = 10**(n_d1_db / 10) # detector 1 detection efficiency [%]

    n_d2_db = hardware_params['detection_eff_d2'] # detector 2 detection efficiency [dB]
    n_d2 = 10**(n_d2_db / 10) # detector 2 detection efficiency [%]

    insertion_loss_into_bsm_dB = hardware_params['insertion_loss_into_bsm'] # dB
    insertion_loss_into_bsm = 10**(insertion_loss_into_bsm_dB / 10)

    alice_fibre_raman_photons_per_det_window = hardware_params['alice_fibre_raman_photons_per_det_window']
    bob_fibre_raman_photons_per_det_window = hardware_params['bob_fibre_raman_photons_per_det_window']

    # [1] Equation S7
    n_R_a = (alice_fibre_raman_photons_per_det_window * insertion_loss_into_bsm) + (mean_noise_photons_per_pulse_a * n_ac)
    n_R_b = (bob_fibre_raman_photons_per_det_window * insertion_loss_into_bsm) + (mean_noise_photons_per_pulse_b * n_bc)

    # [1] Equation S6
    r_1 = ((n_d1 * (n_R_a + n_R_b)) / 2) + dark_counts_per_gate
    r_2 = ((n_d2 * (n_R_a + n_R_b)) / 2) + dark_counts_per_gate

    # [1] Equation S13
    s_0 = (total_transmittance_n0 * mean_photons_per_pulse_a) + r_0
    s_3 = (total_transmittance_n3 * mean_photons_per_pulse_b) + r_3

    total_transmittance_n1 = hardware_params['total_transmittance_n1'] # total transmittance from Alice --> d1 [%]
    total_transmittance_n2 = hardware_params['total_transmittance_n2'] # total transmittance from Bob --> d2 [%]

    # [1] Equation S13
    s_1 = (total_transmittance_n1 * mean_photons_per_pulse_a) + r_1
    s_2 = (total_transmittance_n2 * mean_photons_per_pulse_b) + r_2

    # [1] Equation S14
    c_01 = total_transmittance_n0 * total_transmittance_n1 * (mean_photons_per_pulse_a + mean_photons_per_pulse_a**2) + (s_0 * s_1)
    # [1] Equation S15
    a_01 = s_0 * s_1

    # [1] Equation S14
    c_23 = total_transmittance_n2 * total_transmittance_n3 * (mean_photons_per_pulse_b + mean_photons_per_pulse_b**2) + (s_2 * s_3)
    # [1] Equation S15
    a_23 = (s_2 * s_3)

    # visibility of Detectors 0,1
    v_ent_01 = (c_01 - a_01) / (c_01 + a_01)

    # visibility of Detectors 2, 3
    v_ent_23 = (c_23 - a_23) / (c_23 + a_23)

    return v_ent_23, v_ent_01 # entanglement visibility, Alice visibility



class EmitProtocol(NodeProtocol):
    def __init__(self, node, verbose=False):
        # init parent NodeProtocol
        super().__init__(node)

        self.verbose = verbose
        self.meas_results = []

    def run(self):
        if self.verbose: print({ns.sim_time()}, ": Starting", self.node.name, "s EmitProtocol")
        self.node.subcomponents['alice_qsource'].trigger()
        self.node.subcomponents['ent_qsource'].trigger()
        if self.verbose: print({ns.sim_time()}, self.node.name, "s EmitProtocol sent qubits...")


class ReceiveProtocol(NodeProtocol):
    def __init__(self, node, verbose=False):
      # init parent NodeProtocol
      super().__init__(node)

      self.verbose = verbose
      self.bp = None
      self.alice_q = None

    def run(self):
        if self.verbose: print({ns.sim_time()}, ": Starting", self.node.name, "s ReceiveProtocol")

        port_qin_emitter1 = self.node.ports["qin1_emitter"]
        port_qin_emitter2 = self.node.ports["qin2_emitter"]

        yield self.await_port_input(port_qin_emitter2)
        yield self.await_port_input(port_qin_emitter1)

        self.bp = None

        if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol received BP: ")
        bp, = port_qin_emitter1.rx_input().items

        if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol peeking at Bell-Pair: ", bp)
        if self.verbose: print(ns.qubits.reduced_dm(bp))
        self.bp = bp

        if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol received BP: ")
        alice_q, = port_qin_emitter2.rx_input().items

        if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol peeking at Alice's qubit: ", alice_q)
        if self.verbose: print(ns.qubits.reduced_dm(alice_q))
        self.alice_q = alice_q

        self.send_signal(Signals.SUCCESS)


class QuantumConnection(Connection):
    def __init__(self, length, depolar_rate=0):
        # initialize the parent Connection
        super().__init__(name="QuantumConnection")

        models={"delay_model": FibreDelayModel(),
                "quantum_noise_model" : DepolarNoiseModel(depolar_rate=depolar_rate, time_independent=True),
        }

        # add QuantumChannel subcomponent with associated models
        # forward A Port to ClassicalChannel send Port
        # forward ClassicalChannel recv Port to B Port
        ### length does not have effect on simulation
        self.add_subcomponent(QuantumChannel("qChannel_A2B", length=1,
                              models = models),
                              forward_input=[("A", "send")],
                              forward_output=[("B", "recv")])

def characterized_network_setup(bell_state, entangled_pair_dep_prob, alice_depolar_prob, alice_qubit_state):
    # create pure input entangled state
    pure_ent_input_1, pure_ent_input_2 = ns.qubits.create_qubits(2, no_state=True)
    if bell_state == 'phi+':
        ns.qubits.qubitapi.assign_qstate([pure_ent_input_1, pure_ent_input_2], ks.b00)
    elif bell_state == 'phi-':
        ns.qubits.qubitapi.assign_qstate([pure_ent_input_1, pure_ent_input_2], ks.b10)
    elif bell_state == 'psi+':
        ns.qubits.qubitapi.assign_qstate([pure_ent_input_1, pure_ent_input_2], ks.b01)
    elif bell_state == 'psi-':
        ns.qubits.qubitapi.assign_qstate([pure_ent_input_1, pure_ent_input_2], ks.b11)
    else:
        print("ERROR: unknown Bell State input. Must be: 'phi+', 'phi-', 'psi+', 'psi-'")
        exit(1)
    pure_ent_state = DenseDMRepr(ns.qubits.reduced_dm([pure_ent_input_1, pure_ent_input_2]))

    # create Alice's pure state to teleport
    pure_alice_q, = ns.qubits.create_qubits(1, no_state=True)
    if alice_qubit_state == '0':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.s0)
    elif alice_qubit_state == '1':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.s1)
    elif alice_qubit_state == '+':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.h0)
    elif alice_qubit_state == '-':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.h1)
    elif alice_qubit_state =='0_Y':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.y0)
    elif alice_qubit_state =='1_Y':
        ns.qubits.qubitapi.assign_qstate(pure_alice_q, ks.y1)
    else:
        print("ERROR: unknown KetState input. Must be: '0', '1', '+', '-', '0_Y', '1_Y'")
        exit(1)
    pure_alice_state = DenseDMRepr(ns.qubits.reduced_dm([pure_alice_q]))

    # setup network objects
    emitter = Node("Emitter", qmemory=QuantumMemory("EmitterQmem", num_positions=1))
    ent_qsource = QSource(f"emitter_ent_qsource", StateSampler([pure_ent_state], [1]), num_ports=2, status=SourceStatus.EXTERNAL, frequency=1)
    alice_qsource = QSource(f"emitter_alice_qsource", StateSampler([pure_alice_state], [1]), num_ports=1, status=SourceStatus.EXTERNAL, frequency=1)
    emitter.add_subcomponent(ent_qsource, name="ent_qsource")
    emitter.add_subcomponent(alice_qsource, name="alice_qsource")


    receiver = Node("Receiver")

    network = Network("raman_network")
    network.add_nodes([emitter, receiver])

    # create and connect Nodes with QuantumConnections
    q_conn_ent = QuantumConnection(length=FIBRE_LENGTH, depolar_rate=entangled_pair_dep_prob)

    port_ac, port_bc = network.add_connection(emitter, receiver, connection=q_conn_ent, label="quantum",
                           port_name_node1="qout1_receiver", port_name_node2="qin1_emitter")

    emitter.subcomponents["ent_qsource"].ports['qout1'].connect(emitter.qmemory.ports['qin0'])
    emitter.subcomponents["ent_qsource"].ports['qout0'].forward_output(emitter.ports[port_ac])

    q_conn_alice = QuantumConnection(length=FIBRE_LENGTH, depolar_rate=alice_depolar_prob)

    port_ac2, port_bc = network.add_connection(emitter, receiver, connection=q_conn_alice, label="quantum2",
                           port_name_node1="qout2_receiver", port_name_node2="qin2_emitter")
    emitter.subcomponents["alice_qsource"].ports['qout0'].forward_output(emitter.ports[port_ac2])


    return network, pure_ent_input_1, pure_ent_input_2, pure_alice_state

# standard NetSquid function to extract simulation data during runtime
def setup_datacollectors(prot_emitter, prot_rx):
    def get_fidelity(evexpr):
        b1, = prot_emitter.node.qmemory.pop(0)
        b2 = prot_rx.bp
        alice_q = prot_rx.alice_q

        return {"b1": b1,
                "b2": b2,
                "alice_q": alice_q,
                "dm": ns.qubits.reduced_dm([b1, b2])}

    # init datacollector to call get_fidelity() when triggered
    dc_fidelity = DataCollector(get_fidelity, include_entity_name=False)
    # configure datacollector to trigger when Bob's Protocol signals SUCCESS
    dc_fidelity.collect_on(pydynaa.EventExpression(source=prot_rx,
                                          event_type=Signals.SUCCESS.value))

    return dc_fidelity

def get_dep_prob_from_v(noisy_visibility):
  depolarized_fidelity = (1 + 3 * noisy_visibility) / 4
  depolar_prob = 1 - depolarized_fidelity

  return depolar_prob

def get_dep_prob_from_v_alice(noisy_visibility):
    depolarized_fidelity = (1 + noisy_visibility) / 2
    depolar_prob = 1 - depolarized_fidelity

    return depolar_prob


def run_coex_tele_experiment(random_seed = 1, bell_state="psi-", alice_qubit_state="0", noisy_ent_visibility=1, alice_qubit_noisy_visibility=1, visibility_HOM=None, verbose=True):

    ns.set_qstate_formalism(ns.QFormalism.DM)
    ns.set_random_state(seed=random_seed)
    ns.sim_reset()

    # calculate mixing probabilites from visibilites
    alice_depolar_prob = get_dep_prob_from_v_alice(noisy_visibility=alice_qubit_noisy_visibility)
    entangled_pair_dep_prob = get_dep_prob_from_v(noisy_visibility=noisy_ent_visibility)

    # setup network and NetSquid simulation
    network, pure_ent_input_1, pure_ent_input_2, pure_alice_state = characterized_network_setup(bell_state=bell_state, entangled_pair_dep_prob = entangled_pair_dep_prob, alice_depolar_prob=alice_depolar_prob, alice_qubit_state=alice_qubit_state)

    node_e = network.get_node("Emitter")
    node_r = network.get_node("Receiver")

    emit_prot = EmitProtocol(node_e, verbose=verbose)
    recv_prot = ReceiveProtocol(node_r, verbose=verbose)

    coex_fiber_dm = setup_datacollectors(emit_prot, recv_prot)

    emit_prot.start()
    recv_prot.start()

    # run simulation
    ns.sim_run()

    # save data
    coex_fiber_dm = coex_fiber_dm.dataframe

    # calculate fidelity
    noisy_ent_output_1 = coex_fiber_dm.iloc[0]['b1']
    noisy_ent_output_2 = coex_fiber_dm.iloc[0]['b2']
    noisy_alice_output = coex_fiber_dm.iloc[0]['alice_q']

    f_ent = ns.qubits.dmutil.dm_fidelity(ns.qubits.reduced_dm([noisy_ent_output_1, noisy_ent_output_2]), ns.qubits.reduced_dm([pure_ent_input_1, pure_ent_input_2]), squared=True, dm_check=True)

    f_alice = ns.qubits.fidelity(noisy_alice_output, pure_alice_state, squared=True)

    if verbose:
        print("alice_depolar_prob:", alice_depolar_prob)
        print("entangled_pair_dep_prob:", entangled_pair_dep_prob)
        print("depolarized f_ent:", f_ent)
        print("depolarized f_alice:", f_alice)
    

    if alice_qubit_state == "0" or "1":
        f_poles = .5 + (4/3) * (f_ent - .25) * (f_alice - 0.5)
        if verbose: print("depolarized f_poles:", f_poles)
    else:
        if visibility_HOM is not None:
            f_eq = .5 + (4/3) * visibility_HOM * (f_ent - .25) * (f_alice - 0.5)
            f_avg = .5 + (8/9) * (visibility_HOM + .5) * (f_ent - .25) * (f_alice - .5)
            if verbose:
                print("depolarized f_equatorial:", f_eq)
                print("depolarized f_average", f_avg)
        else:
            print("ERROR: must provide visibility of HOM interference to calculate fidelity of equatorial state and average state on Bloch Sphere.")
            exit(1)

    return f_ent, noisy_ent_output_1, noisy_ent_output_2, noisy_alice_output