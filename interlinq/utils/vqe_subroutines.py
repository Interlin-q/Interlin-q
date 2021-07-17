from qutip import identity, sigmax, sigmay, sigmaz
from qutip import tensor

import numpy as np


def string_to_qutip_pauli(string):
    if string == 'Identity':
        return identity(2)
    if string == 'PauliX':
        return sigmax()
    if string == 'PauliY':
        return sigmay()
    if string == 'PauliZ':
        return sigmaz()


def expectation_value(terms, vector, number_of_qubits):
    total = 0

    for term in terms:
        coefficient, observables = term

        obs_tensor_prod = []

        for _ in range(number_of_qubits):
            obs_tensor_prod.append(identity(2))

        for obs in observables:
            pauli, index = obs

            obs_tensor_prod[index] = string_to_qutip_pauli(pauli)

        obs_tensor_prod = tensor(obs_tensor_prod)

        total += coefficient * np.vdot(vector, obs_tensor_prod @ vector)

    return total
