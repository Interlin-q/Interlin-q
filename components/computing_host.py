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

    def __init__(self, host_id, controller_host_id, total_qubits=0,
        total_pre_allocated_qubits=1, gate_time=None):

        """
        Returns the important things for the computing hosts

        Args:
            host_id (str): The ID of the computing host
            controller_host_id (str): The IDs of controller/master host
            total_qubits (int): Total number of processing qubits possessed by the computing
               host
            total_pre_allocated_qubits (int): Total number of pre allocated qubits (in case of
               generating an EPR pair) possessed by the computing host
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for this computing host
        """
        super().__init__(host_id)

        self._controller_host_id = controller_host_id

        self._total_qubits = total_qubits
        self._total_pre_allocated_qubits = total_pre_allocated_qubits

        self._qubits = None
        self._pre_allocated_qubits = None
        self._bits = None

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

    def _report_error(self, message):
        """
        Stop the processing and report the error message to the controller host

        Args:
            (str): Error message in a string
        """
        print(message)

    def _check_error(self, op, len_qids=0, len_computing_host_ids=1, len_cids=0):
        """
        Check if there is any error in the operation format

        Args:
            (Dict): Dictionary of information regarding the operation
            (int): Permissible number of qubit IDs in the operation
            (int): Permissible number of computing host IDs  in the operation
            (int): Permissible number of classical bit IDs in the operation
        """

        msg = "Error in the operation name: {0}.".format(op['name'])

        if len(operation['qids']) > len_qids:
            msg += "Error Message: 'Number of qubit IDs is exceeding the permissible number"

        if len(operation['computing_host_ids']) > len_computing_host_ids:
            msg += "Error Message: 'Number of computing host IDs is exceeding the permissible number"

        if len(operation['cids']) > len_cids:
            msg += "Error Message: 'Number of classical bit IDs is exceeding the permissible number"

        if operation['computing_host_ids'][0] != self._host_id:
            msg += "Error Message: 'Wrong input format for computing host ids in the operation'"

        self._report_error(msg)

    def _add_new_qubit(self, qubit, qubit_id, pre_allocated=False):
        """
        Add a new qubit in either 'qubits' property or 'pre_allocated_qubits' property

        Args:
            (Qubit): The qubit to be added
            (str): ID of the qubit to be added
            (bool): Boolean flag to check if the new qubit should be created in the pre_allocated
                register
        """
        if pre_allocated:
            if self._total_pre_allocated_qubits > 0:
                self._total_pre_allocated_qubits -= 1
            else:
                msg = "No more preallocated qubits left with the computing host"
                self._report_error(msg)

            self._pre_allocated_qubit[qubit_id] = epr_qubit
        else:
            qubits = self._qubits
            qubits[qubit_id] = epr_qubit
            self._update_stored_qubits(qubits)

    def _update_stored_qubits(self, qubits):
        """
        Update the stored qubits in the class

        Args:
            (Dict): Map of the qubit ids to the corresponding qubits stored with the
                computing host
        """

        if len(qubits) > total_qubits:
            msg = "Number of qubits required for the circuit are more than the total qubits"
            self._report_error(msg)

        self._qubits = qubits

    def _prepare_qubits(self, prepare_qubit_op):
        """
        Follows the operation command to prepare the necessary qubits

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        if prepare_qubits_op['name'] != Constants.PREPARE_QUBITS:
            return None

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

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=1)

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
                msg = "Wrong input format for the gate param in the operation"
                self._report_error(msg)
            qubit.custom_gate(operation['gate_param'])

    def _process_two_qubit_gates(self, operation):
        """
        Follows the operation command to perform two qubit gates on a qubit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=2, len_computing_host_ids=1)

        q_ids = operation['qids']
        qubit_1 = self._qubits[q_ids[0]]
        qubit_2 = self._qubits[q_ids[1]]

        if operation['gate'] == "cnot":
            qubit_1.cnot(qubit_2)

        if operation['gate'] == "cphase":
            qubit_1.cphase(qubit_2)

        if operation['gate'] == "custom_two_qubit_gate":
            if type(operation['gate_param']) is not np.ndarray:
                msg = "Wrong input format for gate param in the two qubit gate operation"
                self._report_error(msg)
            qubit_1.custom_two_qubit_gate(qubit_2, operation['gate_param'])

    def _process_classical_ctrl_gates(self, operation):
        """
        Follows the operation command to perform a classical control gate on a qubit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=1, len_cids=1)

        if operation['cids'][0]:
            self._process_single_gates(operation)

    def _process_send_ent(self, operation):
        """
        Follows the operation command to send EPR pair

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=2)

        qubit_id = operation['qids'][0]
        receiver_id = operation['computing_host_ids'][1]

        self.send_epr(receiver_id, q_id=qubit_id, await_ack=True)

        epr_qubit = self.get_epr(self.id, q_id=qubit_id)
        self._add_new_qubit(epr_qubit, qubit_id, operation['pre_allocated_qubits'])

    def _process_rec_ent(self, operation):
        """
        Follows the operation command to receive EPR pair

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=2)

        epr_qubit = self.get_epr(self.id, q_id=qubit_id)
        self._add_new_qubit(epr_qubit, qubit_id, operation['pre_allocated_qubits'])

    def _process_send_classical(self, operation):
        """
        Follows the operation command to receive a classical bit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=2, len_cids=1)

        bit_id = operation['cids'][0]

        if bit_id not in self._bits.keys():
            msg = "Bit not present in the computing host"
            self._report_error(msg)

        receiver_id = operation['computing_host_ids'][1]

        self.send_classical(receiver_id, self._bits[bit_id], await_ack=True)

    def _process_rec_classical(self, operation):
        """
        Follows the operation command to receive a classical bit

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=2, len_cids=1)

        sender_id = operation['computing_host_ids'][1]
        bit = host.get_classical(sender_id, wait=-1)

        self._bits[bit_id] = bit

    def _process_measure(self, operation):
        """
        Follows the operation command to measure a qubit and save the result

        Args:
            (Dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=1, len_cids=1)

        qubit_id = operation['qids'][0]
        bit_id = operation['cids'][0]

        if qubit_id in self._pre_allocated_qubits:
            qubit = self._pre_allocated_qubits[qubit_id]
        else:
            qubit = self._qubits[qubit_id]

        bit = qubit.measure()
        self._bits[bit_id] = bit

        if qubit_id in self._pre_allocated_qubits:
            del self._pre_allocated_qubits[qubit_id]
            self._total_pre_allocated_qubits -= 1
        else:
            del self._qubits[qubit_id]
            self._total_qubits -= 1

    def perform_schedule(self):
        """
        Process the schedule and perform the corresponding operations accordingly
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

            if operation['name'] == Constants.SEND_CLASSICAL:
                self._process_send_classical(operation)

            if operation['name'] == Constants.REC_CLASSICAL:
                self._process_rec_classical(operation)

            if operation['name'] == Constants.MEASURE:
                self._process_rec_classical(operation)
