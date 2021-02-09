from interlinq.utils import Constants
from . import Operation


class Qubit(object):
    """
    Qubit object which stores the operations performed on it
    """

    def __init__(self, computing_host_id, q_id, prepare_qubit=True):
        """
        Returns the important things for a qubit object in a quantum circuit

        Args:
            computing_host_id (str): ID of the computing host where the qubit is
               located
            q_id (str): ID of the qubit
        """

        self._computing_host_id = computing_host_id
        self._q_id = q_id
        self._operations = {}
        self._current_layer = 0

        if prepare_qubit:
            self.prepare()

    @property
    def q_id(self):
        """
        Get the ID of the qubit
        Returns:
            (str): ID of the qubit
        """
        return self._q_id

    @property
    def computing_host_id(self):
        """
        Get the *operations* in the layer
        Returns:
            (str): ID of the computing host where the qubit is located
        """
        return self._computing_host_id

    @property
    def operations(self):
        """
        Get the *operations* in the layer
        Returns:
            (str): List of Operation objects, which contains information about the
            operation to be performed on the quantum circuit
        """    
        return self._operations

    @property
    def current_layer(self):
        """
        Get the *operations* in the layer
        Returns:
            (str): List of Operation objects, which contains information about the
        """
        return self._current_layer

    def _update_operations(self, op):
        """
        """
        self._operations[self._current_layer] = op

    def update_layer(self, layer):
        """
        """
        self._current_layer = layer

    def prepare(self):
        op = Operation(
            name=Constants.PREPARE_QUBITS,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id])

        self._update_operations(op)

    def single(self, gate, gate_param=None):
        op = Operation(
            name=Constants.SINGLE,
            qids=[self.q_id],
            gate=gate,
            gate_param=gate_param,
            computing_host_ids=[self.computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def two_qubit(self, gate, target_qubit, gate_param=None):
        if target_qubit.computing_host_id == self._computing_host_id:
            op = Operation(
                name=Constants.TWO_QUBIT,
                qids=[self.q_id, target_qubit.q_id],
                gate=gate,
                gate_param=gate_param,
                computing_host_ids=[self.computing_host_id])
        else:
            op = Operation(
                name=Constants.TWO_QUBIT,
                qids=[self.q_id, target_qubit.q_id],
                gate=gate,
                gate_param=gate_param,
                computing_host_ids=[
                    self.computing_host_id,
                    target_qubit.computing_host_id])

        if target_qubit.current_layer + 1 > self.current_layer + 1:
            target_qubit.update_layer(target_qubit.current_layer + 1)
            self.update_layer(target_qubit.current_layer + 1)
        else:
            target_qubit.update_layer(self.current_layer + 1)
            self.update_layer(self.current_layer + 1)

        self._update_operations(op)

    def classical_ctrl_gate(self, gate, cid, gate_param=None):
        op = Operation(
            name=Constants.CLASSICAL_CTRL_GATE,
            qids=[self._q_id],
            cids=[cid],
            gate=gate,
            gate_param=gate_param,
            computing_host_ids=[self._computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def send_ent(self, receiver_id, pre_allocated):
        op = Operation(
            name=Constants.SEND_ENT,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id, receiver_id],
            pre_allocated=pre_allocated)

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def rec_ent(self, sender_id, pre_allocated):
        op = Operation(
            name=Constants.REC_ENT,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id, sender_id],
            pre_allocated=pre_allocated)

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def send_classical(self, bit_id, receiver):
        op = Operation(
            name=Constants.SEND_CLASSICAL,
            cids=[bit_id],
            computing_host_ids=[self.computing_host_id, receiver.computing_host_id])

        if receiver.current_layer + 1 > self.current_layer + 1:
            receiver.update_layer(receiver.current_layer + 1)
            self.update_layer(receiver.current_layer + 1)
        else:
            receiver_qubit.update_layer(self.current_layer + 1)
            self.update_layer(self.current_layer + 1)

        self._update_operations(op)

    def rec_classical(self, bit_id, sender):
        op = Operation(
            name=Constants.REC_CLASSICAL,
            cids=[bit_id],
            computing_host_ids=[self.computing_host_id, sender.computing_host_id])

        if sender_qubit.current_layer + 1 > self.current_layer + 1:
            sender.update_layer(sender.current_layer + 1)
            self.update_layer(sender_qubit.current_layer + 1)
        else:
            senderqqqq.update_layer(self.current_layer + 1)
            self.update_layer(self.current_layer + 1)

        self._update_operations(op)

    def measure(self, bit_id):
        op = Operation(
            name=Constants.MEASURE,
            qids=[self.q_id],
            cids=[bit_id],
            computing_host_ids=[self.computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)
