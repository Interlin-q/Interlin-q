default_single_gate_time = 1
default_single_operation_time = 1

DefaultSingleGateTime = {
    "I": default_single_gate_time,
    "X": default_single_gate_time,
    "Y": default_single_gate_time,
    "Z": default_single_gate_time,
    "T": default_single_gate_time,
    "K": default_single_gate_time,
    "H": default_single_gate_time,
    "rx": default_single_gate_time,
    "ry": default_single_gate_time,
    "rz": default_single_gate_time,
    "cnot": default_single_gate_time,
    "cphase": default_single_gate_time,
    "custom_gate": default_single_gate_time,
    "custom_controlled_gate": default_single_gate_time,
    "custom_two_qubit_control_gate": default_single_gate_time,
    "custom_two_qubit_gate": default_single_gate_time
}

DefaultOperationTime = {
    "SINGLE": DefaultSingleGateTime,
    "TWO_QUBIT": default_single_operation_time,
    "SEND_ENT": default_single_operation_time,
    "REC_ENT": default_single_operation_time,
    "SEND_CLASSICAL": default_single_operation_time,
    "REC_CLASSICAL": default_single_operation_time
}
