from qunetsim.components import Host
from Distributed_Quantum_Phase_Estimation.utils import DefaultGateTime

default_gate_time = DefaultGateTime

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
                gate_time[computing_host_id] = default_gate_time

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
            gate_time = default_gate_time

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
            circuit (list): The circuit to schedule as a series of layers
        """

        pass
