from qunetsim.components import Host
from utils import DefaultOperationTime


class ComputingHost(Host):
    """
    Computing host object which acts as a slave node in a centralised
    distributed network system, connected to the controller host.
    """

    def __init__(self, host_id, controller_host_id, gate_time=None):
        """
        Returns the important things for the computing hosts

        Args:
            host_id (str): The ID of the computing host
            controller_host_id (str): The IDs of controller/master host
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for this computing host
        """
        super().__init__(host_id)

        self._controller_host_id = controller_host_id

        if gate_time is None:
            gate_time = DefaultOperationTime

        # TODO controller host should take this as input from computing host
        self._gate_time = gate_time

    @property
    def controller_host_id(self):
        """
        Get the *controller_host_id* associated to the computing host
        Returns:
            (str): The ID of controller/master host
        """
        return self._controller_host_id
