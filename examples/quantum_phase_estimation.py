from qunetsim.components import Host, Network
from qunetsim.objects import Qubit, Logger
from qunetsim.backends import EQSNBackend
import numpy as np

Logger.DISABLED = True


def phase_gate(theta):
    return np.array([[1, 0], [0, np.exp(1j * theta)]])


def quantum_phase_estimation_protocol(host):
    qubit_1 = Qubit(host=host, q_id="qubit_1")
    qubit_2 = Qubit(host=host, q_id="qubit_2")
    qubit_3 = Qubit(host=host, q_id="qubit_3")
    qubit_4 = Qubit(host=host, q_id="qubit_4")

    # We pick T gate as the unitary gate
    t_gate = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])

    qubit_1.H()
    qubit_2.H()
    qubit_3.H()

    qubit_4.X()

    qubit_1.custom_controlled_gate(qubit_4, t_gate)

    qubit_2.custom_controlled_gate(qubit_4, t_gate)
    qubit_2.custom_controlled_gate(qubit_4, t_gate)

    qubit_3.custom_controlled_gate(qubit_4, t_gate)
    qubit_3.custom_controlled_gate(qubit_4, t_gate)
    qubit_3.custom_controlled_gate(qubit_4, t_gate)
    qubit_3.custom_controlled_gate(qubit_4, t_gate)

    # Inverse fourier transform
    qubit_3.H()
    qubit_3.custom_controlled_gate(qubit_2, phase_gate(-np.pi / 2))

    qubit_2.H()
    qubit_3.custom_controlled_gate(qubit_1, phase_gate(-np.pi / 4))
    qubit_2.custom_controlled_gate(qubit_1, phase_gate(-np.pi / 2))

    qubit_1.H()

    bit_1 = qubit_1.measure()
    bit_2 = qubit_2.measure()
    bit_3 = qubit_3.measure()

    # TODO this should be bit_1 = 1, bit_2 = 0, bit_3 = 0
    print("qubit_3: ", bit_3)
    print("qubit_2: ", bit_2)
    print("qubit_1: ", bit_1)


def main():
    # initialize network
    network = Network.get_instance()
    backend = EQSNBackend()

    nodes = ['QPU']
    network.start(nodes, backend)
    network.delay = 0.2

    host = Host('QPU')

    host.start()
    network.add_host(host)

    t1 = host.run_protocol(quantum_phase_estimation_protocol)
    t1.join()
    network.stop(True)


if __name__ == '__main__':
    main()
