from typing import List, Tuple

Observable = List[Tuple[str, int]]
HamiltonianTerm = Tuple[int, Observable]
Hamiltonian = List[HamiltonianTerm]
