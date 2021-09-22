class Constants:

    OPERATION_NAMES = [
        "PREPARE_QUBITS",
        "SINGLE",
        "TWO_QUBIT",
        "THREE_QUBIT"
        "CLASSICAL_CTRL_GATE",
        "REC_ENT",
        "SEND_ENT",
        "SEND_CLASSICAL",
        "REC_CLASSICAL",
        "MEASURE",
        "REC_HAMILTON",
        "SEND_EXP"
    ]

    PREPARE_QUBITS = "PREPARE_QUBITS"
    SINGLE = "SINGLE"
    TWO_QUBIT = "TWO_QUBIT"
    THREE_QUBIT = "THREE_QUBIT"
    CLASSICAL_CTRL_GATE = "CLASSICAL_CTRL_GATE"

    # Entanglement Operations
    REC_ENT = "REC_ENT"
    SEND_ENT = "SEND_ENT"
    
    # Classical Communication
    SEND_CLASSICAL = "SEND_CLASSICAL"
    REC_CLASSICAL = "REC_CLASSICAL"

    # VQE-related Operations
    REC_HAMILTON = "REC_HAMILTON"
    SEND_EXP = "SEND_EXP"
    
    MEASURE = "MEASURE"

    DISTRIBUTED_CONTROL_CIRCUIT_LEN = 8

    DEFAULT_SINGLE_GATE_TIME = 1
    DEFAULT_SINGLE_OPERATION_TIME = 1
