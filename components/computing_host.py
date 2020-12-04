from qunetsim.components import Host
from utils import DefaultOperationTime
from utils.constants import Constants
from qunetsim.objects import Qubit

import numpy as np
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
        self._qubits = None

        self._classical_bits = None
        self._schedule = []

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

        # TODO: Add encryption for this message
        schedules = json.loads(messages[0].content)
        if self._host_id in schedules:
            self._schedule = schedules[self._host_id]

        # TODO: Check for errors and report it back to controller host
        # immediately

    def _update_stored_qubits(self, qubits):
        """
        """

        if len(qubits) > total_qubits:
            # TODO: Report error back to controller host and stop
            pass

        self._qubits = qubits

    def _prepare_qubits(self, prepare_qubit_op):
        """
        Follows the operation command to prepare the necessary qubits

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if prepare_qubits_op['name'] != Constants.PREPARE_QUBITS:
            # TODO: Report error back to controller host and stop
            pass

        qubits = {}
        for qubit_id in prepare_qubits_op['qids']:
            qubits[qubit_id] = Qubit(host=self, q_id=qubit_id)

        return qubits

    def _process_single_gates(self, operation):
        """
        Follows the operation command to perform single gates on a qubit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if len(operation['qids'] > 1) or len(operation['computing_host_ids'] > 1):
            # TODO: Report error back to controller host and stop
            pass

        q_id = operation['qids'][0]
        qubit = self._qubits[q_id]

        if operation['gate'] == "I":
            qubit.I()

        if operation['gate'] == "X":
            qubit.X()

        if operation['gate'] == "Y":
            qubit.Y()

        if operation['gate'] == "Z":
            qubit.Z()

        if operation['gate'] == "T":
            qubit.T()

        if operation['gate'] == "H":
            qubit.H()

        if operation['gate'] == "K":
            qubit.K()

        if operation['gate'] == "rx":
            qubit.rx(operation['gate_param'])

        if operation['gate'] == "ry":
            qubit.ry(operation['gate_param'])

        if operation['gate'] == "rz":
            qubit.rz(operation['gate_param'])

        if operation['gate'] == "custom_gate":
            if type(operation['gate_param']) is not np.ndarray:
                # TODO: Report error back to controller host and stop
                pass
            qubit.custom_gate(operation['gate_param'])

    def _process_two_qubit_gates(self, operation):
        """
        Follows the operation command to perform two qubit gates on a qubit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if len(operation['qids'] != 2) or len(operation['computing_host_ids'] > 1):
            # TODO: Report error back to controller host and stop
            pass

        q_ids = operation['qids']
        qubit_1 = self._qubits[q_ids[0]]
        qubit_2 = self._qubits[q_ids[1]]

        if operation['gate'] == "cnot":
            qubit_1.cnot(qubit_2)

        if operation['gate'] == "cphase":
            qubit_1.cphase(qubit_2)

        if operation['gate'] == "custom_two_qubit_gate":
            if type(operation['gate_param']) is not np.ndarray:
                # TODO: Report error back to controller host and stop
                pass
            qubit_1.custom_two_qubit_gate(qubit_2, operation['gate_param'])

    def _process_classical_ctrl_gates(self, operation):
        """
        Follows the operation command to perform a classical control gate on a qubit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if len(operation['cids'] > 1):
            # TODO: Report error back to controller host and stop
            pass

        if operation['cids'][0]:
            self._process_single_gates(operation)

    def _process_send_ent(self, operation):
        """
        Follows the operation command to send EPR pair

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if len(operation['qids'] != 2) or len(operation['computing_host_ids'] != 1):
            # TODO: Report error back to controller host and stop
            pass

        if operation['computing_host_ids'][0] != self._host_id:
            # TODO: Report error back to controller host and stop
            pass

        received_id = operation['computing_host_ids'][1]

        if operation['pre_allocated_qubits']:
            if self._pre_allocated_qubits > 0:
                self._pre_allocated_qubits -= 1
            else:
                # TODO: Report error back to controller host and stop
                pass

        self.send_epr(receiver, await_ack=True)

    def _process_rec_ent(self, operation):
        """
        Follows the operation command to receive EPR pair

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if len(operation['qids'] != 2) or len(operation['computing_host_ids'] != 1):
            # TODO: Report error back to controller host and stop
            pass

        if operation['computing_host_ids'][0] != self._host_id:
            # TODO: Report error back to controller host and stop
            pass

    def perform_schedule(self):
        """
        """

        if self._schedule:
            qubits = self._prepare_qubits(self._schedule[0])
            self._update_stored_qubits(qubits)

        for operation in self._schedule:
            # TODO: Add a clock object layer in this section

            if operation['name'] == Constants.SINGLE:
                self._process_single_gates(operation)

            if operation['name'] == Constants.TWO_QUBIT:
                self._process_two_qubit_gates(operation)

            if operation['name'] == Constants.CLASSICAL_CTRL_GATE:
                self._process_classical_ctrl_gate(operation)

            if operation['name'] == Constants.SEND_ENT:
                self._process_send_ent(operation)

            if operation['name'] == Constants.REC_ENT:
                self._process_rec_ent(operation)
