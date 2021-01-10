from qunetsim.components import Network
from qunetsim.objects import Logger

from interlinq import ControllerHost, Constants, Clock, Circuit, Layer, ComputingHost, Operation

import numpy as np

Logger.DISABLED = False


def phase_gate(theta):
    return np.array([[1, 0], [0, np.exp(1j * theta)]])


def quantum_phase_estimation_circuit():
    """
    Returns the monolithic circuit for quantum phase estimation
    algorithm
    """
    layers = []

    # We use T gate here
    t_gate = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])

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

    op_4 = Operation(
        name="SINGLE",
        qids=["qubit_4"],
        gate=Operation.X,
        computing_host_ids=["QPU_2"])

    layers.append(Layer([op_1, op_2, op_3, op_4]))

    # Apply controlled unitaries
    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_1", "qubit_4"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=t_gate,
        computing_host_ids=["QPU_1", "QPU_2"])

    layers.append(Layer([op_1]))

    for _ in range(2):
        op = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_4"],
            gate=Operation.CUSTOM_CONTROLLED,
            gate_param=t_gate,
            computing_host_ids=["QPU_1", "QPU_2"])
        layers.append(Layer([op]))

    for _ in range(4):
        op = Operation(
            name="TWO_QUBIT",
            qids=["qubit_3", "qubit_4"],
            gate=Operation.CUSTOM_CONTROLLED,
            gate_param=t_gate,
            computing_host_ids=["QPU_1", "QPU_2"])
        layers.append(Layer([op]))

    # Inverse Fourier Transform circuit
    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_3"],
        gate=Operation.H,
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_3", "qubit_2"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=phase_gate(-np.pi / 2),
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
        qids=["qubit_3", "qubit_1"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=phase_gate(-np.pi / 4),
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["qubit_2", "qubit_1"],
        gate=Operation.CUSTOM_CONTROLLED,
        gate_param=phase_gate(-np.pi / 2),
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="SINGLE",
        qids=["qubit_1"],
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
        print("qubit_1: ", host.bits['qubit_1'])
        print("qubit_2: ", host.bits['qubit_2'])
        print("qubit_3: ", host.bits['qubit_3'])


def main():
    # initialize network
    network = Network.get_instance()
    network.delay = 0
    network.start()

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

    print('starting...')
    t1 = controller_host.run_protocol(controller_host_protocol)
    t2 = computing_host_1.run_protocol(computing_host_protocol)
    t3 = computing_host_2.run_protocol(computing_host_protocol)

    t1.join()
    t2.join()
    t3.join()
    network.stop(True)
    exit()


if __name__ == '__main__':
    main()
