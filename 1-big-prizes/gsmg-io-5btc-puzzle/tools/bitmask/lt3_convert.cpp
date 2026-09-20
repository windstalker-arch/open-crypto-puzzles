// lt3_convert.cpp -- independent C++ re-implementation of the "tiny hint <3"
// positional-bitmask family (tested.md row late-70), built on the vendored
// oliora/bitmask library (tools/bitmask). Cross-checks the Python packer.
//
// For each (digit stream, value encoding) it emits every packed byte string:
//   PH|<map>|<stream>|<rev>|<lsb>|<hex>          (4 packings per pair)
//   SS|<map>|<stream>|kept|fwd|   <kept>         (token subsequence, fwd/rev)
//   SS|<map>|<stream>|kept|rev|   <reversed>
//   SS|<map>|<stream>|digits|fwd| <digit string>
//   SS|<map>|<stream>|digits|rev| <reversed>
// where the bitmask library is used for the actual byte packing step: each
// group of eight positional bits is folded into a bitmask::bitmask<bytebits>
// and the packed byte is read back from m.bits().
//
// Usage: lt3_convert <streams.txt>

#include <bitmask/bitmask.hpp>

#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <utility>
#include <vector>

namespace {

enum class bytebits : uint32_t {
    b0 = 1u << 0, b1 = 1u << 1, b2 = 1u << 2, b3 = 1u << 3,
    b4 = 1u << 4, b5 = 1u << 5, b6 = 1u << 6, b7 = 1u << 7,
    _bitmask_max_element = b7
};

using BM = ::bitmask::bitmask<bytebits>;

const int LT = 3;

void fill_map(int* m, const std::vector<std::pair<char, int>>& kv) {
    for (int i = 0; i < 26; ++i) m[i] = 9;
    for (auto& p : kv) m[static_cast<int>(p.first - 'a')] = p.second;
}

int map_bi[26], map_hex[26], map_nat[26];

int map_idx(const char* name) {
    if (std::strcmp(name, "m_bi") == 0) return 0;
    if (std::strcmp(name, "m_hex") == 0) return 1;
    return 2;
}

std::vector<int> bits_for(const std::string& toks, const int* map) {
    std::vector<int> out;
    out.reserve(toks.size());
    for (char t : toks) {
        char c = static_cast<char>(std::tolower(static_cast<unsigned char>(t)));
        out.push_back(map[static_cast<int>(c - 'a')] < LT ? 1 : 0);
    }
    return out;
}

std::string pack_hex(const std::vector<int>& bits, bool rev, bool lsb) {
    std::string hex;
    char buf[3];
    for (size_t i = 0; i < bits.size(); i += 8) {
        BM m;
        for (size_t j = 0; j < 8 && i + j < bits.size(); ++j) {
            size_t k = rev ? bits.size() - 1 - (i + j) : i + j;
            if (!bits[k]) continue;
            int pos = lsb ? static_cast<int>(j) : static_cast<int>(7 - j);
            m |= BM(static_cast<bytebits>(1u << pos));
        }
        uint8_t b = static_cast<uint8_t>(m.bits());
        std::snprintf(buf, sizeof buf, "%02x", b);
        hex += buf;
    }
    return hex;
}

void emit_pair(const char* mapname, const int* map,
               const char* stream, const std::string& toks) {
    std::vector<int> bits = bits_for(toks, map);
    for (int rev = 0; rev <= 1; ++rev)
        for (int lsb = 0; lsb <= 1; ++lsb)
            std::printf("PH|%s|%s|%d|%d|%s\n", mapname, stream,
                        rev, lsb, pack_hex(bits, rev != 0, lsb != 0).c_str());

    std::string kept, digits;
    for (char t : toks) {
        char c = static_cast<char>(std::tolower(static_cast<unsigned char>(t)));
        if (map[static_cast<int>(c - 'a')] < LT) {
            kept += t;
            digits += static_cast<char>('0' + map[static_cast<int>(c - 'a')]);
        }
    }
    std::printf("SS|%s|%s|kept|fwd|%s\n", mapname, stream, kept.c_str());
    std::printf("SS|%s|%s|kept|rev|%s\n", mapname, stream,
                std::string(kept.rbegin(), kept.rend()).c_str());
    std::printf("SS|%s|%s|digits|fwd|%s\n", mapname, stream, digits.c_str());
    std::printf("SS|%s|%s|digits|rev|%s\n", mapname, stream,
                std::string(digits.rbegin(), digits.rend()).c_str());
}

}  // namespace

int main(int argc, char** argv) {
    fill_map(map_bi, {{'d', 0}, {'b', 1}, {'i', 2}, {'f', 3}, {'h', 4},
                      {'c', 5}, {'e', 6}, {'g', 7}, {'a', 8}});
    fill_map(map_hex, {{'o', 0}, {'a', 1}, {'b', 2}, {'c', 3}, {'d', 4},
                       {'e', 5}, {'f', 6}, {'g', 7}, {'h', 8}, {'i', 9}});
    fill_map(map_nat, {{'a', 0}, {'b', 1}, {'c', 2}, {'d', 3}, {'e', 4},
                       {'f', 5}, {'g', 6}, {'h', 7}, {'i', 8}});
    const int* maps[3] = {map_bi, map_hex, map_nat};
    const char* names[3] = {"m_bi", "m_hex", "m_nat"};

    if (argc != 2) {
        std::fprintf(stderr, "usage: lt3_convert <streams.txt>\n");
        return 2;
    }
    FILE* f = std::fopen(argv[1], "r");
    if (!f) return 2;
    char line[2048];
    while (std::fgets(line, sizeof line, f)) {
        char label[64];
        char toks[1900];
        if (std::sscanf(line, "%63[^\t]\t%1899s", label, toks) != 2) continue;
        for (int i = 0; i < 3; ++i) emit_pair(names[i], maps[i], label, toks);
    }
    std::fclose(f);
    return 0;
}