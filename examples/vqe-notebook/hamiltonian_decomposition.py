import pennylane as qml
from pennylane import qchem

def decompose(name, geometry, charge, multiplicity, basis_set):
    decomp, qubit_num = qchem.molecular_hamiltonian(
        name,
        geometry,
        charge=charge,
        mult=multiplicity,
        basis=basis_set,
        active_electrons=2,
        active_orbitals=2,
        mapping='jordan_wigner'
        )
    
    coefficients, observables = decomp.terms
    observables = [[group for group in zip(term.name, term.wires)]
        for term in observables
    ]
    
    return observables, qubit_num