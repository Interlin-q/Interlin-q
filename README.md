[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

# Interlin-q

This is a distributed quantum-enabled simulator which imitates the master-slave centralised-control distributed quantum computing system with interconnect communication between the nodes. Using this simulator, one can input any monolithic circuit as well as a distributed quantum computing topology and see the execution of the distributed algorithm happening in real time. The simulator maps the monolithic circuit to a distributed quantum computing achitecture and uses a master-slave relation with a centralized controller communicating to computing nodes in the network. Interlin-q can be used for designing and analysing novel distributed quantum algorithms for various distributed quantum computing architectures.

The method used to accomplish this is based on the following paper:

```
Distributed Quantum Computing and Network Control for Accelerated VQE
Stephen DiAdamo, Marco Ghibaudi, James Cruise (arXiv: 2101.02504)
```

## Setup

To setup Interlin-q, run the below command.

```
pip install -r requirements.txt
```
