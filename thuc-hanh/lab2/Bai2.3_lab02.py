from Crypto.Cipher import DES

def bytes_to_bitstring(data):
    return bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)

def bitstring_to_bytes(bitstring):
    int_val = int(bitstring, 2)
    return int_val.to_bytes(len(bitstring) // 8, 'big')

def test_avalanche():
    key = b'87654321'
    p1 = b'STAYHOME'
    p2 = b'STAYHOMA'
    
    cipher = DES.new(key, DES.MODE_ECB)
    c1 = cipher.encrypt(p1)
    c2 = cipher.encrypt(p2)
    
    bin_c1 = bytes_to_bitstring(c1)
    bin_c2 = bytes_to_bitstring(c2)
    
    hamming_distance = sum(b1 != b2 for b1, b2 in zip(bin_c1, bin_c2))
    percent_changed = (hamming_distance / len(bin_c1)) * 100
    
    decrypted_bytes1 = bitstring_to_bytes(bin_c1)
    decrypted_bytes2 = bitstring_to_bytes(bin_c2)
    
    cipher_dec = DES.new(key, DES.MODE_ECB)
    
    print("TEST CASE Bai2.3")
    print(f"Key                 : {key.decode('utf-8')}")
    print(f"Plaintext 1         : {p1.decode('utf-8')}")
    print(f"Plaintext 2         : {p2.decode('utf-8')}")
    print(" ")
    print(f"Ciphertext 1 (bin)  : {bin_c1}")
    print(f"Ciphertext 2 (bin)  : {bin_c2}")
    print(" ")
    print(f"So bit khac nhau     : {hamming_distance} / {len(bin_c1)} bit")
    print(f"Ti le                : {percent_changed:.2f}%")

if __name__ == "__main__":
    test_avalanche()