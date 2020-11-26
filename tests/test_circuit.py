import unittest
from objects.circuit import Circuit
from objects.layer import Layer
from objects.operation import Operation


class TestCircuit(unittest.TestCase):

    # Runs before all tests
    @classmethod
    def setUpClass(self) -> None:
        q_map = {
            'qubit_1': 'QPU_1',
            'qubit_2': 'QPU_2',
            'qubit_3': 'QPU_1'}
        self.circuit = Circuit(q_map)
        self._q_map = q_map

    # Runs after all tests
    @classmethod
    def tearDownClass(self) -> None:
        pass

    def test_instantiation(self):
        self.assertEqual(self.circuit.total_qubits(), 3)
        self.assertEqual(self.circuit.q_map, self._q_map)
        self.assertEqual(self.circuit.layers, [])

        self.circuit.add_new_qubit({'qubit_4': 'QPU_2'})

        computing_host_map = self.circuit.computing_host_map()
        test_computing_host_map = {
            'QPU_1': ['qubit_1', 'qubit_3'],
            'QPU_2': ['qubit_2'],
            'QPU_4': ['qubit_4']}
        self.assertEqual(self.circuit.q_map, self._q_map)

        self.assertEqual(self.circuit.total_qubits(), 4)

        operations = [Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate="X",
            computing_host_ids=["QPU_1"])]
        layer = Layer(operations)
        self.circuit.add_layer_to_circuit(layer)

        self.assertNotEqual(self.circuit.layers, [])
        self.assertEqual(self.circuit.layers[0].operations[0].name, "SINGLE")
