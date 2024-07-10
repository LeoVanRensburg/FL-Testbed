import sys
import node
import threading
import time
import datetime
import numpy as np

class processVirtualization(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
    def run(self):
        self.agent.start()

def main():
    # setup
    nodeValues = [np.array([10, 20, 30]),
                  np.array([600, 700, 800]),
                  np.array([-586, -486, -386]),
                  np.array([400, 500, 600]),
                  np.array([100, 200, 300])]
    nodeIPs = ["0.0.0.0", "10.0.0.21", "10.0.1.21", "10.0.2.21", "10.0.3.21"]
    algorithm = 1
    topology = 6
    nrOfIterations = 10
    
    if(topology == 6):
        # FCG
        node1 = node.Node(nodeIPs[0], 9999, nodeValues[0], [nodeIPs[i] for i in [1,2,3,4]], algorithm, nrOfIterations)
        print(f"Creating nodeIP: {node1.HOST} with value {node1.VALUE} on Port {node1.PORT}")
        print("node creation complete")
       
        now = datetime.datetime.now()
        wait_seconds = 60 - now.second

        time.sleep(wait_seconds)

        print("Starting")

        #node run
        processVirtualization(node1).start()

if __name__ == "__main__":
    main()
