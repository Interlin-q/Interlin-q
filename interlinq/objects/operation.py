from interlinq.utils import Constants


class Operation(object):
    """
    Operation object which contains information about the quantum operation or a
    quantum gate which is to be applied to a circuit
    """

    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"
    CNOT = "cnot"
    CPHASE = "cphase"
    T = "T"
    H = "H"
    K = "K"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    CUSTOM = "custom_gate"
    CUSTOM_TWO_QUBIT = "custom_two_qubit_gate"
    CUSTOM_CONTROLLED = "custom_controlled_gate"
    MEASURE = "measure"

    def __init__(self, name, qids=None, cids=None, gate=None, gate_param=None, computing_host_ids=[],
                 pre_allocated_qubits=False):
        """
        Returns the important things for a quantum operation

        Args:
            name (str): Name of the operation
            qids (list): List of qubits IDs associated to the operation. The first ID in this
                list will be the ID of the computing host where the operation is being performed
            cids (list): List of classical bit IDs associated to the operation
            gate (str): Name of the single or the two-qubit gate
            gate_param (list): parameter for rotational gates
            computing_host_ids (list): List of associated ID/IDS of the computing host where
                the operation/gate is being performed. The first computing host in the list
                would be the one where the operation is being performed.
            pre_allocated_qubits (bool): Flag to indicate if this operation is being performed on
                a specific pre-allocated qubit (In case of EPR pair generation)
        """

        if name not in Constants.OPERATION_NAMES:
            raise (InputError("Operation is invalid"))
        self._name = name

        self._qids = qids
        self._cids = cids
        self._gate = gate
        self._gate_param = gate_param
        self._computing_host_ids = computing_host_ids
        self._pre_allocated_qubits = pre_allocated_qubits

    def __str__(self):
        return self.name

    @property
    def name(self):
        """
        Get the *name* of the operation

        Returns:
            (str): Name of the operation
        """
        return self._name

    @property
    def qids(self):
        """
        Get the *qid* or the IDs of the qubits associated to the operation

        Returns:
            (list): List of qubit IDs
        """
        return self._qids

    @property
    def gate(self):
        """
        Get the *gate* associated to the operation, if any

        Returns:
            (str): Name of the single or the two-qubit gate
        """

        return self._gate

    @property
    def gate_param(self):
        """
        Get the *gate_param* associated to the operation, if any

        Returns:
            (list): parameter for rotational gates
        """

        return self._gate_param

    @property
    def computing_host_ids(self):
        """
        Get the *computing_host_ids* associated to the operation

        Returns:
            (list): List of associated ID/IDS of the computing host where the operation/gate
                is being performed. The first computing host in the list would be the one
                where the operation is being performed.
        """

        return self._computing_host_ids

    def get_control_qubit(self):
        """
        Get the ID of the control qubit, in case of TWO_QUBIT operations

        Returns:
            (str): ID of the control qubit associated to the two qubit operation
        """

        if self._name == Constants.TWO_QUBIT:
            return self._qids[0]
        raise ValueError("The operation name has to be TWO_QUBIT to get the control qubit ID")

    def get_control_host(self):
        """
        Get the ID of the host with the control qubit, in case of TWO_QUBIT operations

        Returns:
            (str): ID of the control qubit associated to the two qubit operation
        """

        if self._name == Constants.TWO_QUBIT:
            return self._computing_host_ids[0]
        raise ValueError("The operation name has to be TWO_QUBIT to get the control host")

    def get_target_qubit(self):
        """
        Get the ID of the target qubit, in case of TWO_QUBIT operations

        Returns:
            (str): ID of the target qubit associated to the two qubit operation
        """

        if self._name == Constants.TWO_QUBIT:
            return self._qids[1]
        raise ValueError("The operation name has to be TWO_QUBIT to get the target qubit ID")

    def get_target_host(self):
        """
        Get the ID of the host with the target qubit, in case of TWO_QUBIT operations

        Returns:
            (str): ID of the target qubit associated to the two qubit operation
        """

        if self._name == Constants.TWO_QUBIT:
            if len(self._computing_host_ids) == 2:
                return self._computing_host_ids[1]
            return self._computing_host_ids[0]
        raise ValueError("The operation name has to be TWO_QUBIT to get the target host")

    def is_control_gate_over_two_hosts(self):
        """
        Check if the operation is a control gate over two different computing hosts

        Returns:
            (bool): Bool value, which is true if the operation is a control gate over two
                different computing hosts
        """
        if self._name == Constants.TWO_QUBIT and len(self._computing_host_ids) == 2:
            return True
        return False

    def get_dict(self):
        """
        Return the Operation object in a dictionary format
        """

        operation_info = {
            'name': self._name,
            'qids': self._qids,
            'cids': self._cids,
            'gate': self._gate,
            'gate_param': self._gate_param,
            'computing_host_ids': self._computing_host_ids,
            'pre_allocated_qubits': self._pre_allocated_qubits
        }
        return operation_info


class InputError(Exception):
    """
    Exception raised for errors in the input.
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
