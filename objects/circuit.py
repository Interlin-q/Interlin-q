class Circuit(object):
    """
    Circuit object which contains information about a quantum circuit.
    """

    def __init__(self, q_map, layers=[]):
        """
        Returns the important things for a quantum circuit

        Args:
            q_map (dict): A mapping of the qubits required for the circuit to the
               computing host ID where the qubit is located
            layers (list): List of Layer objects, where each layer contains a
               collection of operations to be applied on the qubits in the system
        """

        self._q_map = q_map
        self._layers = layers

    @property
    def q_map(self):
        """
        Get the *q_map* of the circuit
        Returns:
            (dict): A mapping of the qubits required for the circuit to the
                computing host ID where the qubit is located
        """
        return self._q_map

    @property
    def layers(self):
        """
        Get the *layers* of the circuit
        Returns:
            (list): List of Layer objects, where each layer contains a collection
                of gates to be applied on the qubits in the system
        """
        return self._layers

    def total_qubits(self):
        """
        Get the total number of qubits in the circuit
        Returns:
            (int): total number of qubits in circuit
        """

        return len(self._q_map)

    def add_new_qubit(self, qubit_info):
        """
        Add a new qubit to the circuit
        Args:
            qubit_info (dict): Map of new qubit ID to the computing host ID
        """

        if list(qubit_info.keys())[0] in self._q_map:
            raise ValueError("Qubit already added")
        self._q_map.update(qubit_info)

    def add_layer_to_circuit(self, layer):
        """
        Add a new Layer object to the circuit

        Args:
            layer (object): List of operations to be applied to the system
        """
        
        self._layers.append(layer)
