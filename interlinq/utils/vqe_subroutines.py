import numpy as np


def string_to_qutip_pauli(string):
    if string == "Identity":
        return np.eye(2)
    if string == "PauliX":
        return np.array([[0.0, 1.0], [1.0, 0.0]])
    if string == "PauliY":
        return np.array([[0.0, -1j], [1j, 0.0]])
    if string == "PauliZ":
        return np.array([[1.0, 0.0], [0.0, -1.0]])


def tensor_product_matrix_list(matrix_list):
    if len(matrix_list) == 1:
        tmp = matrix_list[0]
    else:
        tmp = np.kron(matrix_list[0], matrix_list[1])

        for i in range(2, len(matrix_list)):
            tmp = np.kron(tmp, matrix_list[i])

    return tmp


def expectation_value(terms, vector, number_of_qubits):
    total = 0

    for term in terms:
        coefficient, observables = term

        obs_tensor_prod = []

        for _ in range(number_of_qubits):
            obs_tensor_prod.append(np.eye(2))

        for obs in observables:
            pauli, index = obs

            obs_tensor_prod[index] = string_to_qutip_pauli(pauli)

        obs_tensor_prod = tensor_product_matrix_list(obs_tensor_prod)

        total += coefficient * np.vdot(vector, obs_tensor_prod @ vector)

    return total
