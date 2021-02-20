import unittest
from interlinq.objects.layer import Layer
from interlinq.objects import Operation


class TestLayer(unittest.TestCase):

    # Runs before all tests
    @classmethod
    def setUpClass(self) -> None:

        op_info_1 = {
            'name': "SINGLE",
            'qids': ["qubit_3"],
            'gate': Operation.X,
            'computing_host_ids': ["QPU_3"]}

        op_info_2 = {
            'name': "SEND_ENT",
            'qids': ["qubit_1", "qubit_2"],
            'computing_host_ids': ["QPU_1", "QPU_2"]}

        op_info_3 = {
            'name': "REC_ENT",
            'qids': ["qubit_2", "qubit_1"],
            'computing_host_ids': ["QPU_2", "QPU_1"]}

        self.operation_1 = Operation(
            name=op_info_1['name'],
            qids=op_info_1['qids'],
            gate=op_info_1['gate'],
            computing_host_ids=op_info_1['computing_host_ids'])

        self.layer = Layer([self.operation_1])

        self._op_info_1 = op_info_1
        self._op_info_2 = op_info_2
        self._op_info_3 = op_info_3
        

    # Runs after all tests
    @classmethod
    def tearDownClass(self) -> None:
        pass

    def test_instantiation(self):
        self.assertEqual(len(self.layer.operations), 1)
        self.assertEqual(self.layer.operations[0].name, "SINGLE")

        self.operation_2 = Operation(
            name=self._op_info_2['name'],
            qids=self._op_info_2['qids'],
            computing_host_ids=self._op_info_2['computing_host_ids'])

        self.operation_3 = Operation(
            name=self._op_info_3['name'],
            qids=self._op_info_3['qids'],
            computing_host_ids=self._op_info_3['computing_host_ids'])

        self.layer.add_operations([self.operation_2, self.operation_3])
        self.assertEqual(len(self.layer.operations), 3)

        self.assertEqual(self.layer.operations[2].name, "REC_ENT")
        self.assertEqual(self.layer.operations[1].computing_host_ids[0], "QPU_1")

        self.layer.remove_operation(index=0)
        self.assertEqual(len(self.layer.operations), 2)
        self.assertEqual(self.layer.operations[1].name, "REC_ENT")
