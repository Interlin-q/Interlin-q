from qunetsim.components import Host
from utils import DefaultOperationTime

import time
import json

class ComputingHost(Host):
    """
    Computing host object which acts as a slave node in a centralised
    distributed network system, connected to the controller host.
    """

    def __init__(self, host_id, controller_host_id, total_qubits=0, pre_allocated_qubits=1, gate_time=None):
        """
        Returns the important things for the computing hosts

        Args:
            host_id (str): The ID of the computing host
            controller_host_id (str): The IDs of controller/master host
            total_qubits (int): Total number of processing qubits possessed by the computing
               host
            pre_allocated_qubits (int): Total number of pre allocated qubits (in case of
               generating an EPR pair) possessed by the computing host
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for this computing host
        """
        super().__init__(host_id)

        self._controller_host_id = controller_host_id
        self._total_qubits = total_qubits
        self._pre_allocated_qubits = pre_allocated_qubits
        self._schedule = None

        if gate_time is None:
            gate_time = DefaultOperationTime

        self._gate_time = gate_time

    @property
    def controller_host_id(self):
        """
        Get the *controller_host_id* associated to the computing host
        Returns:
            (str): The ID of controller/master host
        """
        return self._controller_host_id

    def update_total_qubits(self, total_qubits):
        """
        Set a new value for *total_qubits* in the computing host
        Args:
            (int): Total number of qubits possessed by the computing host
        """

        self._total_qubits = total_qubits

    def receive_schedule(self):
        """
        Receive the broadcasted schedule from the Controller Host and update
        the schedule property
        """

        messages = []
        # Await broadcast messages from the controller host
        while len(messages) < 1:
            messages = self.classical
            messages = [x for x in messages if x.content != 'ACK']

        self._schedule = json.loads(messages[0].content)[self._host_id]
