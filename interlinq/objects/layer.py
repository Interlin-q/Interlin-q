from typing import List, Optional
from .operation import Operation


class Layer(object):
    """
    Layer object which is a collection of operations to be applied on the qubits in the system.
    """

    def __init__(self, operations: Optional[List[Operation]] = None):
        """
        Returns the important things for a layer in a quantum circuit

        Args:
            operations (list): List of Operation objects, which contains information
               about the operation to be performed on the quantum circuit
        """

        self._operations = operations if operations is not None else []

    def __str__(self):
        layer = ""

        for o in self._operations[:-1]:
            layer += f"-{o}-|\n"

        layer += f"-{self._operations[:-1]}-|"
        return layer

    @property
    def operations(self):
        """
        Get the *operations* in the layer

        Returns:
            (list): List of Operation objects, which contains information about the operation to
                    be performed on the quantum circuit.
        """
        return self._operations

    @property
    def depth(self):
        # todo
        return 0

    def __len__(self):
        return self.depth

    def add_operation(self, operation: Operation):
        """
        Add a operation to the layer
        Args:
            operation (Operation): Information about the operation to be added in the layer
        """

        self._operations.append(operation)

    def add_operations(self, operations: List[Operation]):
        """
        Add multiple operations to the layer
        Args:
            operations (list): List of Operation objects
        """

        self._operations.extend(operations)

    def control_gate_present(self):
        """
        Check if a control gate is present in the layer between two different
        computing hosts

        Returns:
            (bool): True if control gate is present between two different computing
                hosts
        """

        control_gate_present = False

        for operation in self._operations:
            if operation.name == "TWO_QUBIT" and len(operation.computing_host_ids) == 2:
                control_gate_present = True
        return control_gate_present

    def remove_operation(self, index: int):
        """
        Remove an operation from the layer.

        Args:
            index (int): Index of the operation to be removed
        """

        self._operations.pop(index)
