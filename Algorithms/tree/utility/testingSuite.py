import pickle
import json
import time
from phe import paillier

# key gen time measurement
start = time.time()
public_key, private_key = paillier.generate_paillier_keypair()
end = time.time ()
time_keygen = end - start

# encryption time measurement
start = time.time()
data = public_key.encrypt(0.274654836348645646534)
end = time.time()
time_encrypt = end - start

# get val time measurement
start = time.time()
val = data.ciphertext()
end = time.time()
time_cipher = end - start

# get exp time measurement
start = time.time()
exp = data.exponent
end = time.time()
time_exp = end - start

# serialization time measurement
start = time.time()
val = pickle.dumps(str(val))
exp = pickle.dumps(str(exp))
end = time.time()
time_dump = end - start

# deserialization time measurement
start = time.time()
val = pickle.loads(val)
exp = pickle.loads(exp)
end = time.time()
time_load = end - start

# make EncNum time measurement
start = time.time()
new_enc = paillier.EncryptedNumber(public_key, int(val), int(exp))
end = time.time()
time_newenc = end - start

# addition with float time measurement
start = time.time()
data += 0.3465 * 0.3333499
end = time.time()
time_addfloat = end - start

# decryption time measurement
start = time.time()
private_key.decrypt(data)
end = time.time()
time_decrypt = end - start

# public key fraction time measurement
start = time.time()
data = public_key.n
end = time.time()
time_keysplit = end - start

print("Key-Gen: %s" % (str(time_keygen)))
print("Encrypt: %s" % (str(time_encrypt)))
print("Decrypt: %s" % (str(time_decrypt)))
print("AddFloat: %s" % (str(time_addfloat)))
print("KeySplit: %s" % (str(time_keysplit)))
print("Cipher: %s" % (str(time_cipher)))
print("Exponent: %s" % (str(time_exp)))
print("newEnc: %s" % (str(time_newenc)))
print("Dump: %s" % (str(time_dump)))
print("Load: %s" % (str(time_load)))