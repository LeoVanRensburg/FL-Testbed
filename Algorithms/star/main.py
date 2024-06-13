import sys
import node
import threading
import time
import datetime

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
    nodeValues = [10,600,-586,400, 100, 100, -895, 10]
    voteValues = [0,1,0,1,0,1,0,1]
    nodeIPs = ["127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5", "127.0.0.6", "127.0.0.7", "127.0.0.8"]
    algorithm = 1
    topology = 6
    nrOfIterations = 10
    
    if(topology == 6):
        # FCG
        node1 = node.Node(nodeIPs[0], 9999, nodeValues[0], [nodeIPs[i] for i in [1,2,3,4]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node1.HOST, node1.VALUE, node1.PORT))
        node2 = node.Node(nodeIPs[1], 9999, nodeValues[1], [nodeIPs[i] for i in [0,2,3,4]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node2.HOST, node2.VALUE, node2.PORT))
        node3 = node.Node(nodeIPs[2], 9999, nodeValues[2], [nodeIPs[i] for i in [0,1,3,4]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node3.HOST, node3.VALUE, node3.PORT))
        node4 = node.Node(nodeIPs[3], 9999, nodeValues[3], [nodeIPs[i] for i in [0,1,2,4]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node4.HOST, node4.VALUE, node4.PORT))
        node5 = node.Node(nodeIPs[4], 9999, nodeValues[4], [nodeIPs[i] for i in [0,1,2,3]], algorithm, nrOfIterations)
        print("Creating nodeIP: %s with value %d on Port %d" % (node5.HOST, node5.VALUE, node5.PORT))
        print("node creation complete")
        
        now = datetime.datetime.now()
        wait_seconds = 60 - now.second

        time.sleep(wait_seconds)

        print("Starting")

        #node run
        processVirtualization(node1).start()
        processVirtualization(node2).start()
        processVirtualization(node3).start()
        processVirtualization(node4).start()
        processVirtualization(node5).start()
        

if __name__ == "__main__":
    main()
