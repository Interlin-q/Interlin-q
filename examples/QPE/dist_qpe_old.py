import sys

from qunetsim.backends import EQSNBackend

sys.path.append("../")

from qunetsim.components import Network
from qunetsim.objects import Logger

from interlinq import (ControllerHost, Constants, Clock,
                       Circuit, Layer, ComputingHost, Operation)

import numpy as np

Logger.DISABLED = False


def phase_gate(theta):
    return np.array([[1, 0], [0, np.exp(1j * theta)]])


def inverse_quantum_fourier_transform(q_ids, computing_host_ids, layers):
    """
    Performs inverse quantum fourier transform
    """

    q_ids.reverse()

    for i in range(len(q_ids)):
        target_qubit_id = q_ids[i]

        for j in range(i):
            control_qubit_id = q_ids[j]
            print(control_qubit_id, target_qubit_id)
            op = Operation(
                name=Constants.TWO_QUBIT,
                qids=[control_qubit_id, target_qubit_id],
                gate=Operation.CUSTOM_CONTROLLED,
                gate_param=phase_gate(-np.pi * (2 ** j) / (2 ** i)),
                computing_host_ids=[computing_host_ids[0]])
            layers.append(Layer([op]))

        op = Operation(
            name=Constants.SINGLE,
            qids=[target_qubit_id],
            gate=Operation.H,
            computing_host_ids=[computing_host_ids[0]])
        layers.append(Layer([op]))
    return layers


def quantum_phase_estimation_circuit(q_map, client_input_gate):
    """
    Returns the monolithic circuit for quantum phase estimation
    algorithm
    """
    layers = []
    computing_host_ids = list(q_map.keys())

    # Prepare the qubits on both computing hosts
    ops = []
    for host_id in computing_host_ids:
        op = Operation(
            name=Constants.PREPARE_QUBITS,
            qids=q_map[host_id],
            computing_host_ids=[host_id])
        ops.append(op)

    layers.append(Layer(ops))

    # Setup the qubits by apply Hadamard gates on qubits of QPU_1
    # and applying X gate to initialise qubit on QPU_2
    ops = []
    for q_id in q_map[computing_host_ids[0]]:
        op = Operation(
            name=Constants.SINGLE,
            qids=[q_id],
            gate=Operation.H,
            computing_host_ids=[computing_host_ids[0]])
        ops.append(op)

    op = Operation(
        name=Constants.SINGLE,
        qids=[q_map[computing_host_ids[1]][0]],
        gate=Operation.X,
        computing_host_ids=[computing_host_ids[1]])
    ops.append(op)

    layers.append(Layer(ops))

    # Apply controlled unitaries
    for i in range(len(q_map[computing_host_ids[0]])):
        max_iter = 2 ** i
        control_qubit_id = q_map[computing_host_ids[0]][i]
        target_qubit_id = q_map[computing_host_ids[1]][0]

        for _ in range(max_iter):
            op = Operation(
                name=Constants.TWO_QUBIT,
                qids=[control_qubit_id, target_qubit_id],
                gate=Operation.CUSTOM_CONTROLLED,
                gate_param=client_input_gate,
                computing_host_ids=computing_host_ids)
            layers.append(Layer([op]))

    # Inverse Fourier Transform circuit
    q_ids = q_map[computing_host_ids[0]].copy()
    layers = inverse_quantum_fourier_transform(
        q_ids,
        computing_host_ids,
        layers)

    # Measure the qubits
    ops = []
    for q_id in q_ids:
        op = Operation(
            name=Constants.MEASURE,
            qids=[q_id],
            cids=[q_id],
            computing_host_ids=[computing_host_ids[0]])
        ops.append(op)
    layers.append(Layer(ops))

    circuit = Circuit(q_map, layers)
    return circuit


def controller_host_protocol(host, q_map, client_input_gate):
    """
    Protocol for the controller host
    """

    circuit = quantum_phase_estimation_circuit(q_map, client_input_gate)
    host.generate_and_send_schedules(circuit)
    host.receive_results()

    results = host.results

    meas_results = results['QPU_0']['val']
    output = [0] * 3
    for qubit in meas_results.keys():
        output[int(qubit[-1])] = meas_results[qubit]
    decimal_value = 0
    output.reverse()
    for i, bit in enumerate(output):
        decimal_value += ((2 ** i) * bit)

    phase = decimal_value / 8
    print("The estimated value of the phase is {0}".format(phase))


def computing_host_protocol(host):
    """
    Protocol for the computing hosts
    """

    host.receive_schedule()
    host.send_results()


def main():
    # initialize network
    network = Network.get_instance()
    network.delay = 0.1
    network.start()

    controller_host = ControllerHost(
        host_id="host_1",
        backend=EQSNBackend()
    )

    computing_hosts, q_map = controller_host.create_distributed_network(
        num_computing_hosts=2,
        num_qubits_per_host=3)
    controller_host.start()

    network.add_hosts([
        computing_hosts[0],
        computing_hosts[1],
        controller_host])

    print('starting...')
    # For phase = 1/8
    # client_input_gate = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])
    # For phase = 1/3
    client_input_gate = np.array([[1, 0], [0, np.exp(1j * 2 * np.pi / 3)]])

    t1 = controller_host.run_protocol(
        controller_host_protocol,
        (q_map, client_input_gate))
    computing_hosts[0].run_protocol(computing_host_protocol)
    computing_hosts[1].run_protocol(computing_host_protocol, blocking=True)

    t1.join()

    network.stop(True)
    exit()


if __name__ == '__main__':
    main()
