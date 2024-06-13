import socket
import threading
import _thread
import time
import pickle
from phe import paillier

""" Handles incoming communication for Node, performs calculations, and sends back values depending on the algorithm chosen
"""
class Server(threading.Thread):
    def __init__(self, HOST, PORT, VALUE, ITERATION, NEIGHBORS, ALGORITHM):
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.VALUE = VALUE
        self.OLDVALUE = VALUE
        self.NRNEIGHBORS = len(NEIGHBORS)
        self.CLOSEDNEIGHBORS = []
        self.YIJ = {}
        self.ITERATION = ITERATION
        self.ALGORITHM = ALGORITHM
        self.VALUECHANGE = False
        self.CLOSE = False
        self.CLOSED = False
        print("Creating Server on %s with Port %s and value %d" % (HOST, PORT, VALUE))

    """ Creates server socket and listens for incoming communication requests
        As longs as no close signal is given it repeatedly accepts new connections and hands them over to a new thread
        When close signal is given, closes server socket and finishes
    """
    def run(self):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.HOST, self.PORT))
            s.settimeout(20)
            s.listen()
            print(self.HOST + " is listening")
            # Check for close flag and depending on that creates new comm. or closes server socket
            while not self.CLOSE:
                try:
                    conn, addr = s.accept()
                    print(self. HOST + ' is connected by', addr)
                    # handover communication to new thread
                    _thread.start_new_thread(self.handleClient, (conn,addr))
                except socket.timeout:
                    print("Calculation done closing " + self.HOST)
                    self.CLOSED = True
                    s.close()


    """ Handles incommming communications, represents one socket communication
        Performs differently depending on the algorithm
    """
    def handleClient(self, conn, addr):
        #receive incoming message
        data = conn.recv(1024)
        #check for correct transmission
        if not data:
            print("ERROR IN TRANSMISSION - NODE: " + self.HOST)
            return -1
        #check for close signal
        if data == b'close':
            conn.sendall(b'bye')
            self.NRNEIGHBORS -= 1
            if self.NRNEIGHBORS == 0:
                self.CLOSE = True
            conn.close()
        else:
            if(self.ALGORITHM == 1):    
                #change data format in int (data should be iteration nr)
                data = int(data)
                if data < self.ITERATION:
                    conn.sendall(b'%f' % self.OLDVALUE)
                elif data > self.ITERATION:
                    conn.sendall(b'%d' % -1)
                else:
                    conn.sendall(b'%f' % self.VALUE)
                #closes this client socket
                conn.close()
            elif(self.ALGORITHM == 2):
                # check for average calculation
                if(data == b'average'):
                    conn.sendall(b'ack')
                    #receiving iteration
                    data = conn.recv(1024)
                    it = int(data)

                    if it < self.ITERATION:
                        # other node lags behind
                        conn.sendall(b'ok')
                        # receiving public key
                        data = conn.recv(8192)
                        # send key ack
                        conn.sendall(b'ack')
                        # create PublicKey from n
                        data = pickle.loads(data)
                        public_key = paillier.PaillierPublicKey(int(data))
                        # receiving val
                        data_val = conn.recv(8192)
                        # load val
                        data_val = pickle.loads(data_val)
                        # send val ack
                        conn.sendall(b'ack')
                        # receiving exponent
                        data_exp = conn.recv(8192)
                        # load exp
                        data_exp = pickle.loads(data_exp)
                        # send exp ack
                        conn.sendall(b'ack')
                        #receiving weight
                        weight = conn.recv(2048)
                        weight = float(pickle.loads(weight))
                        #making encrypted number
                        val = paillier.EncryptedNumber(public_key, int(data_val), int(data_exp))
                        #adding own value
                        val += weight * self.OLDVALUE
                        #dumping added average
                        data_val = pickle.dumps(str(val.ciphertext()))
                        data_exp = pickle.dumps(str(val.exponent))
                        #sending back added average
                        conn.sendall(data_val)
                        conn.recv(1024)
                        conn.sendall(data_exp)
                    elif it > self.ITERATION:
                        # node is ahead of this server and has to wait
                        conn.sendall(b'big')
                    else:
                        conn.sendall(b'ok')
                        # receiving public key
                        data = conn.recv(8192)
                        # creating PublicKey from n
                        data = pickle.loads(data)
                        public_key = paillier.PaillierPublicKey(int(data))
                        # send key ack
                        conn.sendall(b'ack')
                        # receiving val
                        data_val = conn.recv(8192)
                        # load val
                        data_val = pickle.loads(data_val)
                        # send val ack
                        conn.sendall(b'ack')
                        # receiving exp
                        data_exp = conn.recv(8192)
                        # load exp                     
                        data_exp = pickle.loads(data_exp)
                        # send exp ack
                        conn.sendall(b'ack')
                        # receiving weight
                        weight = conn.recv(2048)
                        weight = float(pickle.loads(weight))
                        # making encrypted number
                        val = paillier.EncryptedNumber(public_key, int(data_val), int(data_exp))
                        # adding own value, iteration check because iteration of server might have changed by its node
                        if(it != self.ITERATION):
                            val += weight * self.OLDVALUE
                        else:
                            val += weight * self.VALUE                      
                        # dumping added average
                        data_val = pickle.dumps(str(val.ciphertext()))
                        data_exp = pickle.dumps(str(val.exponent))
                        # send val
                        conn.sendall(data_val)
                        # rec val ack
                        conn.recv(1024)
                        # sending back added average exp
                        conn.sendall(data_exp)
                    #closes this client socket ending the communication
                    conn.close()
                # check for weight calculation mode
                elif(int(data) == 1):
                    conn.sendall(b'ok')
                    data = conn.recv(1024)
                    self.CLOSEDNEIGHBORS.append(pickle.loads(data))
                    conn.close()
                elif(int(data) == 2):
                    conn.sendall(b'ok')
                    data = conn.recv(1024)
                    host = data.decode()
                    conn.sendall(b'ok')
                    data = conn.recv(1024)
                    self.YIJ[host] = float(data)
                    conn.close()