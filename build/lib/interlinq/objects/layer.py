class Layer(object):
    """
    Layer object which is a collection of operations to be applied on the qubits
    in the system.
    """

    def __init__(self, operations=[]):
        """
        Returns the important things for a layer in a quantum circuit

        Args:
            operations (list): List of Operation objects, which contains information
               about the operation to be performed on the quantum circuit
        """

        self._operations = operations

    def __str__(self):
        layer = ''
        for o in self._operations:
            layer += f'-{o}-\n'
        return layer

    @property
    def operations(self):
        """
        Get the *operations* in the layer 
        Returns:
            (list): List of Operation objects, which contains information about the
            operation to be performed on the quantum circuit
        """
        return self._operations

    def add_operation(self, operation):
        """
        Add a operation to the layer
        Args:
            operation (Operation): Information about the operation to be added in the layer
        """

        self._operations.append(operation)

    def add_operations(self, operations):
        """
        Add multiple operations to the layer
        Args:
            operations (list): List of Operation objects
        """

        for operation in operations:
            self._operations.append(operation)

    def control_gate_present(self):
        """
        Check if a control gate is present in the layer between two different
        computing hosts

        Args:
            operations (list): List of Operation objects
        Returns:
            (bool): True if control gate is present between two different computing
                hosts
        """

        control_gate_present = False

        for operation in self._operations:
            if operation.name == "TWO_QUBIT" and len(operation.computing_host_ids) == 2:
                control_gate_present = True
        return control_gate_present

    def remove_operation(self, index):
        """
        Remove an operation from the layer
        Args:
            index (int): Index of the operation to be removed
            operation (Operation): Information about the operation to be removed
        """

        self._operations.pop(index)
