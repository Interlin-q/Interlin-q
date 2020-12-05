from qunetsim.components import Host
from utils import DefaultOperationTime

import json
import uuid

class Clock(Host):
    """
    Computing host object which acts as a slave node in a centralised
    distributed network system, connected to the controller host.
    """

    def __init__(self, controller_host_id, computing_host_ids):
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
        host_id = str(uuid.uuid4())
        super().__init__(host_id)

        self._controller_host_id = controller_host_id
        self._computing_host_ids = computing_host_ids

        self.add_c_connection(controller_host_id)
        self.add_c_connections(computing_host_ids)

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

        # TODO: Add encryption for this message
        schedules = json.loads(messages[0].content)
        if self._host_id in schedules:
            self._schedule = schedules[self._host_id]

    def process_schedule(self):
        """
        """

        if self._schedule:
            for operation in self._schedule 
