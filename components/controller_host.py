from qunetsim.components import Host
from utils import DefaultOperationTime


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

        computing_host_schedules = self._create_distributed_schedules(circuit)

        return computing_host_schedules
