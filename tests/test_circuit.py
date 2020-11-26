import unittest
from objects.circuit import Circuit
from objects.layer import Layer
from objects.operation import Operation


class TestCircuit(unittest.TestCase):

    # Runs before all tests
    @classmethod
    def setUpClass(self) -> None:
        pass

    # Runs after all tests
    @classmethod
    def tearDownClass(self) -> None:
        pass

    def setUp(self):
        q_map = {
            'qubit_1': 'QPU_1',
            'qubit_2': 'QPU_2',
            'qubit_3': 'QPU_1'}
        self._circuit = Circuit(q_map, layers=[])
        self._q_map = q_map

    def tearDown(self):
        del self._circuit

    def test_instantiation(self):
        self.assertEqual(self._circuit.total_qubits(), 3)
        self.assertEqual(self._circuit.q_map, self._q_map)
        self.assertEqual(self._circuit.layers, [])

        self._circuit.add_new_qubit({'qubit_4': 'QPU_2'})

        computing_host_map = self._circuit.computing_host_map()
        test_computing_host_map = {
            'QPU_1': ['qubit_1', 'qubit_3'],
            'QPU_2': ['qubit_2'],
            'QPU_4': ['qubit_4']}
        self.assertEqual(self._circuit.q_map, self._q_map)

        self.assertEqual(self._circuit.total_qubits(), 4)

        operations = [Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate="X",
            computing_host_ids=["QPU_1"])]
        layer = Layer(operations)
        self._circuit.add_layer_to_circuit(layer)

        self.assertNotEqual(self._circuit.layers, [])
        self.assertEqual(self._circuit.layers[0].operations[0].name, "SINGLE")

    def test_control_gate_info(self):
        self._circuit.add_new_qubit({'qubit_4': 'QPU_1'})
        self._circuit.add_new_qubit({'qubit_5': 'QPU_3'})
        self._circuit.add_new_qubit({'qubit_6': 'QPU_4'})

        self.assertEqual(self._circuit.total_qubits(), 6)

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_1"],
            gate="cnot",
            computing_host_ids=["QPU_2", "QPU_1"])

        op_2 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_5", "qubit_6"],
            gate="cnot",
            computing_host_ids=["QPU_3", "QPU_4"])

        layer_1 = Layer([op_1, op_2])

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_3"],
            gate="cnot",
            computing_host_ids=["QPU_2", "QPU_1"])

        layer_2 = Layer([op_1])

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_2", "qubit_4"],
            gate="cnot",
            computing_host_ids=["QPU_2", "QPU_1"])

        layer_3 = Layer([op_1])

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qubit_6", "qubit_1"],
            gate="cnot",
            computing_host_ids=["QPU_4", "QPU_1"])

        layer_4= Layer([op_1])

        self._circuit.add_layer_to_circuit(layer_1)
        self._circuit.add_layer_to_circuit(layer_2)
        self._circuit.add_layer_to_circuit(layer_3)
        self._circuit.add_layer_to_circuit(layer_4)

        control_gate_info = self._circuit.control_gate_info()

        self.assertEqual(len(control_gate_info[0]), 2)
        self.assertEqual(control_gate_info[0][0]['computing_hosts'], ['QPU_2', 'QPU_1'])
        self.assertEqual(control_gate_info[1], [])
        self.assertEqual(control_gate_info[2], [])

        self.assertEqual(len(control_gate_info[0][1]['operations']), 1)

        test_operations = control_gate_info[0][0]['operations']
        self.assertEqual(len(test_operations), 3)
        self.assertEqual(test_operations[0].get_target_qubit(), 'qubit_4')
        self.assertEqual(test_operations[1].get_target_qubit(), 'qubit_3')
        self.assertEqual(test_operations[2].get_target_qubit(), 'qubit_1')

        self.assertEqual(control_gate_info[0][0]['control_qubit'], 'qubit_2')
        self.assertEqual(control_gate_info[3][0]['control_qubit'], 'qubit_6')
