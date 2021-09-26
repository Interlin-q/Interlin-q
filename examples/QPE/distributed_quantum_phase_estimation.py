import sys

from qunetsim.backends import EQSNBackend

sys.path.append("../../")

from qunetsim.components import Network
from qunetsim.objects import Logger

from interlinq import (ControllerHost, Constants, Clock,
                       Circuit, Layer, Operation, Qubit)

import numpy as np

Logger.DISABLED = True


def phase_gate(theta):
    return np.array([[1, 0], [0, np.exp(1j * theta)]])


def quantum_phase_estimation_circuit(q_map, client_input_gate):
    """
    Returns the monolithic circuit for quantum phase estimation
    algorithm
    """
    phase_qubit = Qubit(computing_host_id='QPU_0', q_id=q_map['QPU_0'][0])
    phase_qubit.single(Operation.X)

    measure_qubits = []
    for q_id in q_map['QPU_1']:
        q = Qubit(computing_host_id='QPU_1', q_id=q_id)
        q.single(Operation.H)
        measure_qubits.append(q)

    for i, q in enumerate(measure_qubits):
        for _ in range(2 ** i):
            q.two_qubit(Operation.CUSTOM_CONTROLLED, phase_qubit, client_input_gate)

    # Inverse Fourier Transform
    measure_qubits.reverse()
    for i, q in enumerate(measure_qubits):
        for j, q2 in enumerate(measure_qubits[:i]):
            q2.two_qubit(Operation.CUSTOM_CONTROLLED, q, phase_gate(-np.pi * (2 ** j) / (2 ** i)))
        q.single(gate=Operation.H)

    # Measure the qubits
    for q in measure_qubits:
        q.measure()

    circuit = Circuit(q_map, qubits=measure_qubits + [phase_qubit])
    return circuit


def controller_host_protocol(host, q_map, client_input_gate):
    """
    Protocol for the controller host
    """

    circuit = quantum_phase_estimation_circuit(q_map, client_input_gate)
    print(circuit.counts)
    circuit = host.generate_distributed_circuit(circuit)
    print(circuit.counts)
    host.generate_and_send_schedules(circuit)
    host.receive_results()


    results = host.results
    meas_results = results['QPU_1']['val']
    output = [0] * 3
    print(results)
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
    network.add_hosts(computing_hosts + [controller_host])

    print('starting...')
    # For phase = 1/8
    # client_input_gate = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])
    # For phase = 1/3
    client_input_gate = np.array([[1, 0], [0, np.exp(1j * 2 * np.pi / 3)]])
    t1 = controller_host.run_protocol(
        controller_host_protocol,
        (q_map, client_input_gate))
    t2 = computing_hosts[0].run_protocol(computing_host_protocol)
    t3 = computing_hosts[1].run_protocol(computing_host_protocol)

    t1.join()
    t2.join()
    t3.join()
    network.stop(True)
    exit()


if __name__ == '__main__':
    main()
