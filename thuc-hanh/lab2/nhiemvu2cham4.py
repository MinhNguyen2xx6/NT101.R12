from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

BS = 16
data = get_random_bytes(1000)              # 1. Tạo dữ liệu 1000 byte
key = get_random_bytes(16)                 # AES-128
iv = get_random_bytes(16)

def make(mode):
    if mode == "ECB": return AES.new(key, AES.MODE_ECB)
    if mode == "CBC": return AES.new(key, AES.MODE_CBC, iv)
    if mode == "CFB": return AES.new(key, AES.MODE_CFB, iv, segment_size=128)  # CFB-128
    if mode == "OFB": return AES.new(key, AES.MODE_OFB, iv)

for mode in ["ECB", "CBC", "CFB", "OFB"]:
    # 2. Mã hóa (ECB/CBC cần padding, CFB/OFB thì không)
    pt = pad(data, BS) if mode in ("ECB", "CBC") else data
    ct = bytearray(make(mode).encrypt(pt))

    # 3. Đảo 1 bit tại byte thứ 26 (chỉ số 25)
    ct[25] ^= 0x01

    # 4. Giải mã và so sánh từng khối
    dec = make(mode).decrypt(bytes(ct))
    bad = [i // BS + 1 for i in range(len(pt)) if dec[i] != pt[i]]
    bad_blocks = sorted(set(bad))
    print(f"{mode}: {len(bad)} byte sai, các khối bị hỏng: {bad_blocks}")