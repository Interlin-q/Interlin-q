from qunetsim.components import Host, Network
from qunetsim.objects import Qubit, Logger
from qunetsim.backends import EQSNBackend
from eqsn import EQSN
import numpy as np

Logger.DISABLED = True


def protocol_alice(host, bob_id, backend):
    # Here we write the protocol code for a host.
    epr_id, ack_arrived = host.send_epr(bob_id, await_ack=True)
    if not ack_arrived:
        # Bob didn't receive EPR pair and no ACK received
        raise ValueError('EPR pair not properly established')

    # Receiver got the EPR pair and ACK came back
    # safe to use the EPR pair.
    print('\nAlice received an EPR pair')
    epr_alice = host.get_epr(bob_id, q_id=epr_id)

    # Set up a qubit for the host
    q_alice = Qubit(host)

    # If Alice starts from |1> then uncomment the below line
    # Otherwise Alice startes from |0>
    #q_alice.X()
    #print("Alice starts with qubit |1>")
    print("Alice starts with qubit |0>")

    # Wait for measurement results from Bob
    epr_bob_measurement = host.get_classical(bob_id, wait=-1).pop(0)

    if int(epr_bob_measurement._content) == 1:
        epr_alice.X()

    # Our controlled rotational gate will go here
    # In this case, we apply a Control-H gate. This gate can be customised using
    # custom_controlled_gate function
    #epr_alice.cnot(q_alice)
    h_gate = (1 / 2.0) ** 0.5 * np.array([[1, 1], [1, -1]])
    epr_alice.custom_controlled_gate(q_alice, h_gate)

    epr_alice.H()
    epr_alice_measurement = epr_alice.measure()

    # Send measurement results to Bob
    host.send_classical(bob_id, ("%d" % epr_alice_measurement), await_ack=True)
    print(dir(q_alice))

    print("\nResult of Measurement of Alice's qubit: ", q_alice.measure())
 

def protocol_bob(host, alice_id):
    # Here we write the protocol code for another host.
    epr_bob = host.get_epr(alice_id, wait=5)
    if epr_bob is None:
        # Bob didn't receive EPR pair and no ACK received
        raise ValueError('EPR pair not properly established')

    print('\nBob received an EPR pair')

    q_bob = Qubit(host)
    # If Bob starts form |0> then comment the below line.
    # Otherwise Bob startes from |1>
    q_bob.X()
    print("Bob starts with qubit |1>")
    #print("Bob starts with qubit |0>")

    q_bob.cnot(epr_bob)
    epr_bob_measurement = epr_bob.measure()

    # Send measurement results to Alice
    host.send_classical(alice_id, ("%d" % epr_bob_measurement), await_ack=True)

    # Wait for measurement results from Alice
    epr_alice_measurement = host.get_classical(alice_id, wait=-1).pop(0)

    if int(epr_alice_measurement._content) == 1:
        q_bob.Z()

    print("\nResult of measurement of Bob's qubit: ", q_bob.measure())


def main():
   # initialize network
   network = Network.get_instance()
   backend = EQSNBackend()

   nodes = ['Alice', 'Bob']
   network.start(nodes, backend)
   network.delay = 0.2

   host_alice = Host('Alice')
   host_bob = Host('Bob')

   # Add one way classical and quantum connection
   host_alice.add_connection('Bob')
   host_bob.add_connection('Alice')

   host_alice.start()
   host_bob.start()

   network.add_host(host_alice) 
   network.add_host(host_bob) 

   print("We implement non-local CNOT gate here")
   print("Bob's qubit is the control qubit and Alice's qubit is the target qubit")
   t1 = host_alice.run_protocol(protocol_alice, (host_bob.host_id, backend))
   t2 = host_bob.run_protocol(protocol_bob, (host_alice.host_id,))

   t1.join()
   t2.join()
   network.stop(True)

if __name__ == '__main__':
   main()
