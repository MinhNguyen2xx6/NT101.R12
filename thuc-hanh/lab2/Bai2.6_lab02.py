#!/usr/bin/env python3
"""Lab 02 - Task 2.6: primes, GCD and modular exponentiation (Tkinter GUI)."""
import random
import tkinter as tk
from tkinter import ttk, messagebox

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
MERSENNE_10 = 2 ** 89 - 1          # 10th Mersenne prime
DETERMINISTIC_LIMIT = 3_317_044_064_679_887_385_961_981


# ------------------------------------------------------------------ logic
def mod_exp(a, x, p):
    """Square-and-multiply: a^x mod p, using
    (a*b) mod n = ((a mod n)*(b mod n)) mod n."""
    result = 1
    a %= p
    while x > 0:
        if x & 1:
            result = (result * a) % p
        a = (a * a) % p
        x >>= 1
    return result


def gcd(a, b):
    """Euclidean algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def is_prime(n, rounds=40):
    """Miller-Rabin. Exact below ~3.3e24, probabilistic above."""
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    def is_witness(a):
        x = mod_exp(a, d, n)
        if x in (1, n - 1):
            return False
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return False
        return True

    bases = list(SMALL_PRIMES)
    if n >= DETERMINISTIC_LIMIT:
        bases += [random.randrange(2, n - 1) for _ in range(rounds)]
    return not any(is_witness(a) for a in bases)


def random_prime(bits):
    """Random prime with exactly `bits` bits."""
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n


def largest_primes_below(limit, count):
    found, n = [], limit - 1
    while len(found) < count:
        if is_prime(n):
            found.append(n)
        n -= 1
    return found


# ---------------------------------------------------------------- actions
def act_random_prime(v):
    bits = int(v[0])
    if bits < 2:
        raise ValueError("Bits must be at least 2.")
    p = random_prime(bits)
    return f"{bits}-bit prime:\n{p}\n\nBit length check: {p.bit_length()}"


def act_largest_primes(_):
    primes = largest_primes_below(MERSENNE_10, 10)
    lines = [f"{i:>2}. {p}" for i, p in enumerate(primes, 1)]
    return f"10 largest primes below 2^89 - 1 ({MERSENNE_10}):\n\n" + "\n".join(lines)


def act_primality(v):
    n = int(v[0])
    if n < 0 or n >= MERSENNE_10:
        raise ValueError("n must satisfy 0 <= n < 2^89 - 1.")
    exact = n < DETERMINISTIC_LIMIT
    verdict = "PRIME" if is_prime(n) else "NOT prime"
    note = "exact result" if exact else "probabilistic, error < 4^-40"
    return f"{n}\n\n=> {verdict}  ({note})"


def act_gcd(v):
    a, b = int(v[0]), int(v[1])
    return f"gcd(a, b) = {gcd(a, b)}"


def act_mod_exp(v):
    a, x, p = int(v[0]), int(v[1]), int(v[2])
    if p < 1 or x < 0:
        raise ValueError("Need p >= 1 and x >= 0.")
    r = mod_exp(a, x, p)
    return f"a^x mod p = {r}\n\nBuilt-in pow check: {pow(a, x, p)}"


# -------------------------------------------------------------------- GUI
class App(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=8)
        self.pack(fill="both", expand=True)
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.add_tab("Random prime", [("Bits (e.g. 8, 16, 64)", "64")], act_random_prime)
        self.add_tab("10 largest < M10", [], act_largest_primes,
                     hint="10 largest primes below the 10th Mersenne prime (2^89 - 1).")
        self.add_tab("Primality test", [("n (< 2^89 - 1)", "2305843009213693951")], act_primality)
        self.add_tab("GCD", [("a", "123456789012345678901234567890"),
                             ("b", "987654321098765432109876543210")], act_gcd)
        self.add_tab("Modular exponent", [("a", "7"), ("x", "40"), ("p", "19")], act_mod_exp)

    def add_tab(self, title, fields, action, hint=None):
        frame = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(frame, text=title)
        entries = []
        if hint:
            ttk.Label(frame, text=hint).grid(row=0, column=0, columnspan=2, sticky="w")
        for i, (label, default) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(frame, width=60)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky="ew", padx=6, pady=3)
            entries.append(entry)

        out = tk.Text(frame, height=14, wrap="char", font=("Courier", 10))

        def run():
            try:
                result = action([e.get().strip() for e in entries])
            except ValueError as err:
                messagebox.showerror("Invalid input", str(err) or "Please enter valid integers.")
                return
            out.config(state="normal")
            out.delete("1.0", "end")
            out.insert("1.0", result)
            out.config(state="disabled")

        row = max(len(fields), 1)
        ttk.Button(frame, text="Run", command=run).grid(row=row, column=0, columnspan=2, pady=8)
        out.grid(row=row + 1, column=0, columnspan=2, sticky="nsew")
        out.config(state="disabled")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(row + 1, weight=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lab 02 - Task 2.6: Primes, GCD, Modular Exponentiation")
    root.geometry("760x520")
    App(root)
    root.mainloop()