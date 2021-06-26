[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

# Interlin-q

This is a distributed quantum-enabled simulator which imitates the master-slave centralised-control distributed quantum computing system with interconnect communication between the nodes. Using this simulator, one can input any monolithic circuit as well as a distributed quantum computing topology and see the execution of the distributed algorithm happening in real time. The simulator maps the monolithic circuit to a distributed quantum computing achitecture and uses a master-slave relation with a centralized controller communicating to computing nodes in the network. Interlin-q can be used for designing and analysing novel distributed quantum algorithms for various distributed quantum computing architectures.

The method used to accomplish this is based on the following paper:

```
Distributed Quantum Computing and Network Control for Accelerated VQE
Stephen DiAdamo, Marco Ghibaudi, James Cruise (arXiv: 2101.02504)
```

The simulated architecture can be seen in the image below:

![Simulated Architecture](images/simulated_architechture.png)

## Setup, tests and documentation

See https://interlin-q.github.io/Interlin-q for documentation. To setup Interlin-q, run the below command.

```
pip install -r requirements.txt
```

To run tests, run the below command.

```
nose2
```

## Quick Start Guide

### Quick Example

A basic template of a distributed CNOT gate between two different computing hosts is shown in the file ```examples/template.py```, where the control qubit in first computing host is set in |1> state and the target qubit in the second computing host is set in |0> state.

```
def create_circuit(q_map):
    layers = []
    computing_host_ids = list(q_map.keys())

    # Prepare the qubits on both computing hosts
    ops = []
    for host_id in computing_host_ids:
        op = Operation(
            name=Constants.PREPARE_QUBITS,
            qids=q_map[host_id],
            computing_host_ids=[host_id])
        ops.append(op)
    layers.append(Layer(ops))

    # Circuit input should be added below
    # Put qubit "q_0_0" in |1> state
    op = Operation(
        name=Constants.SINGLE,
        qids=[q_map[computing_host_ids[0]][0]],
        gate=Operation.X,
        computing_host_ids=[computing_host_ids[0]])
    ops.append(op)
    layers.append(Layer(ops))

    # Apply cnot gate from "q_0_0" to "q_1_0"
    control_qubit_id = q_map[computing_host_ids[0]][0]
    target_qubit_id = q_map[computing_host_ids[1]][0]

    op = Operation(
        name=Constants.TWO_QUBIT,
        qids=[control_qubit_id, target_qubit_id],
        gate=Operation.CNOT,
        computing_host_ids=computing_host_ids)
    layers.append(Layer([op]))

    # Measure the qubits
    ops = []
    for host_id in computing_host_ids:
        op = Operation(
            name=Constants.MEASURE,
            qids=[q_map[host_id][0]],
            cids=[q_map[host_id][0]],
            computing_host_ids=[host_id])
        ops.append(op)
    layers.append(Layer(ops))

    circuit = Circuit(q_map, layers)
    return circuit

def controller_host_protocol(host, q_map):
    """
    Protocol for the controller host
    """
    circuit = create_circuit(q_map)
    host.generate_and_send_schedules(circuit)
    host.receive_results()

    results = host.results
    computing_host_ids = host.computing_host_ids

    print('Final results: \n')
    for computing_host_id in computing_host_ids:
        bits = results[computing_host_id]['bits']
        for bit_id, bit in bits.items():
            print("{0}: {1}".format(bit_id, bit))

def computing_host_protocol(host):
    """
    Protocol for the computing hosts
    """
    host.receive_schedule()
    host.send_results()

def main():
    # initialize network
    network = Network.get_instance()
    network.start()

    clock = Clock()
    controller_host = ControllerHost(host_id="host_1", clock=clock)

    # Here the number of computing hosts and number of qubits per computing hosts
    # can be customised
    computing_hosts, q_map = controller_host.create_distributed_network(
        num_computing_hosts=2,
        num_qubits_per_host=2)
    controller_host.start()

    network.add_host(controller_host)
    for host in computing_hosts:
        network.add_host(host)

    print('starting...')
    t = controller_host.run_protocol(controller_host_protocol, (q_map,))
    threads = [t]
    for host in computing_hosts:
        t = host.run_protocol(computing_host_protocol)
        threads.append(t)

    for thread in threads:
        thread.join()
    network.stop(True)
    exit()

if __name__ == '__main__':
    main()
```

In the template, the monolothic circuit can be added in the `create_circuit` function, which will automatically be distributed by the controller host and performed by the computing hosts. The operations needed to perform the monolithic circuit should be added layer by layer. The specific topology required to perform the circuit can be customised by changing the number of computing hosts required to perform the circuit and as well as changing the number of qubits required per computing hosts.

### Distributed Quantum Phase Estimation Tutorial

A tutorial of Distributed Quantum Phase Estimation algorithm can be found [here](examples/QPE/distributed_quantum_phase_estimation_notebook.ipynb).

## Contributing

We welcome contributors. Feel free to open an issue on this repository or add a pull request to submit your patch/contribution. Adding test cases for any contributions is a requirement for any pull request to be merged.

## Citing
```
@article{parekh2021quantum,
  title={Quantum Algorithms and Simulation for Parallel and Distributed Quantum Computing},
  author={Parekh, Rhea and Ricciardi, Andrea and Darwish, Ahmed and DiAdamo, Stephen},
  journal={arXiv preprint arXiv:2106.06841},
  year={2021}
}
```
