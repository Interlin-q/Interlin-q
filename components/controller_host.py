import uuid
import json

from qunetsim.components import Host
from utils import DefaultOperationTime
from objects import Operation, Circuit, Layer


class ControllerHost(Host):
    """
    Controller host object which acts as a master node in a centralised
    distributed network system.
    """

    def __init__(self, host_id, computing_host_ids=[], gate_time=None):
        """
        Returns the important things for the controller hosts

        Args:
            host_id (str): The ID of the controller host
            computing_host_ids (list): The IDs of computing/slave hosts
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for each computing host
        """
        super().__init__(host_id)

        self._computing_host_ids = computing_host_ids
        self.add_c_connections(computing_host_ids)

        if gate_time is None:
            gate_time = {}
            for computing_host_id in computing_host_ids:
                gate_time[computing_host_id] = DefaultOperationTime

        self._gate_time = gate_time

    @property
    def computing_host_ids(self):
        """
        Get the *computing_host_ids* associated to the controller host
        Returns:
            (list): The IDs of computing/slave hosts
        """
        return self._computing_host_ids

    def connect_host(self, computing_host_id, gate_time=None):
        """
        Adds a computing host to the distributed network

        Args:
            computing_host_id (str): The ID of the computing host
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for the computing host to be added
        """

        self._computing_host_ids.append(computing_host_id)
        self.add_c_connection(computing_host_id)

        if gate_time is None:
            gate_time = DefaultOperationTime

        self._gate_time[computing_host_id] = gate_time

    def connect_hosts(self, computing_host_ids, gate_time=None):
        """
        Adds multiple computing hosts to the distributed network

        Args:
            computing_host_id (List): The ID of the computing host
        """

        for computing_host_id in computing_host_ids:
            self._computing_host_ids.append(computing_host_id)
            self.add_c_connection(computing_host_id)

            if gate_time is None:
                gate_time = DefaultOperationTime

            self._gate_time[computing_host_id] = gate_time

    def _create_distributed_schedules(self, circuit):
        """
        Creates a distributed schedule for each of the computing host

        Args:
            circuit (object): The Circuit object which contains information
                regarding a quantum circuit
        """

        time_layer_end = 0
        operation_schedule = []

        layers = circuit.layers

        # We form an intermediate schedule which is used before splitting the
        # schedules for each computing host
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

        return computing_host_schedules

    def _replace_control_gates(self, control_gate_info, current_layer):
        """
        Replace control gates with a distributed version of the control gate over the
        different computing hosts

        Args:
            control_gate_info (List): List of information regarding control gates present
                in one layer
            current_layer (object): Layer object in which the control gates are present
        """

        # TODO: Discuss the IDs of these new qubits:

        max_gates = 0
        for gate_info in control_gate_info:
            max_gates = max(len(gate_info['operations']), max_gates)

        operations = [[] for _ in range(8 + max_gates)]

        for gate_info in control_gate_info:
            control_qubit = gate_info['control_qubit']
            control_host = gate_info['computing_hosts'][0]
            target_host = gate_info['computing_hosts'][1]

            epr_qubit_id_1, epr_qubit_id_2 = str(uuid.uuid4()), str(uuid.uuid4())
            bit_id_1, bit_id_2 = str(uuid.uuid4()), str(uuid.uuid4())

            # Generate new EPR pair (counted in the pre-allocated qubits) for the
            # two computing hosts
            op_1 = Operation(
                name="SEND_ENT",
                qids=[epr_qubit_id_1, epr_qubit_id_2],
                computing_host_ids=[control_host, target_host],
                pre_allocated_qubits=True)

            op_2 = Operation(
                name="REC_ENT",
                qids=[epr_qubit_id_2, epr_qubit_id_1],
                computing_host_ids=[target_host, control_host],
                pre_allocated_qubits=True)

            current_layer.add_operations([op_1, op_2])

            # Circuit to implement distributed control gate
            itr = 0
            op_1 = Operation(
                name="TWO_QUBIT",
                qids=[control_qubit, epr_qubit_id_1],
                gate="cnot",
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name="MEASURE",
                qids=[epr_qubit_id_1],
                cids=[bit_id_1],
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name="SEND_CLASSICAL",
                cids=[bit_id_1],
                computing_host_ids=[control_host, target_host])

            op_2 = Operation(
                name="REC_CLASSICAL",
                qids=[bit_id_1],
                computing_host_ids=[target_host, control_host])
            operations[itr].extend([op_1, op_2])

            itr += 1
            op_1 = Operation(
                name="CLASSICAL_CTRL_GATE",
                qids=[epr_qubit_id_2],
                cids=[bit_id_1],
                gate="X",
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            for op in gate_info['operations'][::-1]:
                itr += 1
                op_1 = Operation(
                    name="TWO_QUBIT",
                    qids=[epr_qubit_id_1, op.get_target_qubit()],
                    gate=op.gate,
                    gate_param=op.gate_param,
                    computing_host_ids=[target_host])
                operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name="SINGLE",
                qids=[epr_qubit_id_2],
                gate="H",
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name="MEASURE",
                qids=[epr_qubit_id_2],
                cids=[bit_id_2],
                computing_host_ids=[target_host])
            operations[itr].extend([op_1])

            itr += 1
            op_1 = Operation(
                name="SEND_CLASSICAL",
                cids=[bit_id_2],
                computing_host_ids=[target_host, control_host])

            op_2 = Operation(
                name="REC_CLASSICAL",
                qids=[bit_id_2],
                computing_host_ids=[control_host, target_host])
            operations[itr].extend([op_1, op_2])

            itr += 1
            op_1 = Operation(
                name="SINGLE",
                qids=[control_qubit],
                gate="Z",
                computing_host_ids=[control_host])
            operations[itr].extend([op_1])

        # Make the new layers from the operations
        distributed_layers = []
        if control_gate_info:
            for ops in operations:
                layer = Layer(ops)
                distributed_layers.append(layer)

        return current_layer, distributed_layers

    def _generate_distributed_circuit(self, circuit):
        """
        Takes the user input monolithic circuit and converts it to a distributed circuit
        over the computing hosts connected to the controller host. Here, we replace the
        normal two qubit control gates to distributed control gates.

        Args:
            circuit (object): The Circuit object which contains information
                regarding a quantum circuit
        """

        distributed_circuit_layers = []

        layers = circuit.layers
        control_gate_info = circuit.control_gate_info()

        for layer_index, layer in enumerate(layers):
            new_layer = Layer(operations=[])

            for op_index, op in enumerate(layer.operations):
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

    def _get_operation_execution_time(self, computing_host_id, op_name, gate):
        """
        Return the execution time for an operation for a specific computing host

        Args:
            computing_host_ids (list): The IDs of computing/slave hosts
            op_name (str): Name of the operation
            gate (str): Name of the gate being performed in the operation, if any
        """
        operation_time = self._gate_time[computing_host_id]

        GATE_OP_NAMES = ["SINGLE", "TWO_QUBIT", "CLASSICAL_CTRL_GATE"]

        if op_name in GATE_OP_NAMES:
            execution_time = operation_time[op_name][gate]
        else:
            execution_time = operation_time[op_name]

        return execution_time

    def generate_and_send_schedules(self, circuit):
        """
        Generate and send distributed schedules to all the computing hosts associated
        to the circuit

        Args:
            circuit (object): The Circuit object which contains information
                regarding a quantum circuit
        """

        # TODO: Implement sending schedule to the specific computing hosts.

        distributed_circuit = self._generate_distributed_circuit(circuit)
        computing_host_schedules = self._create_distributed_schedules(distributed_circuit)

        self.send_broadcast(json.dumps(computing_host_schedules))

        return computing_host_schedules
