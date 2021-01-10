from qunetsim.components import Network
from qunetsim.objects import Logger
from interlinq import ControllerHost, Clock, Circuit, \
    Layer, Operation

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
    layers = []
    op_1 = Operation(
        name="PREPARE_QUBITS",
        qids=["q_0_0"],
        computing_host_ids=["QPU_0"])
    op_2 = Operation(
        name="PREPARE_QUBITS",
        qids=["q_1_0"],
        computing_host_ids=["QPU_1"])

    layers.append(Layer([op_1, op_2]))
    op_1 = Operation(
        name="SINGLE",
        qids=["q_0_0"],
        gate=Operation.I,
        computing_host_ids=["QPU_0"])

    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="TWO_QUBIT",
        qids=["q_0_0", "q_1_0"],
        gate=Operation.CNOT,
        computing_host_ids=["QPU_0", "QPU_1"])
    layers.append(Layer([op_1]))

    op_1 = Operation(
        name="MEASURE",
        qids=["q_0_0"],
        cids=["q_0_0"],
        computing_host_ids=["QPU_0"])

    op_2 = Operation(
        name="MEASURE",
        qids=["q_1_0"],
        cids=["q_1_0"],
        computing_host_ids=["QPU_1"])
    layers.append(Layer([op_1, op_2]))

    circuit = Circuit(q_map, layers)

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
