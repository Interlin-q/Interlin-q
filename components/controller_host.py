from qunetsim.components import Host
from utils import DefaultOperationTime

class ControllerHost(Host):
    """
    Controller host object which acts as a master node in a centralised
    distributed network system.
    """

    def __init__(self, host_id, computing_host_ids, gate_time=None):
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

    def add_computing_host_to_network(self, computing_host_id, gate_time=None):
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

    def add_computing_hosts_to_network(self, computing_host_ids, gate_time=None):
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

    def create_distributed_schedule(self, circuit):
        """
        Creates a distributed schedule for each of the computing host

        Args:
            circuit (object): The circuit object which contains information
                regarding a quantum circuit
        """

        time_layer_end = 0
        operation_schedule = []

        layers = circuit.layers()

        # We form an intermediate schedule which is used before splitting the
        # schedules for each computing host
        for layer in layers:
            max_execution_time = 0

            for op in layer:
                op['layer_end'] = time_layer_end
                gate_schedule.append(op)

                if op['name'] = "SINGLE":
                    # TODO: Fix a format for op, so that a gate can be obtained
                    # directly
                    execution_time = DefaultOperationTime[op['name'][op['gate']]]
                else:
                    execution_time = DefaultOperationTime[op['name']]
                # Find the maximum time taken to execute this layer
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
