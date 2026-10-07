from Crypto.Cipher import AES

key = b'1234567890123456'
plaintext = b"UIT_LAB_UIT_LAB_UIT_LAB_UIT_LAB_"

# 1. AES-ECB
cipher_ecb = AES.new(key, AES.MODE_ECB)
ct_ecb = cipher_ecb.encrypt(plaintext)

# 2. AES-CBC (dùng IV cố định 16 bytes)
iv = b'0000000000000000'
cipher_cbc = AES.new(key, AES.MODE_CBC, iv=iv)
ct_cbc = cipher_cbc.encrypt(plaintext)

# 3. Thử nghiệm các Mode khác
cipher_cfb = AES.new(key, AES.MODE_CFB, iv=iv)
ct_cfb = cipher_cfb.encrypt(plaintext)

cipher_ofb = AES.new(key, AES.MODE_OFB, iv=iv)
ct_ofb = cipher_ofb.encrypt(plaintext)

cipher_ctr = AES.new(key, AES.MODE_CTR, nonce=b'12345678')
ct_ctr = cipher_ctr.encrypt(plaintext)

# In và so sánh kết quả từng khối 16-byte (32 ký tự Hex)
print("=== KẾT QUẢ MÃ HÓA (TÁCH THÀNH KHỐI 16-BYTE) ===")

print("\n--- 1. AES-ECB ---")
print(f"Khối 1: {ct_ecb[:16].hex()}")
print(f"Khối 2: {ct_ecb[16:].hex()}")

print("\n--- 2. AES-CBC ---")
print(f"Khối 1: {ct_cbc[:16].hex()}")
print(f"Khối 2: {ct_cbc[16:].hex()}")

print("\n--- 3. AES-CFB ---")
print(f"Khối 1: {ct_cfb[:16].hex()}")
print(f"Khối 2: {ct_cfb[16:].hex()}")

print("\n--- 4. AES-OFB ---")
print(f"Khối 1: {ct_ofb[:16].hex()}")
print(f"Khối 2: {ct_ofb[16:].hex()}")

print("\n--- 5. AES-CTR ---")
print(f"Khối 1: {ct_ctr[:16].hex()}")
print(f"Khối 2: {ct_ctr[16:].hex()}")