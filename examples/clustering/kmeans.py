from interlinq import (ControllerHost, Constants, Clock,
                       Circuit, Layer, Operation, Qubit)

import numpy as np
import pandas as pd
from qunetsim.components import Network
import matplotlib.pyplot as plt


def u2(psi, lam):
    return (1 / np.sqrt(2)) * \
           np.array([[1, -np.exp(1j * lam)],
                     [np.exp(1j * psi), np.exp(1j * (lam + psi))]])


def cswap():
    return np.array([[1, 0, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0, 0],
                     [0, 0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 1]])


def build_circuit(x_1: list, x_2: list, qpu_id: str, q_ids: list):
    q0 = Qubit(computing_host_id=qpu_id, q_id=q_ids[0])
    q1 = Qubit(computing_host_id=qpu_id, q_id=q_ids[1])
    q2 = Qubit(computing_host_id=qpu_id, q_id=q_ids[2])

    # Encoding
    q1.single(gate=Operation.CUSTOM, gate_param=u2(x_1[0], x_1[1]))
    q2.single(gate=Operation.CUSTOM, gate_param=u2(x_2[0], x_2[1]))

    q0.single(gate=Operation.H)
    q0.three_qubit(gate=Operation.CUSTOM_TWO_QUBIT_CONTROLLED,
                   target_qubit_1=q1,
                   target_qubit_2=q2,
                   gate_param=cswap())
    q0.single(gate=Operation.H)
    q0.measure()
    return [q0, q1, q2]


def controller_host_protocol(host: ControllerHost, q_map, data):
    centroids = []
    circuits = [[], [], []]
    for d in data:
        circuits[0].append(Circuit(q_map, qubits=build_circuit(centroids[0], d, 'QPU_0', q_map['QPU_0'])))
        circuits[1].append(Circuit(q_map, qubits=build_circuit(centroids[1], d, 'QPU_1', q_map['QPU_1'])))
        circuits[2].append(Circuit(q_map, qubits=build_circuit(centroids[2], d, 'QPU_2', q_map['QPU_2'])))

    for circuit in circuits[0]:
        host.generate_and_send_schedules(circuit)
    for circuit in circuits[1]:
        host.generate_and_send_schedules(circuit)
    for circuit in circuits[2]:
        host.generate_and_send_schedules(circuit)

    host.receive_results()
    results = host.results
    print(results)




def main():
    fig, ax = plt.subplots()
    ax.set(xlabel='Data Feature 1', ylabel='Data Feature 2')
    data = pd.read_csv('data.csv',
                       usecols=['Feature 1', 'Feature 2', 'Class'])

    is_green = data['Class'] == 'Green'
    is_black = data['Class'] == 'Blue'
    is_blue = data['Class'] == 'Black'

    green_data = data[is_green].drop(['Class'], axis=1)
    black_data = data[is_black].drop(['Class'], axis=1)
    blue_data = data[is_blue].drop(['Class'], axis=1)

    # This is the point we need to classify
    y_p = 0.141
    x_p = -0.161

    xgc = sum(green_data['Feature 1']) / len(green_data['Feature 1'])
    xbc = sum(blue_data['Feature 1']) / len(blue_data['Feature 1'])
    xkc = sum(black_data['Feature 1']) / len(black_data['Feature 1'])

    ygc = sum(green_data['Feature 2']) / len(green_data['Feature 2'])
    ybc = sum(blue_data['Feature 2']) / len(blue_data['Feature 2'])
    ykc = sum(black_data['Feature 2']) / len(black_data['Feature 2'])

    phi_list = [((x + 1) * np.pi / 2) for x in [x_p, xgc, xbc, xkc]]
    theta_list = [((x + 1) * np.pi / 2) for x in [y_p, ygc, ybc, ykc]]

    network = Network.get_instance()
    network.delay = 0
    network.start()

    clock = Clock()
    controller_host = ControllerHost(
        host_id="host_1",
        clock=clock,
    )
    computing_hosts, q_map = controller_host.create_distributed_network(
        num_computing_hosts=2,
        num_qubits_per_host=3)
    controller_host.start()
    network.add_hosts(computing_hosts + [controller_host])


if __name__ == "__main__":
    main()
