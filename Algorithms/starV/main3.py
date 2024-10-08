import sys
import node
import threading
import time
import datetime
import numpy as np

""" This class creates a new thread for every node
    and starts it
"""
class processVirtualization(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
    def run(self):
        self.agent.start()

""" Here all the setup of the testing environment is done
    There are a number of modes that you can run:
    
    Algorithms:
    1. Simple Distributed Consensus (only works for topologies with uniform degree)
    2. Neighborhood algorithm with added Paillier encryption

    Topologies:
    1. Mesh (Same degree on every vertice)
    2. Cluster (Two neighborhoods of nodes seperated by a link through only 1 vertice)
    3. Star (All nodes are connected to 1 middle node)
    4. Ring (Worst case scenario, represents a chained list that is connected at the end)
    5. Mesh (Just a Mesh with no special properties, aside from cluster probably the most realistic)
    6. Fully connected Mesh (Ideal case since theoretically only 1 communication/iteration is needed)

    Nr. of Iterations:
    Set the number of iterations that the algorithm should perform.
    In general, more iterations -> more precise results

    Node Values, Vote Values, Node IPs:
    If you want to add new nodes you have to add a new IP for it in the IP list as well as choose a value for every node in the value list.
    (Note: Node Values are for Sensor data  (non-binary), Vote Values are for Voting data (binary))
"""
def main():
    # setup
    nodeValues = [np.array([10, 20, 30]),
                  np.array([600, 700, 800]),
                  np.array([-586, -486, -386]),
                  np.array([400, 500, 600]),
                  np.array([100, 200, 300])]
    nodeIPs = ["0.0.0.0", "10.0.0.21", "10.0.1.21", "10.0.2.21", "10.0.3.21"]
    voteValues = [0,1,0,1,0,1,0,1]
    nodeIPs = ["10.0.0.20", "10.0.0.21", "10.0.0.22", "10.0.0.23", "10.0.0.24", "10.0.0.25", "10.0.0.26", "10.0.0.27"]
    algorithm = 1
    topology = 6
    nrOfIterations = 10
    
    if(topology == 6):
        # FCG
        node3 = node.Node(nodeIPs[2], 9999, nodeValues[2], [nodeIPs[i] for i in [0,1,3,4]], algorithm, nrOfIterations)
        print(f"Creating nodeIP: {node3.HOST} with value {node3.VALUE} on Port {node3.PORT}")
        print("node creation complete")
    
        now = datetime.datetime.now()
        wait_seconds = 60 - now.second

        time.sleep(wait_seconds)

        print("Starting")

        #node run
        processVirtualization(node3).start()
        

if __name__ == "__main__":
    main()
