from qunetsim.components import Network
from qunetsim.objects import Qubit, Logger
from qunetsim.backends import EQSNBackend

from components.controller_host import ControllerHost
from components.clock import Clock
from components.computing_host import ComputingHost

from objects.circuit import Circuit
from objects.layer import Layer
from objects.operation import Operation

from utils.constants import Constants

from eqsn import EQSN
import numpy as np

Logger.DISABLED = True

def unitary_gate(theta):
    unitary = np.array(
      [[1, 0], [0, (np.cos(theta) + np.sin(theta)*1j)]],
        dtype=np.csingle)
    return unitary

def quantum_phase_estimation_circuit():
    """
    Returns the monolithic circuit for quantum phase estimation
    algorithm
    """
    layers = []

    # We use T gate here
    theta = np.pi/4
    unitary = unitary_gate(theta)
    #unitary = np.array(
    #    [[1, 0], [0, (0.7071067811865476 + 0.7071067811865475j)]],
    #    dtype=np.csingle)

    q_map = {
        'QPU_1': ['qubit_1', 'qubit_2', 'qubit_3'],
        'QPU_2': ['qubit_4']}

    # Prepare the qubits
    op_1 = Operation(
        name=Constants.PREPARE_QUBITS,
        qids=q_map['QPU_1'],
        computing_host_ids=["QPU_1"])

    op_2 = Operation(
        name=Constants.PREPARE_QUBITS,
        qids=q_map['QPU_2'],
        computing_host_ids=["QPU_2"])

    layers.append(Layer([op_1, op_2]))

    # Apply Hadamard gates
    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_1"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    op_2 = Operation(
        name="SINGLE",
        qids=["qubit_2"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    op_3 = Operation(
        name="SINGLE",
        qids=["qubit_3"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1, op_2, op_3]))

    # Apply controlled unitaries
    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_1", "qubit_4"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=unitary,
        computing_host_ids=["QPU_1", "QPU_2"])

    layers.append(Layer([op_1]))

    for i in range(2):
        op = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_4"],
            gate=Operation.CUSTOM_CONTROLLED,
            gate_param=unitary,
            computing_host_ids=["QPU_1", "QPU_2"])
        layers.append(Layer([op]))

    for i in range(4):
        op = Operation(
            name="TWO_QUBIT",
            qids=["qubit_3", "qubit_4"],
            gate=Operation.CUSTOM_CONTROLLED,
            gate_param=unitary,
            computing_host_ids=["QPU_1", "QPU_2"])
        layers.append(Layer([op]))

    # Inverse Fourier Transform circuit
    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_1"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_1", "qubit_2"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=unitary_gate(np.pi/2),
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_2"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_1", "qubit_3"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=unitary_gate(np.pi/4),
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_2", "qubit_3"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=unitary_gate(np.pi/2),
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_3"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
            name="MEASURE",
            qids=["qubit_1"],
            cids=["qubit_1"],
            computing_host_ids=["QPU_1"])

    op_2 = Operation(
            name="MEASURE",
            qids=["qubit_2"],
            cids=["qubit_2"],
            computing_host_ids=["QPU_1"])

    op_3 = Operation(
            name="MEASURE",
            qids=["qubit_3"],
            cids=["qubit_3"],
            computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1, op_2, op_3]))

    circuit = Circuit(q_map, layers)
    return circuit

def controller_host_protocol(host):
    """
    Protocol for the controller host
    """

    circuit = quantum_phase_estimation_circuit()
    host.generate_and_send_schedules(circuit)
    host.receive_results()

def computing_host_protocol(host):
    """
    Protocol for the computing hosts
    """

    host.receive_schedule()
    host.send_results()

    if host.host_id == 'QPU_1':
        print("qubit_1: ", host._bits['qubit_1'])
        print("qubit_2: ", host._bits['qubit_2'])
        print("qubit_3: ", host._bits['qubit_3'])

def main():
    # initialize network
    network = Network.get_instance()
    backend = EQSNBackend()

    nodes = ['Host_1', 'QPU_1', 'QPU_2']
    network.start(nodes, backend)

    clock = Clock()

    computing_host_1 = ComputingHost(
        host_id="QPU_1",
        controller_host_id="host_1",
        clock=clock,
        total_qubits=10,
        total_pre_allocated_qubits=10)

    computing_host_2 = ComputingHost(
        host_id="QPU_2",
        controller_host_id="host_1",
        clock=clock,
        total_qubits=10,
        total_pre_allocated_qubits=10)

    controller_host = ControllerHost(
        host_id="host_1",
        clock=clock,
        computing_host_ids=["QPU_1", "QPU_2"])

    # Add one way classical and quantum connection
    computing_host_1.add_connections(['QPU_2'])
    computing_host_2.add_connections(['QPU_1'])

    computing_host_1.start()
    computing_host_2.start()
    controller_host.start()

    network.add_hosts([
        computing_host_1,
        computing_host_2,
        controller_host])

    t1 = controller_host.run_protocol(controller_host_protocol)
    t2 = computing_host_1.run_protocol(computing_host_protocol)
    t3 = computing_host_2.run_protocol(computing_host_protocol)

    t1.join()
    t2.join()
    t3.join()
    network.stop(True)

if __name__ == '__main__':
    main()
