from .layer import Layer


class Circuit(object):
    """
    Circuit object which contains information about a quantum circuit.
    """

    def __init__(self, q_map, layers=[], qubits=[]):
        """
        Returns the important things for a quantum circuit

        Args:
            q_map (dict): A mapping of the computing hosts IDS to the list of qubits
                required for the circuit in that host
            layers (list): List of Layer objects, where each layer contains a
                collection of operations to be applied on the qubits in the system
            qubits (list): List of Qubit objects, where each qubit object stores
                the list of operations applied on it
        """

        self._q_map = q_map
        self._layers = layers
        self._qubits = qubits
        self._width = 0

        if not self._layers:
            if self._qubits:
                self.create_layers(self._qubits)

    def __str__(self):
        circuit = ''
        for layer in self._layers:
            circuit += str(layer) + '\n'
        return circuit

    @property
    def q_map(self):
        """
        Get the *q_map* of the circuit
        Returns:
            (dict): A mapping of the computing hosts IDS to the list of qubits
                required for the circuit in that host
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

    @property
    def qubits(self):
        """
        Get the *qubits* of the circuit
        Returns:
            (list): List of Qubit objects, where each qubit object stores the
                list of operations applied on it
        """
        return self._qubits

    def add_new_qubit(self, qubit_info):
        """
        Add a new qubit to the circuit
        Args:
            qubit_info (dict): A mapping of the computing hosts ID to the list of new
                qubits required for the circuit in that host
        """

        computing_host_id = list(qubit_info.keys())[0]

        if type(qubit_info[computing_host_id]) is not list:
            raise ValueError("Qubits for a computing host should be provided as a list")

        if computing_host_id not in self._q_map:
            self._q_map.update(qubit_info)
        else:
            qubits_list = qubit_info[computing_host_id]

            for qubit in qubits_list:
                if qubit in self._q_map[computing_host_id]:
                    raise ValueError("Qubit already added")
                self._q_map[computing_host_id].append(qubit)

    def add_layer_to_circuit(self, layer):
        """
        Add a new Layer object to the circuit

        Args:
            layer (Layer): List of operations to be applied to the system
        """

        self._layers.append(layer)

    def create_layers(self, qubits):
        """
        Create layers for the circuit from the qubits provided
        """

        layers = []
        ops = True
        layer_count = 0

        while ops:
            ops = []
            for qubit in qubits:
                if layer_count in list(qubit.operations.keys()):
                    ops.append(qubit.operations[layer_count])

            layer_count += 1
            if ops:
                layers.append(Layer(ops))

        self._layers = layers

    def insert_layer(self, index, layer):
        """
        Insert a new layer object at a particular index in the circuit

        Args:
            layer (Layer): new layer object to be inserted
            index (int): Index at which the new layer should be inserted at
        """
        if len(layer.operations) > self._width:
            self._width = len(layer.operations)
        self._layers.insert(index, layer)

    def total_qubits(self):
        """
        Get the total number of qubits in the circuit
        Returns:
            (int): total number of qubits in circuit
        """

        total_qubits = 0

        for computing_host_id in list(self._q_map.keys()):
            total_qubits += len(self._q_map[computing_host_id])

        return total_qubits

    def update_layer(self, index, layer):
        """
        Update a layer object at a particular index with a new value

        Args:
            layer (Layer): layer object to be updated
            index (int): Index at which the new layer should be updated
        """

        self._layers[index] = layer

    def update_qubits(self, qubits):
        """
        Update qubits in the circuit

        Args:
            qubits (list): List of Qubit objects, where each qubit object stores
                the list of operations applied on it
        """
        self._qubits = qubits

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
                        for index, gate in enumerate(control_gate_info[layer_index - 1]):
                            if gate['computing_hosts'] == computing_hosts:
                                if gate['control_qubit'] == control_qubit:
                                    operations = gate['operations']
                                    del control_gate_info[layer_index - 1][index]
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
