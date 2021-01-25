from qunetsim.components import Host

from interlinq.components import ComputingHost, Clock
from interlinq.utils import DefaultOperationTime
from interlinq.utils.constants import Constants
from interlinq.objects import Operation, Circuit, Layer

import numpy as np
import uuid
import json


class ControllerHost(Host):
    """
    Controller host object which acts as a master node in a centralised
    distributed network system.
    """

    def __init__(self, host_id: str, clock: Clock, computing_host_ids: list=[], gate_time: dict=None):
        """
        Returns the important things for the controller hosts

        Args:
            host_id (str): The ID of the controller host
            computing_host_ids (list): The IDs of computing/slave hosts
            clock (Clock): Clock object for synchronising the computing hosts
            gate_time (dict): A mapping of gate names to time the gate takes
               to execute for each computing host
        """
        super().__init__(host_id)

        self._computing_host_ids = computing_host_ids
        self.add_c_connections(computing_host_ids)
        self._clock = clock
        self._circuit_max_execution_time = 0

        # TODO: Take gate_time as an input from computing hosts
        if gate_time is None:
            gate_time = {}
            for computing_host_id in computing_host_ids:
                gate_time[computing_host_id] = DefaultOperationTime

        self._gate_time = gate_time
        self._results = None

    @property
    def computing_host_ids(self):
        """
        Get the *computing_host_ids* associated to the controller host
        Returns:
            (list): The IDs of computing/slave hosts
        """
        return self._computing_host_ids

    @property
    def results(self):
        """
        Get the final output of the algorithm or the error reported by the
        computing hosts
        Returns:
            (dict): The final output/error from every computing host
        """
        return self._results

    def create_distributed_network(self, num_computing_hosts: int, num_qubits_per_host: int) -> tuple:
        """
        Create a network of *num_computing_hosts* completely connected computing nodes with
        *num_qubits_per_host* each.

        Args:
            num_computing_hosts (int): The number of computing hosts to initalize
            num_qubits_per_host (int): The number of qubits on each computing host
        Returns:
            (tuple): The list of computing hosts and the qubit map for their qubits
        """

        id_prefix = "QPU_"
        computing_hosts = []
        q_map = {}
        self._computing_host_ids = [
            f'{id_prefix}{str(i)}' for i in range(num_computing_hosts)]

        for i in range(num_computing_hosts):
            computing_host = ComputingHost(
                host_id=id_prefix + str(i),
                controller_host_id=self.host_id,
                clock=self._clock,
                total_qubits=num_qubits_per_host,
                total_pre_allocated_qubits=num_qubits_per_host
            )
            self._gate_time[id_prefix + str(i)] = DefaultOperationTime
            self.add_c_connection(id_prefix + str(i))
            computing_hosts.append(computing_host)
            q_map[computing_host.host_id] = [
                f'q_{str(i)}_{str(j)}' for j in range(num_qubits_per_host)]

        for outer_computing_host in computing_hosts:
            for inner_computing_host in computing_hosts:
                if outer_computing_host.host_id != inner_computing_host.host_id:
                    outer_computing_host.add_connection(
                        inner_computing_host.host_id)
            outer_computing_host.start()

        return computing_hosts, q_map

    def connect_host(self, computing_host_id: str, gate_time: dict=None):
        """
        Adds a computing host to the distributed network

        Args:
            computing_host_id (str): The ID of the computing host
            gate_time (dict): A mapping of gate names to time the gate
                takes to execute for the computing host to be added
        """

        self._computing_host_ids.append(computing_host_id)
        self.add_c_connection(computing_host_id)

        if gate_time is None:
            gate_time = DefaultOperationTime

        self._gate_time[computing_host_id] = gate_time

    def connect_hosts(self, computing_host_ids: list, gate_times: list=None):
        """
        Adds multiple computing hosts to the distributed network

        Args:
            computing_host_id (list): The ID of the computing host
            gate_times (list): A list of mappings of gate names to time the gate
                takes to execute for the computing host to be added
        """

        for i, computing_host_id in enumerate(computing_host_ids):
            self._computing_host_ids.append(computing_host_id)
            self.add_c_connection(computing_host_id)

            if gate_times is None or len(gate_times) == 0 or gate_times[i] is None:
                gate_time = DefaultOperationTime
            else:
                gate_time = gate_times[i]

            self._gate_time[computing_host_id] = gate_time

    def _create_distributed_schedules(self, circuit: Circuit):
        """
        Creates a distributed schedule for each of the computing host

        Args:
            circuit (Circuit): The Circuit object which contains
                information regarding a quantum circuit
        """

        time_layer_end = 0
        operation_schedule = []

        layers = circuit.layers

        # We form an intermediate schedule which is used before splitting
        # the schedules for each computing host
        for layer in layers:
            max_execution_time = 0

            for operation in layer.operations:
                op = operation.get_dict()
                op['layer_end'] = time_layer_end

                operation_schedule.append(op)

                # Find the maximum time taken to execute this layer
                execution_time = self._get_operation_execution_time(
                    op['computing_host_ids'][0],
                    operation.name,
                    operation.gate)
                max_execution_time = max(max_execution_time, execution_time)

            time_layer_end += max_execution_time

        computing_host_schedules = {}

        for computing_host_id in self._computing_host_ids:
            computing_host_schedule = []

            for op in operation_schedule:
                if op['computing_host_ids'][0] == computing_host_id:
                    computing_host_schedule.append(op)
            computing_host_schedules[computing_host_id] = computing_host_schedule

        return computing_host_schedules, time_layer_end

    @staticmethod
    def _replace_control_gates(control_gate_info: list, current_layer: Layer):
        """
        Replace control gates with a distributed version of the control gate
        over the different computing hosts

        Args:
            control_gate_info (list): List of information regarding control
                gates present in one layer
            current_layer (Layer): Layer object in which the control gates
                are present
        """

        max_gates = 0
        for gate_info in control_gate_info:
            max_gates = max(len(gate_info['operations']), max_gates)

        circuit_len = Constants.DISTRIBUTED_CONTROL_CIRCUIT_LEN + max_gates
        operations = [[] for _ in range(circuit_len)]

        for gate_info in control_gate_info:
            control_qubit = gate_info['control_qubit']
            control_host = gate_info['computing_hosts'][0]
            target_host = gate_info['computing_hosts'][1]

            epr_qubit_id = str(uuid.uuid4())
            bit_id_1, bit_id_2 = str(uuid.uuid4()), str(uuid.uuid4())

            # Generate new EPR pair (counted in the pre-allocated qubits) for the
            # two computing hosts
            op_1 = Operation(
                name=Constants.SEND_ENT,
                qids=[epr_qubit_id],
                computing_host_ids=[control_host, target_host],
                pre_allocated_qubits=True)

            op_2 = Operation(
                name=Constants.REC_ENT,
                qids=[epr_qubit_id],
                computing_host_ids=[target_host, control_host],
                pre_allocated_qubits=True)

            current_layer.add_operations([op_1, op_2])

            # Circuit to implement distributed control gate
            itr = 0
            op_1 = Operation(
                name=Constants.TWO_QUBIT,
                qids=[control_qubit, epr_qubit_id],
                gate=Operation.CNOT,
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name=Constants.MEASURE,
                qids=[epr_qubit_id],
                cids=[bit_id_1],
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name=Constants.SEND_CLASSICAL,
                cids=[bit_id_1],
                computing_host_ids=[control_host, target_host])

            op_2 = Operation(
                name=Constants.REC_CLASSICAL,
                cids=[bit_id_1],
                computing_host_ids=[target_host, control_host])
            operations[itr].extend([op_1, op_2])

            itr += 1
            op_1 = Operation(
                name=Constants.CLASSICAL_CTRL_GATE,
                qids=[epr_qubit_id],
                cids=[bit_id_1],
                gate=Operation.X,
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            # The control gate we are trying to implement
            for op in gate_info['operations'][::-1]:
                itr += 1
                op_1 = Operation(
                    name=Constants.TWO_QUBIT,
                    qids=[epr_qubit_id, op.get_target_qubit()],
                    gate=op.gate,
                    gate_param=op.gate_param,
                    computing_host_ids=[target_host])
                operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name=Constants.SINGLE,
                qids=[epr_qubit_id],
                gate=Operation.H,
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name=Constants.MEASURE,
                qids=[epr_qubit_id],
                cids=[bit_id_2],
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name=Constants.SEND_CLASSICAL,
                cids=[bit_id_2],
                computing_host_ids=[target_host, control_host])

            op_2 = Operation(
                name=Constants.REC_CLASSICAL,
                cids=[bit_id_2],
                computing_host_ids=[control_host, target_host])
            operations[itr].extend([op_1, op_2])

            itr += 1
            op_1 = Operation(
                name=Constants.CLASSICAL_CTRL_GATE,
                qids=[control_qubit],
                cids=[bit_id_2],
                gate=Operation.Z,
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

        # Make the new layers from the operations
        distributed_layers = []
        if control_gate_info:
            for ops in operations:
                layer = Layer(ops)
                distributed_layers.append(layer)

        return current_layer, distributed_layers

    def _generate_distributed_circuit(self, circuit: Circuit):
        """
        Takes the user input monolithic circuit and converts it to a
        distributed circuit over the computing hosts connected to the
        controller host. Here, we replace the normal two qubit control
        gates to distributed control gates.

        Args:
            circuit (Circuit): The Circuit object which contains
                information regarding a quantum circuit
        """

        distributed_circuit_layers = []

        layers = circuit.layers
        control_gate_info = circuit.control_gate_info()

        for layer_index, layer in enumerate(layers):
            new_layer = Layer(operations=[])

            for op in layer.operations:
                if not op.is_control_gate_over_two_hosts():
                    new_layer.add_operation(op)

            new_layer, distributed_layers = self._replace_control_gates(
                control_gate_info[layer_index],
                new_layer)

            if new_layer.operations:
                distributed_circuit_layers.append(new_layer)
            distributed_circuit_layers.extend(distributed_layers)

        distributed_circuit = Circuit(circuit.q_map, distributed_circuit_layers)

        return distributed_circuit

    def _get_operation_execution_time(self, computing_host_id: str, op_name: str, gate: str):
        """
        Return the execution time for an operation for a specific computing
        host

        Args:
            computing_host_id (str): The IDs of computing/slave hosts
            op_name (str): Name of the operation
            gate (str): Name of the gate being performed in the operation,
                if any

        Returns:
            (float): The operation execution time
        """
        operation_time = self._gate_time[computing_host_id]

        gate_op_names = [
            Constants.SINGLE,
            Constants.TWO_QUBIT,
            Constants.CLASSICAL_CTRL_GATE]

        if op_name in gate_op_names:
            execution_time = operation_time[op_name][gate]
        else:
            execution_time = operation_time[op_name]

        return execution_time

    def generate_and_send_schedules(self, circuit: Circuit):
        """
        Generate and send distributed schedules to all the computing hosts
        associated to the circuit

        Args:
            circuit (Circuit): The Circuit object which contains information
                regarding a quantum circuit
        """

        distributed_circuit = self._generate_distributed_circuit(circuit)
        computing_host_schedules, max_execution_time = self._create_distributed_schedules(
            distributed_circuit)
        self._circuit_max_execution_time = max_execution_time

        self.send_broadcast(json.dumps(computing_host_schedules, cls=NumpyEncoder))

        # Wait for the computing hosts to receive the broadcast
        for host_id in self._computing_host_ids:
            self.get_classical(host_id, wait=-1)

        # Initialise the clock and start running the algorithm
        self._clock.initialise(max_execution_time)
        self._clock.start()

    def receive_results(self):
        """
        Receive the final output results from all the computing hosts
        """

        results = {}

        for host_id in self._computing_host_ids:
            result = self.get_classical(host_id, wait=-1, seq_num=1)

            # I think this is a bug with QuNetSim... Adding a hack for now
            # to overcome it...
            if result.content == 'ACK':
                result = self.get_classical(host_id, wait=-1, seq_num=1)

            try:
                result = result.content
                results.update(json.loads(result))
            except json.decoder.JSONDecodeError:
                pass

        self._results = results


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, complex):
            return (obj.real, obj.imag)
        return json.JSONEncoder.default(self, obj)
