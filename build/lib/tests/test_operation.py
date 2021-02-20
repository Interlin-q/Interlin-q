import unittest
from interlinq.objects import Operation


class TestOperation(unittest.TestCase):

    # Runs before all tests
    @classmethod
    def setUpClass(self) -> None:

        op_info = {
            'name': "SINGLE",
            'qids': ["qubit_1"],
            'cids': None,
            'gate': Operation.X,
            'gate_param': None,
            'pre_allocated_qubits': False,
            'computing_host_ids': ["QPU_1"]}

        self.operation = Operation(
            name=op_info['name'],
            qids=op_info['qids'],
            gate=op_info['gate'],
            computing_host_ids=op_info['computing_host_ids'])

        self._op_info = op_info

    # Runs after all tests
    @classmethod
    def tearDownClass(self) -> None:
        pass

    def test_instantiation(self):
        self.assertEqual(self.operation.name, "SINGLE")
        self.assertEqual(self.operation.gate, Operation.X)
        self.assertEqual(self.operation.computing_host_ids, ["QPU_1"])
        
        self.assertEqual(self.operation.get_dict(), self._op_info)
