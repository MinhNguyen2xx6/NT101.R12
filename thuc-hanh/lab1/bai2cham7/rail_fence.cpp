
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

using namespace std;

// Trả về chỉ số hàng (rail) của từng ký tự theo đường zigzag
vector<int> railPattern(size_t length, int rails) {
    vector<int> pattern(length, 0);
    if (rails < 2 || (size_t)rails >= length) return pattern;
    int rail = 0, step = 1;
    for (size_t i = 0; i < length; ++i) {
        pattern[i] = rail;
        if (rail == 0) step = 1;
        else if (rail == rails - 1) step = -1;
        rail += step;
    }
    return pattern;
}

string encrypt(const string& plain, int rails) {
    vector<int> pattern = railPattern(plain.size(), rails);
    vector<string> fence(max(rails, 1));
    for (size_t i = 0; i < plain.size(); ++i)
        fence[pattern[i]] += plain[i];
    string cipher;
    for (const string& row : fence) cipher += row;
    return cipher;
}

string decrypt(const string& cipher, int rails) {
    size_t n = cipher.size();
    vector<int> pattern = railPattern(n, rails);
    // Sắp xếp các vị trí theo (hàng, vị trí) = thứ tự đọc của bản mã
    vector<size_t> order(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(),
                [&](size_t a, size_t b) { return pattern[a] < pattern[b]; });
    string plain(n, ' ');
    for (size_t i = 0; i < n; ++i) plain[order[i]] = cipher[i];
    return plain;
}

void showFence(const string& text, int rails) {
    vector<int> pattern = railPattern(text.size(), rails);
    for (int r = 0; r < rails; ++r) {
        for (size_t i = 0; i < text.size(); ++i) {
            cout << (pattern[i] == r ? (text[i] == ' ' ? '_' : text[i]) : '.');
            if (i + 1 < text.size()) cout << ' ';
        }
        cout << '\n';
    }
}

int main() {
    // ---- Ví dụ 1: đoạn văn bản mẫu, k = 3 ----
    string msg = "TRUONG DAI HOC UIT KHOA MANG MAY TINH VA TRUYENTHONG";
    int k = 3;
    cout << "Ban ro   : " << msg << '\n';
    cout << "So hang  : " << k << '\n';
    cout << "So do zigzag:\n";
    showFence(msg, k);
    string c = encrypt(msg, k);
    string d = decrypt(c, k);
    cout << "Ban ma   : " << c << '\n';
    cout << "Giai ma  : " << d << '\n';
    cout << "Dung?    : " << (d == msg ? "true" : "false") << "\n\n";

    // ---- Ví dụ 2: cùng văn bản, thử các khóa k = 2..5 ----
    cout << string(50, '-') << '\n';
    string msg2 = msg;
    for (int r = 2; r <= 5; ++r) {
        string c2 = encrypt(msg2, r);
        string d2 = decrypt(c2, r);
        cout << "k=" << r << ": " << c2 << "\n     -> " << d2 << "  ["
             << (d2 == msg2 ? "OK" : "LOI") << "]\n";
    }

    // ---- Kiểm thử ngẫu nhiên ----
    mt19937 rng(12345);
    for (int t = 0; t < 1000; ++t) {
        int len = 1 + rng() % 60;
        string s;
        for (int i = 0; i < len; ++i) s += (char)(32 + rng() % 95);
        int kk = 2 + rng() % 9;
        if (decrypt(encrypt(s, kk), kk) != s) {
            cout << "LOI tai phep thu " << t << '\n';
            return EXIT_FAILURE;
        }
    }
    cout << "\nKiem thu ngau nhien 1000 truong hop: DAT\n";
    return 0;
}