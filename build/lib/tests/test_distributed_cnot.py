from interlinq.components import ControllerHost
from interlinq.components import Clock
from interlinq.components import ComputingHost
from interlinq.objects.circuit import Circuit
from interlinq.objects.layer import Layer
from interlinq.objects.qubit import Qubit
from interlinq.objects import Operation

from qunetsim.components.network import Network
from qunetsim.backends import EQSNBackend

import unittest
import time


class TestDistributedCnot(unittest.TestCase):

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
        network.start(["host_1", "QPU_1", "QPU_2", "QPU_3"], EQSNBackend())

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

        self.computing_host_3 = ComputingHost(
            host_id="QPU_3",
            controller_host_id="host_1",
            clock=clock,
            total_qubits=2)

        self.controller_host = ControllerHost(
            host_id="host_1",
            clock=clock,
            computing_host_ids=["QPU_1", "QPU_2", "QPU_3"])

        self.computing_host_1.add_connections(['QPU_2', 'QPU_3'])
        self.computing_host_1.start()
        self.computing_host_2.add_connections(['QPU_1', 'QPU_3'])
        self.computing_host_2.start()
        self.computing_host_3.add_connections(['QPU_1', 'QPU_2'])
        self.computing_host_3.start()

        self.controller_host.start()

        network.add_hosts([
            self.controller_host,
            self.computing_host_1,
            self.computing_host_2,
            self.computing_host_3])

        self.network = network
        self.clock = clock

    def tearDown(self):
        self.network.stop(True)

    @unittest.skip("")
    def test_cnot_1(self):
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
            host.receive_results()

        def computing_host_protocol(host):
            host.receive_schedule()
            host.send_results()

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_protocol)
            self.computing_host_2.run_protocol(computing_host_protocol)
            time.sleep(12)

        self.assertEqual(self.clock._maximum_ticks, 13)

        self.assertEqual(self.computing_host_1._bits['qubit_1'], 1)
        self.assertEqual(self.computing_host_2._bits['qubit_2'], 0)

        self.assertEqual(self.controller_host._results['QPU_1']['qubit_1'], 1)
        self.assertEqual(self.controller_host._results['QPU_2']['qubit_2'], 0)

    @unittest.skip("")
    def test_cnot_2(self):
        q_map = {
            'QPU_1': ['qubit_1'],
            'QPU_2': ['qubit_2']}

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

        # Form layer 2
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.X,
            computing_host_ids=["QPU_1"])

        layer_2 = Layer([op_1])

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
            host.receive_results()

        def computing_host_protocol(host):
            host.receive_schedule()
            host.send_results()

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_protocol)
            self.computing_host_2.run_protocol(computing_host_protocol)
            time.sleep(12)

        self.assertEqual(self.clock._maximum_ticks, 13)

        self.assertEqual(self.computing_host_1._bits['qubit_1'], 1)
        self.assertEqual(self.computing_host_2._bits['qubit_2'], 1)

        self.assertEqual(self.controller_host._results['QPU_1']['qubit_1'], 1)
        self.assertEqual(self.controller_host._results['QPU_2']['qubit_2'], 1)

    @unittest.skip("")
    def test_cnot_3(self):
        q_map = {
            'QPU_1': ['qubit_1'],
            'QPU_2': ['qubit_2'],
            'QPU_3': ['qubit_3']}

        # Form layer 1
        op_1 = Operation(
            name="PREPARE_QUBITS",
            qids=["qubit_1"],
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="PREPARE_QUBITS",
            qids=["qubit_2"],
            computing_host_ids=["QPU_2"])

        op_3 = Operation(
            name="PREPARE_QUBITS",
            qids=["qubit_3"],
            computing_host_ids=["QPU_3"])

        layer_1 = Layer([op_1, op_2, op_3])

        # Form layer 2
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.X,
            computing_host_ids=["QPU_1"])

        layer_2 = Layer([op_1])

        # Form layer 3
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_1", "qubit_2"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_1", "QPU_2"])

        layer_3 = Layer([op_1])

        # Form layer 4
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_3"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2", "QPU_3"])

        layer_4 = Layer([op_1])

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

        op_3 = Operation(
            name="MEASURE",
            qids=["qubit_3"],
            cids=["qubit_3"],
            computing_host_ids=["QPU_3"])

        layer_5 = Layer([op_1, op_2, op_3])

        layers = [layer_1, layer_2, layer_3, layer_4, layer_5]
        circuit = Circuit(q_map, layers)

        def controller_host_protocol(host):
            host.generate_and_send_schedules(circuit)
            host.receive_results()

        def computing_host_protocol(host):
            host.receive_schedule()
            host.send_results()

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_protocol)
            self.computing_host_2.run_protocol(computing_host_protocol)
            self.computing_host_3.run_protocol(computing_host_protocol)
            time.sleep(18)

        self.assertEqual(self.clock._maximum_ticks, 23)

        self.assertEqual(self.computing_host_1._bits['qubit_1'], 1)
        self.assertEqual(self.computing_host_2._bits['qubit_2'], 1)
        self.assertEqual(self.computing_host_3._bits['qubit_3'], 1)

        results = self.controller_host._results
        self.assertEqual(results['QPU_1']['type'], 'result')
        self.assertEqual(results['QPU_1']['bits']['qubit_1'], 1)
        self.assertEqual(results['QPU_2']['bits']['qubit_2'], 1)
        self.assertEqual(results['QPU_3']['bits']['qubit_3'], 1)

    def test_cnot_4(self):
        """
        Test with a different input type
        """
        q_map = {
            'QPU_1': ['q_1'],
            'QPU_2': ['q_2'],
            'QPU_3': ['q_3']}

        q_1 = Qubit(computing_host_id="QPU_1", q_id="q_1")
        q_2 = Qubit(computing_host_id="QPU_2", q_id="q_2")
        q_3 = Qubit(computing_host_id="QPU_3", q_id="q_3")

        q_1.single(gate=Operation.X)
        q_1.two_qubit(gate=Operation.CNOT, target_qubit=q_2)

        q_2.two_qubit(gate=Operation.CNOT, target_qubit=q_3)

        q_1.measure(bit_id=q_1.q_id)
        q_2.measure(bit_id=q_2.q_id)
        q_3.measure(bit_id=q_3.q_id)

        circuit = Circuit(q_map, qubits=[q_1, q_2, q_3])

        def controller_host_protocol(host):
            host.generate_and_send_schedules(circuit)
            host.receive_results()

        def computing_host_protocol(host):
            host.receive_schedule()
            host.send_results()

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_protocol)
            self.computing_host_2.run_protocol(computing_host_protocol)
            self.computing_host_3.run_protocol(computing_host_protocol)
            time.sleep(20)

        self.assertEqual(self.clock._maximum_ticks, 23)

        self.assertEqual(self.computing_host_1._bits['q_1'], 1)
        self.assertEqual(self.computing_host_2._bits['q_2'], 1)
        self.assertEqual(self.computing_host_3._bits['q_3'], 1)

        results = self.controller_host._results
        self.assertEqual(results['QPU_1']['type'], 'result')
        self.assertEqual(results['QPU_1']['bits']['q_1'], 1)
        self.assertEqual(results['QPU_2']['bits']['q_2'], 1)
