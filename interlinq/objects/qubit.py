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
            prepare_qubit (bool): Boolean field which indicates if the qubit should
               be prepared when initiated. This should be set to False for qubits
               which are created by sending/receiver EPR pairs
        """

        self._computing_host_id = computing_host_id
        self._q_id = q_id
        self._operations = {}
        self._current_layer = 0

        if prepare_qubit:
            # Prepare the qubits when initiated
            # prepare_qubits should be False when initiating a qubit with the
            # operations 'send_epr' or 'receive_epr'
            self._prepare()

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
        Get the *computing_host_id* linked to the qubit
        Returns:
            (str): ID of the computing host where the qubit is located
        """
        return self._computing_host_id

    @property
    def operations(self):
        """
        Get the *operations* in the layer
        Returns:
            (str): List of Operation objects, which contains information about
            the operation to be performed on the quantum circuit
        """    
        return self._operations

    @property
    def current_layer(self):
        """
        Get the *current_layer*, which is the layer of the last operation on the
        qubit
        Returns:
            (str): List of Operation objects, which contains information about the
        """
        return self._current_layer

    def _update_operations(self, op):
        """
        Update the list of operations performed on the qubit with the latest
        operation

        Args:
            op (Operation): Last operation performed on the qubit
        """
        self._operations[self._current_layer] = op

    def _prepare(self):
        """
        Operation to prepare the qubit
        """
        op = Operation(
            name=Constants.PREPARE_QUBITS,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id])

        self._update_operations(op)

    def update_layer(self, layer):
        """
        Update the list of operations performed on the qubit with th

        Args:
            op (Operation): Last operation performed on the qubit
        """
        self._current_layer = layer

    def single(self, gate, gate_param=None):
        """
        Operation to apply a single gate to the qubit

        Args:
            gate (str): Name of the single qubit gate to be applied
            gate_param (list): Parameter for rotational gates
        """
        op = Operation(
            name=Constants.SINGLE,
            qids=[self.q_id],
            gate=gate,
            gate_param=gate_param,
            computing_host_ids=[self.computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def two_qubit(self, gate, target_qubit, gate_param=None):
        """
        Operation to apply a two qubit gate to the qubit

        Args:
            gate (str): Name of the single qubit gate to be applied
            target_qubit (Qubit): The other qubit on which the qubit gate is
               applied on. In case on control gates, this is the target qubit
            gate_param (list): Parameter for rotational gates
        """

        computing_host_ids = [self.computing_host_id]
        if target_qubit.computing_host_id != self.computing_host_id:
            computing_host_ids.append(target_qubit.computing_host_id)

        op = Operation(
            name=Constants.TWO_QUBIT,
            qids=[self.q_id, target_qubit.q_id],
            gate=gate,
            gate_param=gate_param,
            computing_host_ids=computing_host_ids)

        if target_qubit.current_layer + 1 > self.current_layer + 1:
            target_qubit.update_layer(target_qubit.current_layer + 1)
            self.update_layer(target_qubit.current_layer + 1)
        else:
            target_qubit.update_layer(self.current_layer + 1)
            self.update_layer(self.current_layer + 1)

        self._update_operations(op)

    def classical_ctrl_gate(self, gate, bit_id, gate_param=None):
        """
        Operation to apply a classical control gate to the qubit

        Args:
            gate (str): Name of the single qubit gate to be applied
            bit_id (str): ID of the bit which controls if the gate should
               be applied
            gate_param (list): Parameter for rotational gates
        """
        op = Operation(
            name=Constants.CLASSICAL_CTRL_GATE,
            qids=[self._q_id],
            cids=[bit_id],
            gate=gate,
            gate_param=gate_param,
            computing_host_ids=[self.computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def send_ent(self, receiver_id, pre_allocated=True):
        """
        Operation to send an EPR pair

        Args:
            receiver_id (str): ID of the computing host which receives
                the EPR pair
            pre_allocated (bool): Boolean value which determines if the qubit
                is pre_allocated or not
        """
        op = Operation(
            name=Constants.SEND_ENT,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id, receiver_id],
            pre_allocated=pre_allocated)

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def rec_ent(self, sender_id, pre_allocated=True):
        """
        Operation to receive an EPR pair

        Args:
            sender_id (str): ID of the computing host which sends the
                EPR pair
            pre_allocated (bool): Boolean value which determines if the qubit
                is pre_allocated or not
        """
        op = Operation(
            name=Constants.REC_ENT,
            qids=[self._q_id],
            computing_host_ids=[self.computing_host_id, sender_id],
            pre_allocated=pre_allocated)

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)

    def send_classical(self, bit_id, receiver):
        """
        Operation to send a classical bit

        Args:
            bit_id (str): ID of the bit which has to be sent
            receiver (Qubit): Qubit which receives the classical bit
        """
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
        """
        Operation to receive a classical bit

        Args:
            bit_id (str): ID of the bit which has to be sent
            sender (Qubit): Qubit which sends the classical bit
        """
        op = Operation(
            name=Constants.REC_CLASSICAL,
            cids=[bit_id],
            computing_host_ids=[self.computing_host_id, sender.computing_host_id])

        if sender_qubit.current_layer + 1 > self.current_layer + 1:
            sender.update_layer(sender.current_layer + 1)
            self.update_layer(sender_qubit.current_layer + 1)
        else:
            sender.update_layer(self.current_layer + 1)
            self.update_layer(self.current_layer + 1)

        self._update_operations(op)

    def measure(self, bit_id):
        """
        Operation to measure the qubit

        Args:
            bit_id (str): ID of the bit where the result of the measurement
                has to be stored
        """
        op = Operation(
            name=Constants.MEASURE,
            qids=[self.q_id],
            cids=[bit_id],
            computing_host_ids=[self.computing_host_id])

        self.update_layer(self.current_layer + 1)
        self._update_operations(op)
