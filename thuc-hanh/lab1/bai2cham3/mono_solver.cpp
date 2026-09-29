
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

using namespace std;


static const string QUADGRAM_FILE = "english_quadgrams.txt";

static const string CIPHERTEXT =
    "SA LCO AWJ KJOA VN ASRJO, SA LCO AWJ LVHOA VN ASRJO, SA LCO AWJ CZJ VN LSOMVR, "
    "SA LCO AWJ CZJ VN NVVDSOWPJOO, SA LCO AWJ JFVEW VN KJDSJN, SA LCO AWJ JFVEW VN SPEHJMQDSAI, "
    "SA LCO AWJ OJCOVP VN DSZWA, SA LCO AWJ OJCOVP VN MCHGPJOO, SA LCO AWJ OFHSPZ VN WVFJ, "
    "SA LCO AWJ LSPAJH VN MJOFCSH, LJ WCM JUJHIAWSPZ KJNVHJ QO, LJ WCM PVAWSPZ KJNVHJ QO, "
    "LJ LJHJ CDD ZVSPZ MSHJEA AV WJCUJP, LJ LJHJ CDD ZVSPZ MSHJEA AWJ VAWJH LCI. "
    "AWJHJ LJHJ C GSPZ LSAW C DCHZJ YCL CPM C BQJJP LSAW C FDCSP NCEJ, VP AWJ AWHVPJ VN JPZDCPM.";

static vector<float> QG;  // 26^4 giá trị log10(P)

bool loadQuadgrams(const string& path) {
    ifstream f(path);
    if (!f) return false;
    vector<double> cnt(26 * 26 * 26 * 26, 0.0);
    double total = 0;
    string w;
    double c;
    while (f >> w >> c) {
        if (w.size() != 4) continue;
        int idx = 0;
        bool ok = true;
        for (char ch : w) {
            ch = toupper((unsigned char)ch);
            if (ch < 'A' || ch > 'Z') { ok = false; break; }
            idx = idx * 26 + (ch - 'A');
        }
        if (!ok) continue;
        cnt[idx] += c;
        total += c;
    }
    if (total <= 0) return false;
    float floorLp = (float)log10(0.01 / total);  // quadgram chưa từng gặp
    QG.assign(cnt.size(), floorLp);
    for (size_t i = 0; i < cnt.size(); i++)
        if (cnt[i] > 0) QG[i] = (float)log10(cnt[i] / total);
    return true;
}

// ------------------------------------------------------------------ Helpers
using Key = array<int, 26>;  // Key[cipherLetter] = plainLetter

double scoreText(const vector<int>& ct, const Key& key, vector<int>& buf) {
    size_t n = ct.size();
    for (size_t i = 0; i < n; i++) buf[i] = key[ct[i]];
    double s = 0;
    for (size_t i = 0; i + 3 < n; i++)
        s += QG[((buf[i] * 26 + buf[i + 1]) * 26 + buf[i + 2]) * 26 + buf[i + 3]];
    return s;
}

double indexOfCoincidence(const vector<int>& ct) {
    array<double, 26> f{};
    for (int c : ct) f[c]++;
    double N = ct.size(), sum = 0;
    for (double x : f) sum += x * (x - 1);
    return N > 1 ? sum / (N * (N - 1)) : 0;
}

Key freqInitKey(const vector<int>& ct) {
    static const string ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ";
    array<int, 26> cnt{};
    for (int c : ct) cnt[c]++;
    vector<int> idx(26);
    iota(idx.begin(), idx.end(), 0);
    stable_sort(idx.begin(), idx.end(), [&](int a, int b) { return cnt[a] > cnt[b]; });
    Key k;
    for (int r = 0; r < 26; r++) k[idx[r]] = ORDER[r] - 'A';
    return k;
}

// Hill-climbing: thử mọi cặp hoán đổi, giữ nếu điểm tăng; lặp đến khi không cải thiện.
double hillClimb(Key& key, const vector<int>& ct, vector<int>& buf, double cur) {
    bool improved = true;
    while (improved) {
        improved = false;
        for (int i = 0; i < 25; i++)
            for (int j = i + 1; j < 26; j++) {
                swap(key[i], key[j]);
                double s = scoreText(ct, key, buf);
                if (s > cur + 1e-9) { cur = s; improved = true; }
                else swap(key[i], key[j]);
            }
    }
    return cur;
}

string applyKey(const string& original, const Key& key) {
    string out;
    out.reserve(original.size());
    for (char ch : original) {
        if (isalpha((unsigned char)ch)) {
            char p = 'A' + key[toupper((unsigned char)ch) - 'A'];
            out += islower((unsigned char)ch) ? (char)tolower(p) : p;
        } else out += ch;
    }
    return out;
}

// ------------------------------------------------------------------ Main
int main(int argc, char** argv) {
    string qgPath = QUADGRAM_FILE, filePath, textArg;
    int restarts = 30, shakes = 300;
    unsigned seed = random_device{}();
    bool verbose = false;

    for (int i = 1; i < argc; i++) {
        string a = argv[i];
        auto next = [&]() -> string { return (i + 1 < argc) ? argv[++i] : ""; };
        if (a == "-q") qgPath = next();
        else if (a == "-f") filePath = next();
        else if (a == "-t") textArg = next();
        else if (a == "-r") restarts = atoi(next().c_str());
        else if (a == "-k") shakes = atoi(next().c_str());
        else if (a == "-s") seed = (unsigned)strtoul(next().c_str(), nullptr, 10);
        else if (a == "-v") verbose = true;
        else { cerr << "Tuỳ chọn không hợp lệ: " << a << "\n"; return 1; }
    }

    if (!loadQuadgrams(qgPath)) {
        cerr << "Không đọc được file quadgram: " << qgPath
             << "\n=> Hãy đặt file này cùng thư mục với chương trình (hoặc sửa QUADGRAM_FILE).\n";
        return 1;
    }

    // ---- Đọc ciphertext
    string original;
    if (!textArg.empty()) original = textArg;
    else if (!filePath.empty()) {
        ifstream f(filePath);
        if (!f) { cerr << "Không mở được file: " << filePath << "\n"; return 1; }
        stringstream ss; ss << f.rdbuf(); original = ss.str();
    } else {
        original = CIPHERTEXT;  // mặc định: dùng ciphertext nhúng sẵn trong code
    }

    // ---- Chuẩn hoá
    vector<int> ct;
    for (char ch : original)
        if (isalpha((unsigned char)ch) && toupper((unsigned char)ch) <= 'Z')
            ct.push_back(toupper((unsigned char)ch) - 'A');
    if (ct.size() < 20) {
        cerr << "Ciphertext quá ngắn (" << ct.size() << " chữ cái) - cần tối thiểu ~100 để có kết quả tin cậy.\n";
        return 1;
    }

    // ---- Thống kê ciphertext
    array<int, 26> cnt{};
    for (int c : ct) cnt[c]++;
    cout << "=== THỐNG KÊ CIPHERTEXT ===\n";
    cout << "Độ dài (sau chuẩn hoá): " << ct.size() << " chữ cái\n";
    cout << fixed << setprecision(4);
    cout << "Index of Coincidence  : " << indexOfCoincidence(ct)
         << "  (tiếng Anh ~0.0667, ngẫu nhiên ~0.0385)\n";
    {
        vector<int> idx(26);
        iota(idx.begin(), idx.end(), 0);
        sort(idx.begin(), idx.end(), [&](int a, int b) { return cnt[a] > cnt[b]; });
        cout << "Top 6 chữ cái         : ";
        for (int i = 0; i < 6; i++)
            cout << char('A' + idx[i]) << "(" << setprecision(1) << 100.0 * cnt[idx[i]] / ct.size() << "%) ";
        cout << setprecision(4) << "\n\n";
    }

    // ---- Tìm khóa
    mt19937 rng(seed);
    vector<int> buf(ct.size());
    Key bestKey{};
    double bestScore = -1e18;
    auto t0 = chrono::steady_clock::now();
    long long evalRounds = 0;

    cout << "=== QUÁ TRÌNH TÌM KHÓA (seed=" << seed << ", restarts=" << restarts
         << ", shakes/restart=" << shakes << ") ===\n";

    for (int r = 0; r < restarts; r++) {
        Key key = freqInitKey(ct);
        if (r > 0) {
            if (r % 2 == 0) shuffle(key.begin(), key.end(), rng);        // khởi tạo hoàn toàn ngẫu nhiên
            else for (int m = 0; m < 10; m++) swap(key[rng() % 26], key[rng() % 26]);  // nhiễu nhẹ quanh khởi tạo tần suất
        }
        double cur = scoreText(ct, key, buf);
        cur = hillClimb(key, ct, buf, cur);
        evalRounds++;

        // Iterated local search: nhiễu 2-3 hoán đổi rồi hill-climb lại, giữ nếu tốt hơn
        Key localBest = key;
        double localScore = cur;
        for (int s = 0; s < shakes; s++) {
            Key k2 = localBest;
            int nsw = 2 + rng() % 2;
            for (int m = 0; m < nsw; m++) swap(k2[rng() % 26], k2[rng() % 26]);
            double sc = scoreText(ct, k2, buf);
            sc = hillClimb(k2, ct, buf, sc);
            evalRounds++;
            if (sc > localScore + 1e-9) { localScore = sc; localBest = k2; }
        }

        if (verbose || localScore > bestScore)
            cout << "  restart " << setw(3) << r + 1 << "/" << restarts
                 << "  score=" << setprecision(2) << localScore
                 << (localScore > bestScore ? "   <-- tốt nhất mới" : "") << setprecision(4) << "\n";
        if (localScore > bestScore) { bestScore = localScore; bestKey = localBest; }
    }

    double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();

    // ---- Kết quả
    string plainAlpha(26, '?');  // key theo cipher A..Z
    for (int c = 0; c < 26; c++) plainAlpha[c] = cnt[c] ? 'A' + bestKey[c] : '.';
    string cipherAlpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    cout << "\n=== KẾT QUẢ ===\n";
    cout << "Cipher : " << cipherAlpha << "\n";
    cout << "Plain  : " << plainAlpha << "   ('.' = chữ không xuất hiện trong ciphertext)\n";
    cout << setprecision(2);
    cout << "Điểm quadgram (log10)   : " << bestScore << "  (trung bình "
         << bestScore / (ct.size() - 3) << " / quadgram; tiếng Anh thường ≈ -4.2 đến -4.8)\n";
    cout << "Số lượt hill-climb      : " << evalRounds << "\n";
    cout << "Thời gian               : " << secs << " s\n\n";
    cout << "=== BẢN RÕ TỐT NHẤT ===\n" << applyKey(original, bestKey) << "\n";
    return 0;
}