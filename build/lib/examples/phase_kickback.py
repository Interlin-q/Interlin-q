import sys
sys.path.append("../")

from qunetsim.components import Network
from qunetsim.objects import Logger
from interlinq import ControllerHost, Clock, Circuit, \
    Layer, Operation, Qubit

Logger.DISABLED = True


def main():
    network = Network.get_instance()
    network.delay = 0.1
    network.start()

    clock = Clock()

    controller_host = ControllerHost(
        host_id="host_1",
        clock=clock,
    )
    computing_hosts, q_map = controller_host.create_distributed_network(num_computing_hosts=2,
                                                                        num_qubits_per_host=10)

    controller_host.start()
    network.add_hosts([
        computing_hosts[0],
        computing_hosts[1],
        controller_host])

    q_0_0 = Qubit(computing_host_id="QPU_0", q_id="q_0_0")
    q_0_1 = Qubit(computing_host_id="QPU_1", q_id="q_0_1")

    q_0_0.single(gate=Operation.I)
    q_0_0.two_qubit(gate=Operation.CNOT, target_qubit=q_0_1)

    q_0_0.measure(bit_id=q_0_0.q_id)
    q_0_1.measure(bit_id=q_0_1.q_id)

    qubits = [q_0_0, q_0_1]
    circuit = Circuit(q_map, qubits=qubits)

    def controller_host_protocol(host):
        host.generate_and_send_schedules(circuit)
        host.receive_results()
        print(host.results)

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
