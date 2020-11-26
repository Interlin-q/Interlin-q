from utils import OperationNames


class Operation(object):
    """
    Operation object which contains information about the quantum operation or a
    quantum gate which is to be applied to a circuit
    """

    def __init__(self, name, qids=None, cids=None, gate=None, gate_param=None, computing_host_ids=[], pre_allocated_qubits=False):
        """
        Returns the important things for a quantum operation

        Args:
            name (str): Name of the operation
            qids (list): List of qubits IDs associated to the operation. The first ID in this
                list will be the ID of the computing host where the operation is being performed
            cids (list): List of classical bit IDs associated to the operation
            gate (str): Name of the single or the two-qubit gate
            gate_param (int): parameter for rotational gates
            computing_host_ids (list): List of associated ID/IDS of the computing host where
                the operation/gate is being performed. The first computing host in the list
                would be the one where the operation is being performed.
            pre_allocated_qubits (bool): Flag to indicate if this operation is being performed on
                a sepcific pre-allocated qubit (In case of EPR pair generation)
        """

        if name not in OperationNames:
            raise (InputError("Operation is invalid"))
        self._name = name

        self._qids = qids
        self._cids = cids
        self._gate = gate
        self._gate_param = gate_param
        self._computing_host_ids = computing_host_ids
        self._pre_allocated_qubits = pre_allocated_qubits

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
            (int): parameter for rotational gates
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
            'computing_host_ids': self._computing_host_ids
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
