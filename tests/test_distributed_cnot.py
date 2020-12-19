from components.controller_host import ControllerHost
from components.clock import Clock
from components.computing_host import ComputingHost
from objects.circuit import Circuit
from objects.layer import Layer
from objects.operation import Operation

from qunetsim.components.network import Network
from qunetsim.backends import EQSNBackend

import unittest
import time


class TestDistributedCnotProtocol(unittest.TestCase):

    # Runs before all tests
    @classmethod
    def setUpClass(cls) -> None:
        pass

    # Runs after all tests
    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self):
        network = Network.get_instance()
        network.start(["host_1", "QPU_1", "QPU_2"], EQSNBackend())

        clock = Clock()

        self.computing_host_1 = ComputingHost(
            host_id="QPU_1",
            controller_host_id="host_1",
            clock=clock,
            total_qubits=2)

        self.computing_host_2 = ComputingHost(
            host_id="QPU_2",
            controller_host_id="host_1",
            clock=clock,
            total_qubits=2)

        self.controller_host = ControllerHost(
            host_id="host_1",
            computing_host_ids=["QPU_1", "QPU_2"])

        self.computing_host_1.add_connections(['QPU_2'])
        self.computing_host_1.start()
        self.computing_host_2.add_connections(['QPU_1'])
        self.computing_host_2.start()
        self.controller_host.add_c_connections(['QPU_1', 'QPU_2'])
        self.controller_host.start()

        network.add_hosts([
            self.controller_host,
            self.computing_host_1,
            self.computing_host_2])

        self.network = network
        self.clock = clock

    def tearDown(self):
        self.network.stop(True)

    def test_cnot_protocol(self):
        q_map = {
            'QPU_1': ['qubit_1'],
            'QPU_2': ['qubit_2']}

        # TODO: Maybe layer one is always like this
        # Form layer 1
        op_1 = Operation(
            name="PREPARE_QUBITS",
            qids=["qubit_1"],
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="PREPARE_QUBITS",
            qids=["qubit_2"],
            computing_host_ids=["QPU_2"])

        layer_1 = Layer([op_1, op_2])

        # TODO: For operations, can the name and computing host ids be found from
        #       the gate name and qubit id? That would simplify the inputs
        #       We could have an OperationFactory object that takes the topology as input
        #       and then it can generate the operations using those two points

        # Form layer 2
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.X,
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="SINGLE",
            qids=["qubit_2"],
            gate=Operation.X,
            computing_host_ids=["QPU_2"])

        layer_2 = Layer([op_1, op_2])

        # Form layer 3
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_1", "qubit_2"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_1", "QPU_2"])

        layer_3 = Layer([op_1])

        # Form layer 4
        op_1 = Operation(
            name="MEASURE",
            qids=["qubit_1"],
            cids=["qubit_1"],
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="MEASURE",
            qids=["qubit_2"],
            cids=["qubit_2"],
            computing_host_ids=["QPU_2"])

        layer_4 = Layer([op_1, op_2])

        layers = [layer_1, layer_2, layer_3, layer_4]
        circuit = Circuit(q_map, layers)

        def controller_host_protocol(host):
            host.generate_and_send_schedules(circuit)

        def computing_host_1_protocol(host):
            host.receive_schedule()

        def computing_host_2_protocol(host):
            host.receive_schedule()

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_1_protocol)
            self.computing_host_2.run_protocol(computing_host_2_protocol)
            time.sleep(0.5)

        self.clock.initialise(self.controller_host)
        self.clock.start()
        self.assertEqual(self.clock._maximum_ticks, 13)

        self.assertEqual(self.computing_host_1._bits['qubit_1'], 1)
        self.assertEqual(self.computing_host_2._bits['qubit_2'], 0)

        def computing_host_1_protocol(host):
            host.send_results()

        def computing_host_2_protocol(host):
            host.send_results()

        def controller_host_protocol(host):
            host.receive_results()

        for i in range(1):
            self.computing_host_1.run_protocol(computing_host_1_protocol)
            self.computing_host_2.run_protocol(computing_host_2_protocol)
            self.controller_host.run_protocol(controller_host_protocol)
            time.sleep(0.5)

        self.assertEqual(self.controller_host._results['QPU_1']['qubit_1'], 1)
        self.assertEqual(self.controller_host._results['QPU_2']['qubit_2'], 0)
