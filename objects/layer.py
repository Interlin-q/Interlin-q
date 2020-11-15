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
            operation (object): Information about the operation to be added in the layer
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
