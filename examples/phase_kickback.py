import sys

sys.path.append("../")

from qunetsim.components import Network
from qunetsim.objects import Logger
from qunetsim.backends import QuTipBackend
from interlinq import ControllerHost, Clock, Circuit, Operation, Qubit

Logger.DISABLED = True


def main():
    network = Network.get_instance()
    network.delay = 0.1
    qutip = QuTipBackend()
    network.start(backend=qutip)

    controller_host = ControllerHost(
        host_id="host_1",
        backend=qutip
    )
    computing_hosts, q_map = controller_host \
        .create_distributed_network(num_computing_hosts=2,
                                    num_qubits_per_host=2)

    controller_host.start()

    network.add_hosts(computing_hosts + [controller_host])

    print(q_map)

    q_0_0 = Qubit(computing_host_id="QPU_0", q_id="q_0_0")
    q_0_1 = Qubit(computing_host_id="QPU_0", q_id="q_0_1")
    q_1_0 = Qubit(computing_host_id="QPU_1", q_id="q_1_0")
    q_1_1 = Qubit(computing_host_id="QPU_1", q_id="q_1_1")

    q_0_0.single(gate=Operation.X)
    q_0_1.single(gate=Operation.X)
    q_1_0.single(gate=Operation.X)
    q_1_1.single(gate=Operation.X)

    # This works
    # q_0_0.two_qubit(gate=Operation.CNOT, target_qubit=q_1_0)
    # q_0_1.two_qubit(gate=Operation.CNOT, target_qubit=q_1_1)

    # This doesn't work
    q_0_0.two_qubit(gate=Operation.CNOT, target_qubit=q_1_0)
    q_0_1.two_qubit(gate=Operation.CNOT, target_qubit=q_1_0)

    q_0_0.measure()
    q_0_1.measure()
    q_1_0.measure()
    q_1_1.measure()

    qubits = [q_0_0, q_0_1, q_1_0, q_1_1]
    circuit = Circuit(q_map, qubits=qubits)

    def controller_host_protocol(host):
        host.generate_and_send_schedules(circuit)
        host.receive_results()

    def computing_host_protocol(host):
        host.receive_schedule()
        host.send_results()
        print(host.host_id, host.bits)

    print('starting...')
    t = controller_host.run_protocol(controller_host_protocol)
    computing_hosts[0].run_protocol(computing_host_protocol)
    g = computing_hosts[1].run_protocol(computing_host_protocol)

    t.join()
    g.join()

    network.stop(True)


if __name__ == "__main__":
    main()
