from qutip import identity, sigmax, sigmay, sigmaz
from qutip import expect

def string_to_qutip_pauli(string):
    if string == 'Identity':
        return identity(2)
    if string == 'PauliX':
        return sigmax()
    if string == 'PauliY':
        return sigmay()
    if string == 'PauliZ':
        return sigmaz()

def expectation_value(terms, matrices, tmp):
    total = 0
    
    for term in terms:
        coefficient, observables = term
        
        needed_matrices = []
        needed_paulis = []
        
        for obs in observables:
            pauli, index = obs
            
            needed_matrices.append(matrices[index])
            needed_paulis.append(string_to_qutip_pauli(pauli))
        
        expectation = expect(needed_paulis, needed_matrices)
        
        total += coefficient * expectation[0][0]
    
    return total