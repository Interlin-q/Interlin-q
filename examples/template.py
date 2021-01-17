import sys
sys.path.append("../")

from qunetsim.components import Network
from qunetsim.objects import Logger

from interlinq import (ControllerHost, Constants, Clock,
Circuit, Layer, ComputingHost, Operation)

import numpy as np

Logger.DISABLED = True


def create_circuit(q_map):
    """
    Create the necessary circuit here
    """
    layers = []
    computing_host_ids = list(q_map.keys())

    # Circuit input should be added

    # Prepare the qubits on both computing hosts
    ops = []
    for host_id in computing_host_ids:
        op = Operation(
            name=Constants.PREPARE_QUBITS,
            qids=q_map[host_id],
            computing_host_ids=[host_id])
        ops.append(op)

    layers.append(Layer(ops))

    # Put qubit "q_0_0" in |1> state
    op = Operation(
        name=Constants.SINGLE,
        qids=[q_map[computing_host_ids[0]][0]],
        gate=Operation.X,
        computing_host_ids=[computing_host_ids[0]])
    ops.append(op)

    layers.append(Layer(ops))

    # Apply cnot gate from "q_0_0" to "q_1_0"
    control_qubit_id = q_map[computing_host_ids[0]][0]
    target_qubit_id = q_map[computing_host_ids[1]][0]

    op = Operation(
        name=Constants.TWO_QUBIT,
        qids=[control_qubit_id, target_qubit_id],
        gate=Operation.CNOT,
        computing_host_ids=computing_host_ids)
    layers.append(Layer([op]))

    # Measure the qubits
    ops = []
    for host_id in computing_host_ids:
        op = Operation(
            name=Constants.MEASURE,
            qids=[q_map[host_id][0]],
            cids=[q_map[host_id][0]],
            computing_host_ids=[host_id])
        ops.append(op)
    layers.append(Layer(ops))

    circuit = Circuit(q_map, layers)
    return circuit


def controller_host_protocol(host, q_map):
    """
    Protocol for the controller host
    """

    circuit = create_circuit(q_map)
    host.generate_and_send_schedules(circuit)
    host.receive_results()

    results = host.results
    computing_host_ids = host.computing_host_ids

    print('Final results: \n')
    for computing_host_id in computing_host_ids:
        bits = results[computing_host_id]['bits']
        for bit_id, bit in bits.items():
            print("{0}: {1}".format(bit_id, bit))


def computing_host_protocol(host):
    """
    Protocol for the computing hosts
    """

    host.receive_schedule()
    host.send_results()


def main():
    # initialize network
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
        num_qubits_per_host=2)
    controller_host.start()

    network.add_host(controller_host)
    for host in computing_hosts:
        network.add_host(host)

    print('starting...')
    t = controller_host.run_protocol(controller_host_protocol, (q_map,))
    threads = [t]
    for host in computing_hosts:
        t = host.run_protocol(computing_host_protocol)
        threads.append(t)

    for thread in threads:    
        thread.join()
    network.stop(True)
    exit()


if __name__ == '__main__':
    main()
