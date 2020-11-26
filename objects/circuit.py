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

    def insert_layer(self, index, layer):
        """
        Insert a new layer object at a particular index in the circuit

        Args:
            layer (object): new layer object to be inserted
            index (int): Index at which the new layer should be inserted at
        """

        self._layers.insert(index, layer)

    def update_layer(self, index, layer):
        """
        Update a layer object at a particular index with a new value

        Args:
            layer (object): layer object to be updated
            index (int): Index at which the new layer should be updated
        """

        self._layers[index] = layer

    def computing_host_map(self):
        """
        Return a map of computing hosts to all the qubits required from that
        computing host for the circuit.

        Returns:
            (dict): A mapping of the computing host ID to the qubits required
                from that computing host in the circuit
        """

        computing_host_map = {}
        for key, value in self._q_map.items():
            if value not in computing_host_map:
                computing_host_map[value] = [key]
            else:
                computing_host_map[value].append(key)

        return computing_host_map

    def control_gate_info(self):
        """
        Get information about the control gates between two different computing
        hosts in the circuit. This information includes the operation index in the
        layer, the associated computing host IDs, control qubit for the control gate.

        Returns:
            (list): Layer-wise list of control gate information in the circuit
        """

        control_gate_info = []

        for layer_index, layer in enumerate(self._layers[::-1]):
            control_gates = []
            for op_index, op in enumerate(layer.operations):
                computing_hosts = op.computing_host_ids

                if op.is_control_gate_over_two_hosts():
                    control_qubit = op.get_control_qubit()

                    operations = []
                    if layer_index != 0:
                        for index, gate in enumerate(control_gate_info[layer_index-1]):
                            if gate['computing_hosts'] == computing_hosts:
                                if gate['control_qubit'] == control_qubit:
                                    operations = gate['operations']
                                    del control_gate_info[layer_index-1][index]
                    operations.append(op)

                    control_gate = {
                        'op_index': op_index,
                        'computing_hosts': computing_hosts,
                        'control_qubit': control_qubit,
                        'operations': operations
                    }
                    control_gates.append(control_gate)
            control_gate_info.append(control_gates)

        return control_gate_info[::-1]
