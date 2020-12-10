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


class TestDistributedProtocol(unittest.TestCase):

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

        self.computing_host_1 = ComputingHost(
            host_id="QPU_1",
            controller_host_id="host_1",
            total_qubits=2)

        self.computing_host_2 = ComputingHost(
            host_id="QPU_2",
            controller_host_id="host_1",
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

        self._network = network

    def tearDown(self):
        self._network.stop(True)

    def test_distributed_scheduler(self):
        q_map = {
            'QPU_1': ['qubit_1', 'qubit_2'],
            'QPU_2': ['qubit_2', 'qubit_3']}

        # Form layer 1
        op_1 = Operation(
            name="SINGLE",
            qids=["qubit_1"],
            gate="H",
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
            qids=["qubit_2", "qubit_3"],
            gate="cnot",
            computing_host_ids=["QPU_2"])

        layer_2 = Layer([op_1])

        layers = [layer_1, layer_2]
        circuit = Circuit(q_map, layers)

        def controller_host_protocol(host):
            host.generate_and_send_schedules(circuit)

        def computing_host_1_protocol(host):
            host.receive_schedule()

        def computing_host_2_protocol(host):
            host.receive_schedule()

        computing_host_schedules, max_execution_time = self.controller_host._create_distributed_schedules(circuit)

        self.assertEqual(max_execution_time, 2)

        for i in range(1):
            self.controller_host.run_protocol(controller_host_protocol)
            self.computing_host_1.run_protocol(computing_host_1_protocol)
            self.computing_host_2.run_protocol(computing_host_2_protocol)
            time.sleep(0.5)

        self.assertEqual(self.controller_host._circuit_max_execution_time, 2)
        clock = Clock()
        clock.initialise_clock(self.controller_host)
        self.assertEqual(clock._maximum_ticks, 2)

        self.assertEqual(self.computing_host_1._schedule, computing_host_schedules['QPU_1'])
        self.assertEqual(self.computing_host_2._schedule, computing_host_schedules['QPU_2'])
