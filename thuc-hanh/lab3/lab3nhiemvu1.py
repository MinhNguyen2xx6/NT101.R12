import base64

# ---------------- Cơ bản ----------------
def make_keys(p, q, e):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return (e, n), (d, n)

def byte_len(n):
    return (n.bit_length() + 7) // 8

def int_to_bytes(m):
    return m.to_bytes(max(1, (m.bit_length() + 7) // 8), "big")

def b64decode_safe(s):
    s = s.strip().rstrip("=")
    if len(s) % 4 == 1:               # chuỗi bị cắt mất ký tự cuối
        print("  [!] Chuỗi Base64 bị cắt, bỏ ký tự cuối:", s[-1])
        s = s[:-1]
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s)

# ---------------- Bước 1: sinh khóa ----------------
params = {
    1: (11, 17, 7),
    2: (20079993872842322116151219, 676717145751736242170789, 17),
    3: (int("F7E75FDC469067FFDC4E847C51F452DF", 16),
        int("E85CED54AF57E53E092113E62F436F4F", 16),
        int("0D88C3", 16)),
}
keys = {}
print("=" * 60, "\nBƯỚC 1: KHÓA\n" + "=" * 60)
for i, (p, q, e) in params.items():
    keys[i] = make_keys(p, q, e)
    (e, n), (d, _) = keys[i]
    print(f"[Bộ {i}] n = {n}\n        PU = {{e={e}, n}}\n        PR = {{d={d}, n}}")
    print(f"        (hex) n = {n:X}, d = {d:X}\n")

# ---------------- Bước 2: M = 5, khóa bộ 1 ----------------
print("=" * 60, "\nBƯỚC 2: M = 5 (khóa bộ 1)\n" + "=" * 60)
(e1, n1), (d1, _) = keys[1]
M = 5
C = pow(M, e1, n1)
print(f"Bảo mật  : C = M^e mod n = {C};  giải mã = {pow(C, d1, n1)}")
S = pow(M, d1, n1)
print(f"Xác thực : S = M^d mod n = {S};  kiểm tra = {pow(S, e1, n1)}")

# ---------------- Bước 3: mã hóa chuỗi -> Base64 ----------------
print("\n" + "=" * 60, "\nBƯỚC 3: MÃ HÓA CHUỖI\n" + "=" * 60)
msg = "The University of Information Technology."
data = msg.encode()

def encrypt_bytes(data, key, use_private=False):
    """Mã hóa; chia khối nếu n nhỏ. Mỗi khối ra byte_len(n) byte."""
    exp, n = key
    k = byte_len(n)
    block = max(1, k - 1)            # khối < n (n nhỏ: 1 byte ASCII < 187)
    out = b""
    for i in range(0, len(data), block):
        m = int.from_bytes(data[i:i + block], "big")
        out += pow(m, exp, n).to_bytes(k, "big")
    return out

def decrypt_bytes(ct, key, ):
    exp, n = key
    k = byte_len(n)
    out = b""
    for i in range(0, len(ct), k):
        c = int.from_bytes(ct[i:i + k], "big")
        out += int_to_bytes(pow(c, exp, n))
    return out

for i in (1, 2, 3):
    pu, pr = keys[i]
    ct = encrypt_bytes(data, pu)
    print(f"[Khóa {i}] Base64 (PU): {base64.b64encode(ct).decode()}")
    print(f"          Giải mã lại : {decrypt_bytes(ct, pr).decode(errors='replace')}")
    sig = encrypt_bytes(data, pr)
    print(f"          Base64 (PR, xác thực): {base64.b64encode(sig).decode()}\n")

# ---------------- Bước 4: giải mã các bản mã đã cho ----------------
print("=" * 60, "\nBƯỚC 4: GIẢI MÃ CÁC BẢN MÃ\n" + "=" * 60)
ciphers = {
    "Base64 #1": b64decode_safe(
        "raUcesUlOkx/8ZhgodMoo0Uu18sC20yXlQFevSu7W/FDxIy0YRHMyXcHdD9PBvIT2aUft5fCQEGomiVVPv4I"),
    "Hex": bytes.fromhex("C87F570FC4F699CEC24020C6F54221ABAB2CE0C3"),
    "Base64 #2": b64decode_safe(
        "Z2BUSkJcg0w4XEpgm0JcMExEQmBlVH6dYEpNTHpMHptMQ7NgT"),  # dán đủ chuỗi trong đề nếu bị cắt
}

def printable(b):
    return len(b) > 0 and sum(32 <= x < 127 for x in b) / len(b) > 0.9

def try_decrypt(ct):
    """Thử mọi khóa, d/e, kích thước khối, thứ tự byte; trả về kết quả đọc được."""
    res = []
    for k in (1, 2, 3):
        (e, n), (d, _) = keys[k]
        kb = byte_len(n)
        for lab, ex in (("d (khóa riêng)", d), ("e (khóa công khai)", e)):
            for bs in sorted({kb, kb - 1, 1} - {0}):
                if bs == 1 and k != 1:
                    continue
                for cord in ("big", "little"):
                    for mord in ("big", "little"):
                        out, ok = b"", True
                        for j in range(0, len(ct), bs):
                            c = int.from_bytes(ct[j:j + bs], cord)
                            if c >= n:
                                ok = False
                                break
                            m = pow(c, ex, n)
                            out += m.to_bytes(max(1, (m.bit_length() + 7) // 8), mord)
                        if ok and printable(out):
                            res.append((k, lab, bs, cord, mord, out.decode()))
    return res

for name, ct in ciphers.items():
    print(f"\n{name} ({len(ct)} byte):")
    for k, lab, bs, cord, mord, txt in try_decrypt(ct):
        print(f"  Khóa bộ {k}, dùng {lab}, khối {bs} byte, bản mã {cord}-endian, bản rõ {mord}-endian")
        print(f"  => {txt}")