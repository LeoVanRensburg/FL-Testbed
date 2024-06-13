from utility import server
from phe import paillier
import sys
import socket
import time
import pickle
import random

# represents one agent of the network
class Node():
    # initializes node with HOST-IP, PORT NR. and NODE VALUE and NEIGHBOR-NODES
    def __init__(self, HOST, PORT, VALUE, neighbors, algorithm, nrOfIterations, reportTo):
        # nodes are identified by their IP
        self.HOST = HOST
        # preassigned Port Number, Same for every agent
        self.PORT = PORT
        # creating the key pair for paillier encryption
        public_key, private_key = paillier.generate_paillier_keypair()
        self.PUBLIC = public_key
        self.PRIVATE = private_key
        # value is the current local average
        self.VALUE = float(VALUE)
        # oldValue is the local average of the previous iteration 
        self.OLDVALUE = float(VALUE)
        # list of neighbors excluding self
        self.neighbors = neighbors
        # list of neighbors including self
        self.closedNeighbors = list(neighbors)
        self.closedNeighbors.append(HOST)
        # neighbors connections
        self.whoKnowsWho = {}
        # own neighbor link values
        self.linkValues = {}
        # yij dictionary
        self.yij = {}
        # wij dictionary (weights to every neighbor)
        self.wij = {}       
        # transmission counter
        self.nrTransmissions = 0
        # chosen algorithm
        self.algorithm = algorithm
        # nr. of iterations
        self.nrOfIterations = nrOfIterations
        self.reportTo = reportTo


    """ Represents main, will do as follows:
        1. Setup Server and starts Server thread
        2. Starts time measurement
        3. Starts Algorithm
        4. Ends time measurement
        5. Notifies all neighbors to close
        6. Waits for signal of all neighbors that server is not needed anymore and then joins own server
        7. Display final results of this node (Final value, Nr. of Transmissions, Time needed)
    """
    def start(self):
        # server startup, creates new Thread and sleeps for 1s so all server have time to start"""
        nodeServer = server.Server(self.HOST, self.PORT, self.VALUE, 1, self.neighbors, self.algorithm)
        nodeServer.start()

        time.sleep(1)

        # start time measurement
        start = time.time()

        # start algorithm
        if(self.algorithm == 1):
            self.computeSimple(nodeServer, self.neighbors)
        elif(self.algorithm == 2):
            self.computeNeighborhood(nodeServer)
        
        # finish time measurement
        end = time.time()

        # send close message to all neighbors
        for i in self.neighbors:
            self.sendClose(i)

        # close server
        while not nodeServer.CLOSED:
            time.sleep(0.1)
        nodeServer.join()

        # print results
        # random is used so the nodes display their final value at different times
        time.sleep(random.random())
        print("Node: " + self.HOST + " has final result: " + str(self.VALUE))
        
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get local machine name
        host = self.reportTo
        port = 12345
        # Connect to the server
        client_socket.connect((host, port))
        # Send the number
        number = self.VALUE
        client_socket.send(str(self.VALUE).encode())
        client_socket.close()
        print("Node: " + self.HOST + " has successfully transmitted")
        
        if(self.algorithm == 1):
            print("Node: " + self.HOST + " took " + str((end-start)) + " seconds")
        else:
            print("Node: " + self.HOST + " took " + str((end-start)-3) + " seconds")
        print("Node: " + self.HOST + " needed " + str(self.nrTransmissions) + " transmissions")


    """ This is the main method for communicating with other nodes when performing average calculation
        using the Simple algorithm.
        Runs as follows:
            1. Create new socket and connect with specific neighbor
            2. Perform Algorithm specific communication
    """
    def send(self, neighbor, iteration, retry_limit=1000):
        retry_count = 0
        while retry_count < retry_limit:
            # making connection
            cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cl.connect((neighbor, self.PORT))
            # send iteration for iteration check
            cl.sendall(b'%d' % (iteration))
            # receiving either -1 if iteration doesn't match or Value if iteration matches
            rec = float(cl.recv(1024))
            if rec == -1:
                cl.close()
                retry_count += 1
                time.sleep(1)  # Wait a bit before retrying
                continue
            else:
                print("%s has Value: %f and receives %f" % (self.HOST, self.VALUE, rec))
                self.nrTransmissions += 1
                cl.close()
                return rec
        # If the function reaches this point, it means it has retried the maximum number of times
        print("Failed to send data to %s after %d retries" % (neighbor, retry_limit))
        return None



    def sendNeighborhoodEncryption(self, neighbor, encVal, weight, iteration):
        # making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))
        # sends notification that communication is for average calculation
        cl.sendall(b'average')
        data = cl.recv(1024)
        if(data == b'ack'):
            # send iteration for iteration check
            cl.sendall(b'%d' % (iteration))
            # wait for big or ok
            data = cl.recv(1024)
            if(data == b'big'):
                # server lags behind
                cl.close()
                return self.sendNeighborhoodEncryption(neighbor, encVal, weight, iteration)
            elif(data == b'ok'):
                # sending public key fragment n
                data = pickle.dumps(str(self.PUBLIC.n))
                cl.sendall(data)
                # wait for key ack
                data = cl.recv(1024)
                if(data == b'ack'):
                    # dumping and sending val, exp
                    data_val = pickle.dumps(str(encVal.ciphertext()))
                    data_exp = pickle.dumps(str(encVal.exponent))
                    # send val
                    cl.sendall(data_val)
                    # wait for send ack
                    data = cl.recv(1024)
                    # send exp
                    cl.sendall(data_exp)
                    # wait for exp ack
                    cl.recv(1024)
                    # dumping weight
                    data = pickle.dumps(str(weight))
                    # sending weight
                    cl.sendall(data)
                    # receiving val
                    data_val = cl.recv(8192)
                    # load val
                    data_val = pickle.loads(data_val)
                    cl.sendall(b'ack')
                    # receiving exp
                    data_exp = cl.recv(8192)
                    # load exp
                    data_exp = pickle.loads(data_exp)
                    # close cl socket
                    cl.close()
                    # make enc num
                    data = paillier.EncryptedNumber(self.PUBLIC, int(data_val), int(data_exp))
                    self.nrTransmissions += 1
                    return data
                else:
                    print("something went wrong")
            

    """ send method for the neighborhood algorithm (weight calculation)
        differs from regular send because no values are exchanged only neighbor addresses
    """
    def sendNeighborhood(self, neighbor, mode):
        # making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))

        # mode 1 is the transmission of the closed neighborhood
        if mode == 1:
            # serialize list
            data_string = pickle.dumps(self.closedNeighbors)

            # sending mode nr. first
            cl.sendall(b'%d' % (mode))
            if(cl.recv(1024) == b'ok'):
                cl.sendall(b'%s' % data_string)
                self.nrTransmissions += 1
            cl.close()
        # mode 2 is for sending own yij value for one specific neighbor
        elif mode == 2:
            cl.sendall(b'%d' % (mode))
            if(cl.recv(1024) == b'ok'):
                cl.sendall(self.HOST.encode())
            if(cl.recv(1024) == b'ok'):
                cl.sendall(b'%f' % (self.yij[neighbor]))
                self.nrTransmissions += 1
            cl.close()


    """ This method is responsible for sending the message to all other nodes that this node has completed the algorithm and is closing it's server
    """
    def sendClose(self, neighbor):
        #making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))

        #send close message
        cl.sendall(b'close')
        print("Close send, received: " + str(cl.recv(1024)))
        cl.close()


    """ The Simple Algorithm
    """
    def computeSimple(self, nodeServer, nrNeighbors):
        #This for loop determines how many iterations the algorithm will go through, lower -> less accuracy, higher -> more accuracy
        for i in range(1, self.nrOfIterations + 1):
            #Server always is in same iteration as the node it belongs to
            nodeServer.ITERATION = i
            
            #print Iteration nr.
            print(self.HOST + " is in iteration: " + str(i))

            #Create list with initial own value
            values = [self.VALUE]

            #Fetch current value from each neighbor and store in list
            for j in self.neighbors:
                values.append(self.send(j, i))

            #Execute algorithm, Update current and old value
            self.OLDVALUE = self.VALUE
            avg = 0
            for i in values:
                avg += i
            # Unweighted calculation of the average
            self.VALUE = avg / (len(nrNeighbors) + 1)

            #Update value on server to new avg and old avg
            nodeServer.OLDVALUE = self.OLDVALUE
            nodeServer.VALUE = self.VALUE


    """ The Neighborhood Algorithm
    """
    def computeNeighborhood(self, nodeServer):
        # first the weight for each neighbor is calculated / This is the essential part that differs this algo from another
        self.calculateWeightsFromNeighborhood(nodeServer)
        # calculation of the average
        for i in range(1, self.nrOfIterations + 1):
            print(self.HOST + " is in iteration: " + str(i))
            # initialize avg of this iteration with own value
            avg = self.VALUE * self.wij[self.HOST]
            # encrypt average for sending
            avg = self.PUBLIC.encrypt(avg)
            # connect with every neighbor and hand over current avg
            for j in self.neighbors:
                avg = self.sendNeighborhoodEncryption(j, avg, self.wij[j], i)
            # decrypt avg for display
            avg = self.PRIVATE.decrypt(avg)
            print("%s has new value: %f" % (self.HOST, avg))
            
            # update node's current and old value
            self.OLDVALUE = self.VALUE
            self.VALUE = avg

            # update nodes iteration, value and oldvalue
            # protected to avoid value mixups in this node's server
            nodeServer.VALUECHANGE = True
            nodeServer.ITERATION += 1
            nodeServer.OLDVALUE = self.OLDVALUE
            nodeServer.VALUE = self.VALUE
            nodeServer.VALUECHANGE = False
    
    """ The weight calculation from the neighborhood algorithm
        Keep prints for debugging
    """
    def calculateWeightsFromNeighborhood(self, nodeServer):
        #mode is used to set the send configuration
        mode = 1

        # step 1: broadcast own list of own neighbors to neighbors
        for i in self.neighbors:
            self.sendNeighborhood(i, mode)

        time.sleep(2)

        # make dictionary for relations that each node has
        for i in nodeServer.CLOSEDNEIGHBORS:
            self.whoKnowsWho[i[len(i) - 1]] = i

        # step 2: calculate yij
        for i in self.neighbors:
            self.yij[i] = (1 - ( (len(self.listIntersect(self.closedNeighbors, self.whoKnowsWho[i]))) / (1 + 2 * min(len(self.closedNeighbors), len(self.whoKnowsWho[i])) - len(self.listIntersect(self.closedNeighbors, self.whoKnowsWho[i]))) ))

        # step 3: calculate a
        a = sum(self.yij.values())
        if a > 1:
            for i in self.neighbors:
                self.yij[i] = self.yij[i] / a

        # step 4: send yij to every neighbor j
        mode = 2
        for i in self.neighbors:
            self.sendNeighborhood(i, mode)
        time.sleep(1)

        # step 5: calculate weights
        for i in self.neighbors:
            self.wij[i] = min(self.yij[i], nodeServer.YIJ[i])
        self.wij[self.HOST] = (1 - sum(self.wij.values()))
        # If value is very small it is set equal to 0 to save some computation time
        if(abs(self.wij[self.HOST]) < 0.001):
            self.wij[self.HOST] = 0
        print("%s: Weight calculation complete" % self.HOST)
        print("%s: %s" % (self.HOST, self.wij))
        return 1


    """ returns an intersection of two lists
    """
    def listIntersect(self, list1, list2):
        return list(set(list1) & set(list2))
        
# represents one agent of the network
class Node2():
    # initializes node with HOST-IP, PORT NR. and NODE VALUE and NEIGHBOR-NODES
    def __init__(self, HOST, PORT, VALUE, neighbors, algorithm, nrOfIterations):
        # nodes are identified by their IP
        self.HOST = HOST
        # preassigned Port Number, Same for every agent
        self.PORT = PORT
        # creating the key pair for paillier encryption
        public_key, private_key = paillier.generate_paillier_keypair()
        self.PUBLIC = public_key
        self.PRIVATE = private_key
        # value is the current local average
        self.VALUE = float(VALUE)
        # oldValue is the local average of the previous iteration 
        self.OLDVALUE = float(VALUE)
        # list of neighbors excluding self
        self.neighbors = neighbors
        # list of neighbors including self
        self.closedNeighbors = list(neighbors)
        self.closedNeighbors.append(HOST)
        # neighbors connections
        self.whoKnowsWho = {}
        # own neighbor link values
        self.linkValues = {}
        # yij dictionary
        self.yij = {}
        # wij dictionary (weights to every neighbor)
        self.wij = {}       
        # transmission counter
        self.nrTransmissions = 0
        # chosen algorithm
        self.algorithm = algorithm
        # nr. of iterations
        self.nrOfIterations = nrOfIterations


    """ Represents main, will do as follows:
        1. Setup Server and starts Server thread
        2. Starts time measurement
        3. Starts Algorithm
        4. Ends time measurement
        5. Notifies all neighbors to close
        6. Waits for signal of all neighbors that server is not needed anymore and then joins own server
        7. Display final results of this node (Final value, Nr. of Transmissions, Time needed)
    """
    def start(self):
        # server startup, creates new Thread and sleeps for 1s so all server have time to start"""
        nodeServer = server.Server(self.HOST, self.PORT, self.VALUE, 1, self.neighbors, self.algorithm)
        nodeServer.start()

        time.sleep(1)

        # start time measurement
        start = time.time()

        # start algorithm
        if(self.algorithm == 1):
            self.computeSimple(nodeServer, self.neighbors)
        elif(self.algorithm == 2):
            self.computeNeighborhood(nodeServer)
        
        # finish time measurement
        end = time.time()

        # send close message to all neighbors
        for i in self.neighbors:
            self.sendClose(i)

        # close server
        while not nodeServer.CLOSED:
            time.sleep(0.1)
        nodeServer.join()

        # print results
        # random is used so the nodes display their final value at different times
        time.sleep(random.random())
        print("Node: " + self.HOST + " has final result: " + str(self.VALUE))
        if(self.algorithm == 1):
            print("Node: " + self.HOST + " took " + str((end-start)) + " seconds")
        else:
            print("Node: " + self.HOST + " took " + str((end-start)-3) + " seconds")
        print("Node: " + self.HOST + " needed " + str(self.nrTransmissions) + " transmissions")


    """ This is the main method for communicating with other nodes when performing average calculation
        using the Simple algorithm.
        Runs as follows:
            1. Create new socket and connect with specific neighbor
            2. Perform Algorithm specific communication
    """
    def send(self, neighbor, iteration, retry_limit=1000):
        retry_count = 0
        while retry_count < retry_limit:
            # making connection
            cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cl.connect((neighbor, self.PORT))
            # send iteration for iteration check
            cl.sendall(b'%d' % (iteration))
            # receiving either -1 if iteration doesn't match or Value if iteration matches
            rec = float(cl.recv(1024))
            if rec == -1:
                cl.close()
                retry_count += 1
                time.sleep(1)  # Wait a bit before retrying
                continue
            else:
                print("%s has Value: %f and receives %f" % (self.HOST, self.VALUE, rec))
                self.nrTransmissions += 1
                cl.close()
                return rec
        # If the function reaches this point, it means it has retried the maximum number of times
        print("Failed to send data to %s after %d retries" % (neighbor, retry_limit))
        return None



    def sendNeighborhoodEncryption(self, neighbor, encVal, weight, iteration):
        # making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))
        # sends notification that communication is for average calculation
        cl.sendall(b'average')
        data = cl.recv(1024)
        if(data == b'ack'):
            # send iteration for iteration check
            cl.sendall(b'%d' % (iteration))
            # wait for big or ok
            data = cl.recv(1024)
            if(data == b'big'):
                # server lags behind
                cl.close()
                return self.sendNeighborhoodEncryption(neighbor, encVal, weight, iteration)
            elif(data == b'ok'):
                # sending public key fragment n
                data = pickle.dumps(str(self.PUBLIC.n))
                cl.sendall(data)
                # wait for key ack
                data = cl.recv(1024)
                if(data == b'ack'):
                    # dumping and sending val, exp
                    data_val = pickle.dumps(str(encVal.ciphertext()))
                    data_exp = pickle.dumps(str(encVal.exponent))
                    # send val
                    cl.sendall(data_val)
                    # wait for send ack
                    data = cl.recv(1024)
                    # send exp
                    cl.sendall(data_exp)
                    # wait for exp ack
                    cl.recv(1024)
                    # dumping weight
                    data = pickle.dumps(str(weight))
                    # sending weight
                    cl.sendall(data)
                    # receiving val
                    data_val = cl.recv(8192)
                    # load val
                    data_val = pickle.loads(data_val)
                    cl.sendall(b'ack')
                    # receiving exp
                    data_exp = cl.recv(8192)
                    # load exp
                    data_exp = pickle.loads(data_exp)
                    # close cl socket
                    cl.close()
                    # make enc num
                    data = paillier.EncryptedNumber(self.PUBLIC, int(data_val), int(data_exp))
                    self.nrTransmissions += 1
                    return data
                else:
                    print("something went wrong")
            

    """ send method for the neighborhood algorithm (weight calculation)
        differs from regular send because no values are exchanged only neighbor addresses
    """
    def sendNeighborhood(self, neighbor, mode):
        # making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))

        # mode 1 is the transmission of the closed neighborhood
        if mode == 1:
            # serialize list
            data_string = pickle.dumps(self.closedNeighbors)

            # sending mode nr. first
            cl.sendall(b'%d' % (mode))
            if(cl.recv(1024) == b'ok'):
                cl.sendall(b'%s' % data_string)
                self.nrTransmissions += 1
            cl.close()
        # mode 2 is for sending own yij value for one specific neighbor
        elif mode == 2:
            cl.sendall(b'%d' % (mode))
            if(cl.recv(1024) == b'ok'):
                cl.sendall(self.HOST.encode())
            if(cl.recv(1024) == b'ok'):
                cl.sendall(b'%f' % (self.yij[neighbor]))
                self.nrTransmissions += 1
            cl.close()


    """ This method is responsible for sending the message to all other nodes that this node has completed the algorithm and is closing it's server
    """
    def sendClose(self, neighbor):
        #making connection
        cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cl.connect((neighbor, self.PORT))

        #send close message
        cl.sendall(b'close')
        print("Close send, received: " + str(cl.recv(1024)))
        cl.close()


    """ The Simple Algorithm
    """
    def computeSimple(self, nodeServer, nrNeighbors):
        #This for loop determines how many iterations the algorithm will go through, lower -> less accuracy, higher -> more accuracy
        for i in range(1, self.nrOfIterations + 1):
            #Server always is in same iteration as the node it belongs to
            nodeServer.ITERATION = i
            
            #print Iteration nr.
            print(self.HOST + " is in iteration: " + str(i))

            #Create list with initial own value
            values = [self.VALUE]

            #Fetch current value from each neighbor and store in list
            for j in self.neighbors:
                values.append(self.send(j, i))

            #Execute algorithm, Update current and old value
            self.OLDVALUE = self.VALUE
            avg = 0
            for i in values:
                avg += i
            # Unweighted calculation of the average
            self.VALUE = avg / (len(nrNeighbors) + 1)

            #Update value on server to new avg and old avg
            nodeServer.OLDVALUE = self.OLDVALUE
            nodeServer.VALUE = self.VALUE


    """ The Neighborhood Algorithm
    """
    def computeNeighborhood(self, nodeServer):
        # first the weight for each neighbor is calculated / This is the essential part that differs this algo from another
        self.calculateWeightsFromNeighborhood(nodeServer)
        # calculation of the average
        for i in range(1, self.nrOfIterations + 1):
            print(self.HOST + " is in iteration: " + str(i))
            # initialize avg of this iteration with own value
            avg = self.VALUE * self.wij[self.HOST]
            # encrypt average for sending
            avg = self.PUBLIC.encrypt(avg)
            # connect with every neighbor and hand over current avg
            for j in self.neighbors:
                avg = self.sendNeighborhoodEncryption(j, avg, self.wij[j], i)
            # decrypt avg for display
            avg = self.PRIVATE.decrypt(avg)
            print("%s has new value: %f" % (self.HOST, avg))
            
            # update node's current and old value
            self.OLDVALUE = self.VALUE
            self.VALUE = avg

            # update nodes iteration, value and oldvalue
            # protected to avoid value mixups in this node's server
            nodeServer.VALUECHANGE = True
            nodeServer.ITERATION += 1
            nodeServer.OLDVALUE = self.OLDVALUE
            nodeServer.VALUE = self.VALUE
            nodeServer.VALUECHANGE = False
    
    """ The weight calculation from the neighborhood algorithm
        Keep prints for debugging
    """
    def calculateWeightsFromNeighborhood(self, nodeServer):
        #mode is used to set the send configuration
        mode = 1

        # step 1: broadcast own list of own neighbors to neighbors
        for i in self.neighbors:
            self.sendNeighborhood(i, mode)

        time.sleep(2)

        # make dictionary for relations that each node has
        for i in nodeServer.CLOSEDNEIGHBORS:
            self.whoKnowsWho[i[len(i) - 1]] = i

        # step 2: calculate yij
        for i in self.neighbors:
            self.yij[i] = (1 - ( (len(self.listIntersect(self.closedNeighbors, self.whoKnowsWho[i]))) / (1 + 2 * min(len(self.closedNeighbors), len(self.whoKnowsWho[i])) - len(self.listIntersect(self.closedNeighbors, self.whoKnowsWho[i]))) ))

        # step 3: calculate a
        a = sum(self.yij.values())
        if a > 1:
            for i in self.neighbors:
                self.yij[i] = self.yij[i] / a

        # step 4: send yij to every neighbor j
        mode = 2
        for i in self.neighbors:
            self.sendNeighborhood(i, mode)
        time.sleep(1)

        # step 5: calculate weights
        for i in self.neighbors:
            self.wij[i] = min(self.yij[i], nodeServer.YIJ[i])
        self.wij[self.HOST] = (1 - sum(self.wij.values()))
        # If value is very small it is set equal to 0 to save some computation time
        if(abs(self.wij[self.HOST]) < 0.001):
            self.wij[self.HOST] = 0
        print("%s: Weight calculation complete" % self.HOST)
        print("%s: %s" % (self.HOST, self.wij))
        return 1


    """ returns an intersection of two lists
    """
    def listIntersect(self, list1, list2):
        return list(set(list1) & set(list2))
