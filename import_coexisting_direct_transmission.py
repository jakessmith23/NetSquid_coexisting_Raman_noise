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



FIBRE_LENGTH = 1
C = .0002 # speed of light in NetSquid fiber [km/ns]
DELAY = (FIBRE_LENGTH / C) + 1

class EmitProtocol(NodeProtocol):
    def __init__(self, node, verbose=False):
      # init parent NodeProtocol
      super().__init__(node)

      self.meas_results = []

    def run(self):
        self.node.subcomponents['qsource'].trigger()
        yield self.await_timer(DELAY)


class ReceiveProtocol(NodeProtocol):
    def __init__(self, node, verbose=False):
      # init parent NodeProtocol
      super().__init__(node)

      self.verbose = verbose
      self.bp = None

    def run(self):
        if self.verbose: print({ns.sim_time()}, ": Starting", self.node.name, "s ReceiveProtocol")

        port_qin_emitter = self.node.ports["qin_emitter"]

        while True:

          yield self.await_port_input(port_qin_emitter)

          self.bp = None

          if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol received BP: ")
          bp, = port_qin_emitter.rx_input().items

          if self.verbose: print({ns.sim_time()}, self.node.name, "'s ReceiveProtocol peeking: ", bp)
          if self.verbose: print(ns.qubits.reduced_dm(bp))
          self.bp = bp

          self.send_signal(Signals.SUCCESS)


class QuantumConnection(Connection):
    def __init__(self, length, depolar_rate=0):
        # initialize the parent Connection
        super().__init__(name="QuantumConnection")

        models={"delay_model": FibreDelayModel(),
                "quantum_noise_model" : DepolarNoiseModel(depolar_rate=depolar_rate, time_independent=True),
                #'quantum_loss_model' : FibreLossModel(p_loss_length=attenuation_coeff)}
        }

        # add QuantumChannel subcomponent with associated models
        # forward A Port to ClassicalChannel send Port
        # forward ClassicalChannel recv Port to B Port
        ### length does not have effect on simulation
        self.add_subcomponent(QuantumChannel("qChannel_A2B", length=1,
                              models = models),
                              forward_input=[("A", "send")],
                              forward_output=[("B", "recv")])

def characterized_network_setup(ket_state, depolar_prob):
    # create pure input state
    pure_input, = ns.qubits.create_qubits(1, no_state=True)
    if ket_state == '0':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.s0)
    elif ket_state == '1':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.s1)
    elif ket_state == '+':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.h0)
    elif ket_state == '-':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.h1)
    elif ket_state =='0_Y':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.y0)
    elif ket_state =='1_Y':
        ns.qubits.qubitapi.assign_qstate([pure_input], ks.y1)
    else:
        print("ERROR: unknown KetState input. Must be: '0', '1', '+', '-', '0_Y', '1_Y'")
        exit(1)
    pure_input_state = DenseDMRepr(ns.qubits.reduced_dm([pure_input]))

    # create and connect network objects
    emitter = Node("Emitter", qmemory=QuantumMemory("EmitterQmem", num_positions=1))
    qsource = QSource(f"emitter_qsource", StateSampler([pure_input_state], [1]), num_ports=1, status=SourceStatus.EXTERNAL, frequencey=1)
    emitter.add_subcomponent(qsource, name="qsource")

    receiver = Node("Receiver")

    network = Network("raman_network")
    network.add_nodes([emitter, receiver])

    q_conn = QuantumConnection(length=FIBRE_LENGTH, depolar_rate=depolar_prob)

    port_ac, port_bc = network.add_connection(emitter, receiver, connection=q_conn, label="quantum",
                           port_name_node1="qout_receiver", port_name_node2="qin_emitter")

    
    emitter.subcomponents["qsource"].ports['qout0'].forward_output(emitter.ports[port_ac])

    return network, pure_input

# standard NetSquid function to extract simulation data during runtime
def setup_datacollectors(prot_emitter, prot_rx):
    def get_fidelity(evexpr):

        qubit = prot_rx.bp

        return {"qubit": qubit,
                }

    # init datacollector to call get_fidelity() when triggered
    dc_fidelity = DataCollector(get_fidelity, include_entity_name=False)
    # configure datacollector to trigger when Bob's Protocol signals SUCCESS
    dc_fidelity.collect_on(pydynaa.EventExpression(source=prot_rx,
                                          event_type=Signals.SUCCESS.value))

    return dc_fidelity

def calc_dep_prob(incident_raman_photons_per_s, quantum_photons_incident_per_s, detector_gate_time_s):

  raman_photons_incident_per_gate = incident_raman_photons_per_s * detector_gate_time_s

  quantum_photons_incident_per_gate = quantum_photons_incident_per_s * detector_gate_time_s

  depolar_prob = raman_photons_incident_per_gate / (raman_photons_incident_per_gate + quantum_photons_incident_per_gate)

  return depolar_prob


def run_coex_direct_transm_experiment(incident_raman_photons_per_s, quantum_photons_incident_per_s, detector_gate_time_s, random_seed = 1, ket_state="0", verbose=True):

    ns.set_qstate_formalism(ns.QFormalism.DM)
    ns.set_random_state(seed=random_seed)
    ns.sim_reset()

    # calculate mixing probability from incident photons
    depolar_prob = calc_dep_prob(incident_raman_photons_per_s=incident_raman_photons_per_s, quantum_photons_incident_per_s=quantum_photons_incident_per_s, detector_gate_time_s=detector_gate_time_s)

    # setup network and simulation
    network, pure_input = characterized_network_setup(ket_state=ket_state, depolar_prob = depolar_prob)

    node_e = network.get_node("Emitter")
    node_r = network.get_node("Receiver")

    emit_prot = EmitProtocol(node_e)
    recv_prot = ReceiveProtocol(node_r, verbose=True)

    coex_fiber_dm = setup_datacollectors(emit_prot, recv_prot)

    emit_prot.start()
    recv_prot.start()

    ns.sim_run()

    # save data
    coex_fiber_dm = coex_fiber_dm.dataframe

    # calculate fidelity
    noisy_output = coex_fiber_dm.iloc[0]['qubit']

    dep_fidelity = ns.qubits.dmutil.dm_fidelity(ns.qubits.reduced_dm([noisy_output]), ns.qubits.reduced_dm([pure_input]), squared=True, dm_check=True)


    if verbose:    
        print("depolarization probability:", depolar_prob)
        print("depolarized fidelity:", dep_fidelity)

    return dep_fidelity, noisy_output