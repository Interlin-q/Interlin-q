import json
import time
from typing import Optional, Dict

import numpy as np
from qunetsim.components import Host
from qunetsim.objects import Qubit

from .clock import Clock
from ..objects.operation import Operation
from ..utils import DefaultOperationTime
from ..utils.constants import Constants
from ..utils.vqe_subroutines import expectation_value

MAX_WAIT = 5


class ComputingHost(Host):
    """
    Computing host object which acts as a slave node in a centralised
    distributed network system, connected to the controller host.
    """

    def __init__(
            self,
            host_id: str,
            controller_host_id: str,
            total_qubits: int = 0,
            total_pre_allocated_qubits: int = 1,
            gate_time: Optional[Dict[str, int]] = None,
            backend: Optional = None,
    ):

        """
        Returns the important things for the computing hosts

        Args:
            host_id (str): The ID of the computing host
            controller_host_id (str): The IDs of controller/master host
            total_qubits (int): Total number of processing qubits possessed by
               the computing host
            total_pre_allocated_qubits (int): Total number of pre allocated qubits
               (in case of generating an EPR pair) possessed by the computing host
            gate_time (dict): A mapping of gate names to time the gate takes to
               execute for this computing host
            backend (Backend): Backend for this host
        """
        super().__init__(host_id, backend=backend)

        self.add_c_connection(controller_host_id)
        self._controller_host_id = controller_host_id

        self._total_qubits = total_qubits
        self._total_pre_allocated_qubits = total_pre_allocated_qubits

        self._qubits = {}
        self._pre_allocated_qubits = {}
        self._bits = {}

        self._error_message = None

        self._schedule = {}

        if gate_time is None:
            gate_time = DefaultOperationTime

        self._gate_time = gate_time

        self._last_buffer_size = 0

        # Attach computing host to the clock
        self._clock = Clock.get_instance()
        self._clock.attach_host(self)

    @property
    def controller_host_id(self):
        """
        Get the *controller_host_id* associated to the computing host

        Returns:
            (str): The ID of controller/master host
        """
        return self._controller_host_id

    @property
    def bits(self):
        """
        Get the classical bits measured by this host.

        Returns:
            (dict): The dictionary of bits
        """
        results = {}
        for i in self._bits:
            # Hack to filter out EPR pairs
            # TODO: Is there a better way to overcome this?
            if len(i) < 15:
                results[i] = self._bits[i]
        return results

    @property
    def qubit_ids(self):
        """
        Return the qubit IDs for this computing host.

        Returns:
            (list): The IDs of the qubits stored by this computing host.
        """
        return list(self._qubits.keys())

    @property
    def total_qubits(self):
        """
        Return the total number of qubits for computing host.

        Returns:
            (int): The total number of qubits stored by this computing host.
        """
        return self._total_qubits

    @property
    def assigned_hamiltonian(self):
        """
        Return the currently assigned Hamiltonians for this host.

        Returns:
            (list): A list of the assigned terms of this computing host.
        """
        return self._hamiltonian

    def update_total_qubits(self, total_qubits: int):
        """
        Set a new value for *total_qubits* in the computing host.

        Args:
            (int): Total number of qubits possessed by the computing host
        """
        self._total_qubits = total_qubits

    def receive_schedule(self):
        """
        Receive the broadcast schedule from the Controller Host and update
        the schedule property
        """

        messages = []

        while len(messages) <= self._last_buffer_size:
            messages = self.classical
            messages = [x for x in messages if x.content != "ACK"]

        self._last_buffer_size = len(messages)

        # Await broadcast messages from the controller host
        # while len(messages) < 1:
        #    messages = self.classical
        #    messages = [x for x in messages if x.content != 'ACK']

        # TODO: Add encryption for this message
        schedules = json.loads(messages[0].content)
        schedule = {}

        if self._host_id in schedules:
            for op in schedules[self._host_id]:
                if op["layer_end"] in schedule.keys():
                    schedule[op["layer_end"]].append(op)
                else:
                    schedule[op["layer_end"]] = [op]
        self._schedule = schedule

        # Send Acknowledgement of receiving broadcast to the ControllerHost
        msg = "ACK"
        self.send_classical(self._controller_host_id, msg, await_ack=True)

    def _report_error(self, message: str):
        """
        Stop the processing and report the error message to the controller host

        Args:
            (str): Error message in a string
        """
        self._clock.stop_clock()
        self._error_message = message

    def _check_errors(
            self, op, len_qids: int = 0, len_computing_host_ids: int = 1, len_cids: int = 0
    ):
        """
        Check if there is any error in the operation format

        Args:
            op (Dict): Dictionary of information regarding the operation
            len_qids (int): Permissible number of qubit IDs in the operation
            len_computing_host_ids (int): Permissible number of computing
                host IDs in the operation
            len_cids (int): Permissible number of classical bit IDs in the
                operation
        """

        msg = None
        error_msg = "Error in the operation name: {0}. ".format(op["name"])

        if op["qids"]:
            if len(op["qids"]) > len_qids:
                msg = (
                        error_msg + "Error Message: 'Number of qubit IDs is "
                                    "exceeding the permissible number"
                )

        if len(op["computing_host_ids"]) > len_computing_host_ids:
            msg = (
                    error_msg + "Error Message: 'Number of computing host IDs "
                                "is exceeding the permissible number"
            )

        if op["cids"]:
            if len(op["cids"]) > len_cids:
                msg = (
                        error_msg + "Error Message: 'Number of classical bit IDs"
                                    "is exceeding the permissible number"
                )

        if op["computing_host_ids"][0] != self._host_id:
            msg = (
                    error_msg + "Error Message: 'Wrong input format for computing"
                                "host ids in the operation'"
            )

        if op["name"] == "REC_HAMILTON" and (
                len(op["hamiltonian"]) == 0 or op["hamiltonian"] is None
        ):
            msg = (
                    error_msg + "Error Message: 'Received an empty/no list of observables'"
            )

        if op["name"] == "SEND_EXP" and (
                len(self._hamiltonian) == 0 or self._hamiltonian is None
        ):
            msg = (
                    error_msg + "Error Message: 'Received an empty/no list of observables'"
            )

        if msg:
            self._report_error(msg)

    def _add_new_qubit(self, qubit: Qubit, qubit_id: str, pre_allocated: bool = False):
        """
        Add a new qubit in either 'qubits' property or 'pre_allocated_qubits'
        property.

        Args:
            qubit (Qubit): The qubit to be added
            qubit_id (str): ID of the qubit to be added
            pre_allocated (bool): Boolean flag to check if the new qubit should
                be created in the pre_allocated register
        """
        if pre_allocated:
            if self._total_pre_allocated_qubits > 0:
                self._total_pre_allocated_qubits -= 1
            else:
                msg = "No more preallocated qubits left with the computing host"
                self._report_error(msg)

            self._pre_allocated_qubits[qubit_id] = qubit
        else:
            qubits = self._qubits
            qubits[qubit_id] = qubit
            self._update_stored_qubits(qubits)

    def _get_stored_qubit(self, qubit_id: str) -> Qubit:
        """
        Extract the qubit from the computing host given the qubit id.

        Args:
            qubit_id (str): ID of the qubit to be added
        """
        if qubit_id in self._qubits:
            return self._qubits[qubit_id]
        if qubit_id in self._pre_allocated_qubits:
            return self._pre_allocated_qubits[qubit_id]

    def _update_stored_qubits(self, qubits: Dict[str, Qubit]):
        """
        Update the stored qubits in the class

        Args:
            qubits (dict): Map of the qubit ids to the corresponding qubits
                stored with the computing host
        """

        if len(qubits) + len(self.qubit_ids) > self._total_qubits:
            msg = (
                "Number of qubits required for the circuit are more "
                "than the total qubits"
            )
            self._report_error(msg)
        self._qubits.update(qubits)

        # if len(self.qubit_ids) > 1:
        #     self._merge_qubits(qubits)

    @staticmethod
    def extract_gate_param(op: dict) -> np.ndarray:
        """
        Extract gate parameter array as an np array

        Args:
            op (dict): Dictionary of information regarding the operation

        Returns:
            (np.ndarray): The parameter array.
        """

        param = op["gate_param"]
        for i in range(len(param)):
            for j in range(len(param[0])):
                if type(param[i][j]) != int:
                    param[i][j] = param[i][j][0] + param[i][j][1] * 1j
        return np.asarray(param)

    def _prepare_qubits(self, prepare_qubit_op: dict):
        """
        Follows the operation command to prepare the necessary qubits

        Args:
            prepare_qubit_op (dict): Dictionary of information regarding
                the operation
        """

        qubits = {}
        for qubit_id in prepare_qubit_op["qids"]:
            qubits[qubit_id] = Qubit(host=self, q_id=qubit_id)
            self.add_data_qubit(self.host_id, qubits[qubit_id], qubit_id)
        self._update_stored_qubits(qubits)

    def _merge_qubits(self, qubits: dict):
        main_qubit = self._get_stored_qubit(self.qubit_ids[0])
        for q_id in qubits.keys():
            qubit = self._get_stored_qubit(q_id)
            main_qubit.cnot(qubit)
            main_qubit.cnot(qubit)
            print("did this", self.host_id)

    def _process_single_gates(self, operation: dict, classical_ctrl_gate: bool = False):
        """
        Follows the operation command to perform single gates on a qubit

        Args:
            operation (dict): Dictionary of information regarding the operation
            classical_ctrl_gate (bool): If the single gate being performed is part of a
                classical control single gate
        """

        if not classical_ctrl_gate:
            self._check_errors(op=operation, len_qids=1, len_computing_host_ids=1)

        q_id = operation["qids"][0]
        qubit = self._get_stored_qubit(q_id)

        if operation["gate"] == Operation.I:
            qubit.I()

        elif operation["gate"] == Operation.X:
            qubit.X()

        elif operation["gate"] == Operation.Y:
            qubit.Y()

        elif operation["gate"] == Operation.Z:
            qubit.Z()

        elif operation["gate"] == Operation.T:
            qubit.T()

        elif operation["gate"] == Operation.H:
            qubit.H()

        elif operation["gate"] == Operation.K:
            qubit.K()

        elif operation["gate"] == Operation.RX:
            qubit.rx(operation["gate_param"])

        elif operation["gate"] == Operation.RY:
            qubit.ry(operation["gate_param"])

        elif operation["gate"] == Operation.RZ:
            qubit.rz(operation["gate_param"])

        elif operation["gate"] == Operation.CUSTOM:
            gate_param = self.extract_gate_param(operation)
            qubit.custom_gate(gate_param)

    def _process_two_qubit_gates(self, operation: dict):
        """
        Follows the operation command to perform two qubit gates on a qubit

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=2, len_computing_host_ids=1)

        q_ids = operation["qids"]
        qubit_1 = self._get_stored_qubit(q_ids[0])
        qubit_2 = self._get_stored_qubit(q_ids[1])

        if operation["gate"] == Operation.CNOT:
            qubit_1.cnot(qubit_2)

        elif operation["gate"] == Operation.CPHASE:
            qubit_1.cphase(qubit_2)

        elif operation["gate"] == Operation.CUSTOM_TWO_QUBIT:
            gate_param = self.extract_gate_param(operation)
            qubit_1.custom_two_qubit_gate(qubit_2, gate_param)

        elif operation["gate"] == Operation.CUSTOM_CONTROLLED:
            gate_param = self.extract_gate_param(operation)
            qubit_1.custom_controlled_gate(qubit_2, gate_param)

    def _process_three_qubit_gate(self, operation: dict):
        self._check_errors(op=operation, len_qids=3, len_computing_host_ids=1)
        q_ids = operation["qids"]
        qubit_1 = self._get_stored_qubit(q_ids[0])
        qubit_2 = self._get_stored_qubit(q_ids[1])
        qubit_3 = self._get_stored_qubit(q_ids[2])
        if operation["gate"] == Operation.CUSTOM_TWO_QUBIT_CONTROLLED:
            gate_param = self.extract_gate_param(operation)
            qubit_1.custom_two_qubit_control_gate(qubit_2, qubit_3, gate_param)

    def _process_classical_ctrl_gates(self, operation: dict):
        """
        Follows the operation command to perform a classical control gate
        on a qubit.

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(
            op=operation, len_qids=1, len_computing_host_ids=1, len_cids=1
        )

        control_bit_id = operation["cids"][0]
        bit = int(self._bits[control_bit_id])

        if bit:
            self._process_single_gates(operation, classical_ctrl_gate=True)

    def _process_send_ent(self, operation: dict):
        """
        Follows the operation command to send EPR pair

        Args:
           operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=2)

        qubit_id = operation["qids"][0]
        receiver_id = operation["computing_host_ids"][1]

        self.send_epr(receiver_id, q_id=qubit_id, await_ack=True)

        epr_qubit = self.get_epr(receiver_id, q_id=qubit_id)
        self._add_new_qubit(epr_qubit, qubit_id, operation["pre_allocated_qubits"])

    def _process_rec_ent(self, operation: dict):
        """
        Follows the operation command to receive EPR pair

        Args:
           operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_qids=1, len_computing_host_ids=2)

        qubit_id = operation["qids"][0]
        receiver_id = operation["computing_host_ids"][1]

        i = 0
        epr_qubit = None

        while i < MAX_WAIT and epr_qubit is None:
            epr_qubit = self.get_epr(receiver_id, q_id=qubit_id)
            i += 1
            time.sleep(0.5)

        self._add_new_qubit(epr_qubit, qubit_id, operation["pre_allocated_qubits"])

    def _process_send_classical(self, operation: dict):
        """
        Follows the operation command to receive a classical bit

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=2, len_cids=1)

        bit_id = operation["cids"][0]

        if bit_id not in self._bits.keys():
            msg = "Bit not present in the computing host"
            self._report_error(msg)

        receiver_id = operation["computing_host_ids"][1]

        self.send_classical(receiver_id, self._bits[bit_id], await_ack=True)

    def _process_rec_classical(self, operation: dict):
        """
        Follows the operation command to receive a classical bit

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=2, len_cids=1)

        sender_id = operation["computing_host_ids"][1]
        msg = self.get_next_classical(sender_id, wait=-1)
        bit = msg.content
        bit_id = operation["cids"][0]

        self._bits[bit_id] = bit

    def _process_measurement(self, operation: dict):
        """
        Follows the operation command to measure a qubit and save the result

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(
            op=operation, len_qids=1, len_computing_host_ids=1, len_cids=1
        )

        qubit_id = operation["qids"][0]
        bit_id = operation["cids"][0]

        qubit = self._get_stored_qubit(qubit_id)

        bit = qubit.measure(non_destructive=False)
        self._bits[bit_id] = bit

        if qubit_id in self._pre_allocated_qubits:
            del self._pre_allocated_qubits[qubit_id]
            self._total_pre_allocated_qubits += 1
        else:
            del self._qubits[qubit_id]
            self._total_qubits -= 1

    def _process_rec_hamilton(self, operation: dict):
        """
        Receives a list of observables from the controller to calculate their expectation values

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=1)

        self._hamiltonian = operation["hamiltonian"]

        self._calculated_exp = False

        return

    def _process_send_exp(self, operation: dict):
        """
        Calculate the expectation value of the qubits and send the results back to the controller

        Args:
            operation (dict): Dictionary of information regarding the operation
        """

        self._check_errors(op=operation, len_computing_host_ids=1)

        indices = []

        for qubit_id in self.qubit_ids:
            indices.append(self.get_qubit_by_id(qubit_id))

        statevector = self.backend.statevector(indices[0])[1]

        self.exp = expectation_value(self._hamiltonian, statevector, self._total_qubits)

        self._calculated_exp = True

        return

    def perform_schedule(self, ticks: int):
        """
        Process the schedule and perform the corresponding operations
        accordingly

        Args:
           ticks (int): Number of times the clock has ticked
        """

        if ticks not in self._schedule:
            self._clock.respond()
            return

        for operation in self._schedule[ticks]:
            if operation["name"] == Constants.PREPARE_QUBITS:
                self._prepare_qubits(operation)

            if operation["name"] == Constants.SINGLE:
                self._process_single_gates(operation)

            if operation["name"] == Constants.TWO_QUBIT:
                self._process_two_qubit_gates(operation)

            if operation['name'] == Constants.THREE_QUBIT:
                self._process_three_qubit_gate(operation)

            if operation["name"] == Constants.CLASSICAL_CTRL_GATE:
                self._process_classical_ctrl_gates(operation)

            if operation["name"] == Constants.SEND_ENT:
                self._process_send_ent(operation)

            if operation["name"] == Constants.REC_ENT:
                self._process_rec_ent(operation)

            if operation["name"] == Constants.SEND_CLASSICAL:
                self._process_send_classical(operation)

            if operation["name"] == Constants.REC_CLASSICAL:
                self._process_rec_classical(operation)

            if operation["name"] == Constants.MEASURE:
                self._process_measurement(operation)

            if operation["name"] == Constants.REC_HAMILTON:
                self._process_rec_hamilton(operation)

            if operation["name"] == Constants.SEND_EXP:
                self._process_send_exp(operation)

        self._clock.respond()

    def send_results(self, result_type: str = "bits"):
        """
        Send results to Controller Host
        """

        # TODO: Check if there is a better implementation
        # Wait for the clock to stop ticking to send the results
        while not self._clock.has_stopped:
            time.sleep(1)

        # Wait until the expectation calculation is finished
        while result_type == "expectation" and not self._calculated_exp:
            time.sleep(0.5)

        if self._error_message:
            msg = {"type": "error", "message": self._error_message}
        else:
            if result_type == "bits":
                msg = {"type": "measurement_result", "val": self.bits}
            elif result_type == "expectation":
                msg = {"type": "expectation_value", "val": np.real(self.exp)}
            else:
                msg = {
                    "type": "unsupported_result_type",
                    "message": "Supported result types are only 'bits' and 'expectation'",
                }

        message = json.dumps({self.host_id: msg})
        self.send_classical(self._controller_host_id, message, await_ack=True)
