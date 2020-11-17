from qunetsim.components import Host
from utils import DefaultOperationTime
from objects import Operation, Layer


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

        for computing_host_id in computing_host_id:
            self._computing_host_ids.append(computing_host_id)
            self.add_c_connection(computing_host_id)

            if gate_time is None:
                gate_time = default_gate_time

            self._gate_time[computing_host_id] = gate_time

    def _create_distributed_schedule(self, circuit):
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

    def _replace_cnot(self, layer_index, layer, circuit, op):
        """
        Replace cnot with a distributed control gate

        Args:
            layer (object): The layer object which is a collection of operations
                to be applied to the qubits in the system
        """

        control_qubit, target_qubit = op.qids[0], op.qids[1]
        control_host, target_host = op.computing_host_ids[0], op.computing_host_ids[1]

        new_layers = []

        # TODO: Discuss the IDs of these new qubits:
        op_1 = Operation(
            name="SEND_ENT",
            qids=["qid1", "qid2"],
            computing_host_ids=[control_host, target_host])

        op_2 = Operation(
            name="REC_ENT",
            qids=["qid2", "qid1"],
            computing_host_ids=[target_host, control_host])

        layer.add_operations([op_1, op_2])
        circuit.update_layer(layer_index, layer)

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=[control_qubit, "qid1"],
            gate="cnot",
            computing_host_ids=[control_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="MEASURE",
            qids=["qid1"],
            cids=["bit1"],
            computing_host_ids=[control_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="SEND_CLASSICAL",
            cids=["bit1"],
            computing_host_ids=[control_host, target_host])

        op_2 = Operation(
            name="REC_CLASSICAL",
            qids=["bit1"],
            computing_host_ids=[target_host, control_host])

        new_layers.append(Layer([op_1, op_2]))

        op_1 = Operation(
            name="CLASSICAL_CTRL_GATE",
            qids=["qid2"],
            cids=["bit1"],
            gate="X",
            computing_host_ids=[target_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="TWO_QUBIT",
            qids=["qid2", target_qubit],
            gate=op.gate,
            gate_param=op.gate_param,
            computing_host_ids=[target_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="SINGLE",
            qids=["qid2"],
            gate="H",
            computing_host_ids=[target_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="MEASURE",
            qids=["qid2"],
            cids=["bit2"],
            computing_host_ids=[target_host])

        new_layers.append(Layer([op_1]))

        op_1 = Operation(
            name="SEND_CLASSICAL",
            cids=["bit2"],
            computing_host_ids=[target_host, control_host])

        op_2 = Operation(
            name="REC_CLASSICAL",
            qids=["bit2"],
            computing_host_ids=[control_host, target_host])

        new_layers.append(Layer([op_1, op_2]))

        op_1 = Operation(
            name="SINGLE",
            qids=[control_qubit],
            gate="Z",
            computing_host_ids=[control_host])

        new_layers.append(Layer([op_1]))

        itr = 1
        for layer in new_layers:
            circuit.insert_layer(layer_index + itr, layer)
            itr += 1

        return circuit

    def _generate_distributed_circuit(self, circuit):
        """
        Takes the user input monolithic circuit and converts it to a distributed circuit
        over the computing hosts connected to the controller host. Here, we replace the
        normal two qubit control gates to distributed control gates.

        Args:
            circuit (object): The Circuit object which contains information
                regarding a quantum circuit
        """

        layers = circuit.layers

        for layer_index, layer in enumerate(layers):
            if layer.cnot_present():
                for op_index, op in enumerate(layer.operations):
                    if op.name == "TWO_QUBIT" and len(op.computing_host_ids) == 2:
                        layer.remove_operation(op_index)
                        circuit.update_layer(layer_index, layer)
                        # TODO: Further optimisation, instead of insert entire new layers
                        # insert relevant operations in existing layers
                        circuit = self._replace_cnot(layer_index, layer, circuit, op)

        return circuit

    def _get_operation_execution_time(self, computing_host_id, op_name, gate):
        """
        Return the execution time for an operation for a specific computing host

        Args:
            computing_host_ids (list): The IDs of computing/slave hosts
            op_name (str): Name of the operation
            gate (str): Name of the gate being performed in the operation, if any
        """
        operation_time = self._gate_time[computing_host_id]

        if op_name == "SINGLE" or op_name == "TWO_QUBIT" or op_name == "CLASSICAL_CTRL_GATE":
            execution_time = operation_time[op_name][gate]
        else:
            execution_time = operation_time[op_name]

        return execution_time

    def generate_schedules(self, circuit):
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

        return computing_host_schedules
