import string
from collections import Counter

ENGLISH_FREQ = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702,
    'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153,
    'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507,
    'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974,
    'z': 0.00074
}

def clean_text(text):
    return ''.join(c.lower() for c in text if c.isalpha())

def calculate_ioc(text):
    n = len(text)
    if n <= 1: return 0
    freqs = Counter(text)
    ioc = sum(f * (f - 1) for f in freqs.values()) / (n * (n - 1))
    return ioc

def estimate_key_length(text, max_len=20):
    best_len = 1
    max_ioc = 0
    
    for k in range(1, max_len + 1):
        avg_ioc = 0
        for i in range(k):
            column = text[i::k]
            avg_ioc += calculate_ioc(column)
        avg_ioc /= k
        
        if avg_ioc > max_ioc:
            max_ioc = avg_ioc
            best_len = k
            
    return best_len, max_ioc

def find_key(text, key_length):
    key = ""
    for i in range(key_length):
        column = text[i::key_length]
        best_shift = 0
        min_chi_sq = float('inf')
        
        for shift in range(26):
            chi_sq = 0
            shifted_col = [chr(((ord(c) - 97 - shift) % 26) + 97) for c in column]
            counts = Counter(shifted_col)
            n = len(shifted_col)
            
            for char, expected_prob in ENGLISH_FREQ.items():
                expected_count = expected_prob * n
                actual_count = counts.get(char, 0)
                if expected_count > 0:
                    chi_sq += ((actual_count - expected_count) ** 2) / expected_count
                    
            if chi_sq < min_chi_sq:
                min_chi_sq = chi_sq
                best_shift = shift
                
        key += chr(best_shift + 97)
    return key

def decrypt_vigenere(ciphertext, key):
    plaintext = []
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            is_upper = char.isupper()
            c_val = ord(char.lower()) - 97
            k_val = ord(key[key_idx % len(key)]) - 97
            p_val = (c_val - k_val) % 26
            p_char = chr(p_val + 97)
            plaintext.append(p_char.upper() if is_upper else p_char)
            key_idx += 1
        else:
            plaintext.append(char)
    return ''.join(plaintext)

def break_vigenere_cipher(ciphertext):
    print("[-] Cleaning ciphertext...")
    cleaned = clean_text(ciphertext)
    
    print("[-] Estimating key length (1 to 20)...")
    key_len, ioc_val = estimate_key_length(cleaned)
    print(f"[+] Key length: {key_len} (Avg IoC = {ioc_val:.4f})")
    
    print("[-] Analyzing frequency to recover key...")
    key = find_key(cleaned, key_len)
    print(f"[+] Predicted key: {key.upper()}")
    
    print("[-] Decrypting...\n")
    plaintext = decrypt_vigenere(ciphertext, key)
    return key, plaintext

if __name__ == "__main__":
    ciphertext = "pp oiuibvql avpgzwm, vyabnwzycbbg klhqla mv uqwckl kzzwktcfcwg hpp wwftwzcktakah bxjjzcynlu pyzbcgp zzht omnpxtcfckts eahkxwve uvw h uqn wy ywxy-jtzgp wiejwxubbvpe wiesgp utzvtunpfz va nztuurizf tgemizlu uh etfu fbim htq bikk va xmvprtyz. mogey lxagdgqgpufck tsialqmooe uzx buqx nhy edsxmviduxape wyg zlpqlimpqz uvw kkscbts uuavbui mhl oltuzqvhvuiv mv rdibxjv pubt wtupivf, yqv jkvyecvz vp fbm buvqlvxa czx khuhuxmgakmf khtoghqvhvuivl zwob il jtqxqm jcdx bkhpeukmpqzm igk gyuqe"
    
    key, plaintext = break_vigenere_cipher(ciphertext)
    print("=== RESULTS ===")
    print(f"KEY       : {key}")
    print(f"PLAINTEXT :\n{plaintext}")