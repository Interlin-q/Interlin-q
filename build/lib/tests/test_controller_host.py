from interlinq.components import ControllerHost
from interlinq.components import Clock
from interlinq.objects.circuit import Circuit
from interlinq.objects.layer import Layer
from interlinq.objects import Operation

from qunetsim.components.network import Network
from qunetsim.backends import EQSNBackend

import unittest


class TestControllerHost(unittest.TestCase):

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
        network.start(["host_1"], EQSNBackend())

        clock = Clock()

        self.controller_host = ControllerHost(
            host_id="host_1",
            clock=clock,
            computing_host_ids=["QPU_1"])
        network.add_host(self.controller_host)

        self._network = network

    def tearDown(self):
        self._network.stop(True)

    def test_instantiation(self):
        self.assertEqual(self.controller_host.host_id, "host_1")
        self.assertEqual(self.controller_host.computing_host_ids, ["QPU_1"])
        self.assertEqual(self.controller_host._get_operation_execution_time("QPU_1", "SINGLE", "X"), 1)

        self.controller_host.connect_host("QPU_2")
        self.assertEqual(self.controller_host.computing_host_ids, ["QPU_1", "QPU_2"])
        self.assertEqual(self.controller_host._get_operation_execution_time("QPU_1", "REC_ENT", None), 1)

    def test_distributed_scheduler(self):
        self.controller_host.connect_host("QPU_2")

        q_map = {
            'QPU_1': ['qubit_1', 'qubit_2'],
            'QPU_2': ['qubit_2', 'qubit_4']}

        # Form layer 1
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.H,
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="SEND_ENT",
            qids=["qubit_2"],
            computing_host_ids=["QPU_1", "QPU_2"])

        op_3 = Operation(
            name="REC_ENT",
            qids=["qubit_2"],
            computing_host_ids=["QPU_2", "QPU_1"])

        layer_1 = Layer([op_1, op_2, op_3])

        # Form layer 2
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_4"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2"])

        layer_2 = Layer([op_1])

        # Form layer 3
        op_1 = Operation(
            name="MEASURE",
            qids=["qubit_2"],
            cids=["bit_1"],
            computing_host_ids=["QPU_2"])

        layer_3 = Layer([op_1])

        # Form layer 4
        op_1 = Operation(
            name="SEND_CLASSICAL",
            cids=["bit_1"],
            computing_host_ids=["QPU_2", "QPU_1"])

        op_2 = Operation(
            name="REC_CLASSICAL",
            cids=["bit_1"],
            computing_host_ids=["QPU_1", "QPU_2"])

        layer_4 = Layer([op_1, op_2])

        # Form layer 5
        op_1 = Operation(
            name="CLASSICAL_CTRL_GATE",
            qids=["qubit_1"],
            cids=["bit_1"],
            gate=Operation.X,
            computing_host_ids=["QPU_1"])

        layer_5 = Layer([op_1])

        layers = [layer_1, layer_2, layer_3, layer_4, layer_5]
        circuit = Circuit(q_map, layers)

        computing_host_schedules, max_execution_time = self.controller_host._create_distributed_schedules(circuit)

        self.assertEqual(len(computing_host_schedules), 2)
        self.assertEqual(len(computing_host_schedules['QPU_1']), 4)
        self.assertEqual(len(computing_host_schedules['QPU_2']), 4)

        self.assertEqual(max_execution_time, 5)

        self.assertEqual(computing_host_schedules['QPU_1'][0]['name'], "SINGLE")
        self.assertEqual(computing_host_schedules['QPU_1'][0]['layer_end'], 0)
        self.assertEqual(computing_host_schedules['QPU_1'][1]['name'], "SEND_ENT")
        self.assertEqual(computing_host_schedules['QPU_1'][1]['layer_end'], 0)
        self.assertEqual(computing_host_schedules['QPU_1'][2]['name'], "REC_CLASSICAL")
        self.assertEqual(computing_host_schedules['QPU_1'][2]['layer_end'], 3)
        self.assertEqual(computing_host_schedules['QPU_1'][3]['name'], "CLASSICAL_CTRL_GATE")
        self.assertEqual(computing_host_schedules['QPU_1'][3]['layer_end'], 4)

        self.assertEqual(computing_host_schedules['QPU_2'][0]['name'], "REC_ENT")
        self.assertEqual(computing_host_schedules['QPU_2'][0]['layer_end'], 0)
        self.assertEqual(computing_host_schedules['QPU_2'][1]['name'], "TWO_QUBIT")
        self.assertEqual(computing_host_schedules['QPU_2'][1]['layer_end'], 1)
        self.assertEqual(computing_host_schedules['QPU_2'][2]['name'], "MEASURE")
        self.assertEqual(computing_host_schedules['QPU_2'][2]['layer_end'], 2)
        self.assertEqual(computing_host_schedules['QPU_2'][3]['name'], "SEND_CLASSICAL")
        self.assertEqual(computing_host_schedules['QPU_2'][3]['layer_end'], 3)

    def test_monolithic_to_distributed_circuit_algorithm_1(self):
        self.controller_host.connect_host("QPU_2")

        q_map = {
            'QPU_1': ['qubit_1', 'qubit_2'],
            'QPU_2': ['qubit_3', 'qubit_4'],
            'QPU_3': ['qubit_5']}

        # Form layer 1
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.H,
            computing_host_ids=["QPU_1"])

        op_2 = Operation(
            name="SINGLE",
            qids=["qubit_3"],
            gate=Operation.H,
            computing_host_ids=["QPU_2"])

        op_3 = Operation(
            name="SINGLE",
            qids=["qubit_3"],
            gate=Operation.H,
            computing_host_ids=["QPU_3"])

        layer_1 = Layer([op_1, op_2, op_3])

        # Form layer 2
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_3", "qubit_1"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2", "QPU_1"])

        op_2 = Operation(
            name="SINGLE",
            qids=["qubit_3"],
            gate=Operation.X,
            computing_host_ids=["QPU_3"])

        layer_2 = Layer([op_1, op_2])

        # Form layer 3
        op_1 = Operation(
            name="MEASURE",
            qids=["qubit_3"],
            cids=["bit_1"],
            computing_host_ids=["QPU_2"])

        layer_3 = Layer([op_1])

        layers = [layer_1, layer_2, layer_3]
        circuit = Circuit(q_map, layers)

        distributed_circuit = self.controller_host._generate_distributed_circuit(circuit)

        self.assertEqual(len(distributed_circuit.layers), 12)

        self.assertEqual(len(distributed_circuit.layers[0].operations), 3)
        self.assertEqual(len(distributed_circuit.layers[1].operations), 3)

        self.assertEqual(distributed_circuit.layers[1].operations[0].name, "SINGLE")
        self.assertEqual(distributed_circuit.layers[1].operations[1].name, "SEND_ENT")
        self.assertEqual(distributed_circuit.layers[1].operations[2].name, "REC_ENT")

        self.assertEqual(distributed_circuit.layers[2].operations[0].name, "TWO_QUBIT")
        self.assertEqual(distributed_circuit.layers[10].operations[0].name, "CLASSICAL_CTRL_GATE")

        self.assertEqual(distributed_circuit.layers[11].operations[0].name, "MEASURE")

    def test_monolithic_to_distributed_circuit_algorithm_2(self):
        self.controller_host.connect_hosts(["QPU_2", "QPU_3", "QPU_4", "QPU_5"])

        q_map = {
            'QPU_1': ['qubit_1', 'qubit_3', 'qubit_4'],
            'QPU_2': ['qubit_2'],
            'QPU_3': ['qubit_5'],
            'QPU_4': ['qubit_6'],
            'QPU_5': ['qubit_7']}

        # Form layer 1
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate=Operation.H,
            computing_host_ids=["QPU_1"])

        layer_1 = Layer([op_1])

        # Form layer 2
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_1"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2", "QPU_1"])

        op_2 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_5", "qubit_6"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_3", "QPU_4"])

        op_3 = Operation(
            name="SINGLE",
            qids=["qubit_7"],
            gate=Operation.H,
            computing_host_ids=["QPU_5"])

        layer_2 = Layer([op_1, op_2, op_3])

        # Form layer 3
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_3"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2", "QPU_1"])

        layer_3 = Layer([op_1])

        # Form layer 4
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_4"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_2", "QPU_1"])

        layer_4 = Layer([op_1])

        # Form layer 5
        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_1", "qubit_6"],
            gate=Operation.CNOT,
            computing_host_ids=["QPU_1", "QPU_4"])

        layer_5 = Layer([op_1])

        layers = [layer_1, layer_2, layer_3, layer_4, layer_5]
        circuit = Circuit(q_map, layers)

        distributed_circuit = self.controller_host._generate_distributed_circuit(circuit)

        layers = distributed_circuit.layers
        self.assertEqual(len(layers), 23)

        self.assertEqual(layers[0].operations[0].name, "SINGLE")

        layer_op_names = [i.name for i in layers[1].operations]
        self.assertEqual(layer_op_names, ['SINGLE', 'SEND_ENT', 'REC_ENT', 'SEND_ENT', 'REC_ENT'])

        layer_op_names = [i.name for i in layers[2].operations]
        self.assertEqual(layer_op_names, ["TWO_QUBIT", "TWO_QUBIT"])

        self.assertEqual(layers[6].operations[0].name, "TWO_QUBIT")
        self.assertEqual(layers[6].operations[1].name, "TWO_QUBIT")
        self.assertEqual(layers[7].operations[0].name, "TWO_QUBIT")
        self.assertEqual(layers[7].operations[1].name, "SINGLE")
        self.assertEqual(layers[8].operations[0].name, "TWO_QUBIT")

        layer_op_names = [i.name for i in layers[11].operations]
        self.assertEqual(layer_op_names, ['SEND_CLASSICAL', 'REC_CLASSICAL'])

        layer_op_names = [i.name for i in layers[13].operations]
        self.assertEqual(layer_op_names, ['SEND_ENT', 'REC_ENT'])

        self.assertEqual(layers[22].operations[0].name, "CLASSICAL_CTRL_GATE")
