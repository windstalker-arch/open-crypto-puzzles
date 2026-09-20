#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "bloom_filter.hpp"

class persistent_bloom : public bloom_filter {
public:
    using bloom_filter::bloom_filter;
    using bloom_filter::contains;
    using bloom_filter::insert;

    void set_state(std::size_t table_size, std::size_t salt_count,
                   unsigned long rnd, std::vector<unsigned int> salt,
                   std::vector<unsigned char> table) {
        table_size_ = table_size;
        salt_count_ = salt_count;
        random_seed_ = rnd;
        salt_ = std::move(salt);
        bit_table_ = std::move(table);
        inserted_element_count_ = 0;
    }

    std::size_t table_bytes() const { return bit_table_.size(); }
    std::size_t param_table_size() const { return table_size_; }
    unsigned long seed() const { return random_seed_; }
    const std::vector<unsigned int>& salt() const { return salt_; }
    const std::vector<unsigned char>& table() const { return bit_table_; }
};

static bool save(const persistent_bloom& f, const std::string& path) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) return false;
    const char magic[3] = {'B', 'F', '1'};
    out.write(magic, 3);
    unsigned long long ts = f.param_table_size();
    out.write(reinterpret_cast<const char*>(&ts), 8);
    unsigned int sc = static_cast<unsigned int>(f.salt().size());
    out.write(reinterpret_cast<const char*>(&sc), 4);
    unsigned long rnd = f.seed();
    out.write(reinterpret_cast<const char*>(&rnd), sizeof(rnd));
    const std::vector<unsigned int>& salt = f.salt();
    for (unsigned int s : salt) out.write(reinterpret_cast<const char*>(&s), 4);
    const std::vector<unsigned char>& table = f.table();
    out.write(reinterpret_cast<const char*>(table.data()),
              static_cast<std::streamsize>(table.size()));
    return (bool)out;
}

static bool load(const std::string& path, persistent_bloom& f) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;
    char magic[3] = {0, 0, 0};
    in.read(magic, 3);
    if (std::strncmp(magic, "BF1", 3) != 0) return false;
    unsigned long long ts = 0;
    in.read(reinterpret_cast<char*>(&ts), 8);
    unsigned int sc = 0;
    in.read(reinterpret_cast<char*>(&sc), 4);
    unsigned long rnd = 0;
    in.read(reinterpret_cast<char*>(&rnd), sizeof(rnd));
    std::vector<unsigned int> salt;
    salt.reserve(sc);
    for (unsigned int i = 0; i < sc; ++i) {
        unsigned int s = 0;
        in.read(reinterpret_cast<char*>(&s), 4);
        salt.push_back(s);
    }
    std::size_t nbytes = static_cast<std::size_t>(ts / 8);
    std::vector<unsigned char> table(nbytes);
    in.read(reinterpret_cast<char*>(table.data()), static_cast<std::streamsize>(nbytes));
    if (!in) return false;
    f.set_state(static_cast<std::size_t>(ts), sc, rnd, std::move(salt), std::move(table));
    return true;
}

static void usage() {
    std::cerr
        << "usage: bloom_dedup FILTER_PATH [--projected N] [--fp P] [--seed S] [--check]\n"
        << "  reads candidate strings (one per line) from stdin\n"
        << "  default: prints only unseen lines, inserts them into FILTER_PATH\n"
        << "  --check: writes [dup] or [new] per line to stdout, mutates nothing\n"
        << "  --projected N: expected element count (default 5000000)\n"
        << "  --fp P: max false positive probability 0<P<1 (default 0.000001)\n"
        << "  --seed S: randomizer seed (default 0xA5A5A5A5)\n";
}

int main(int argc, char* argv[]) {
    std::string path;
    std::size_t projected = 5000000;
    double fp = 0.000001;
    unsigned int seed = 0xA5A5A5A5;
    bool check = false;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--projected" && i + 1 < argc) projected = std::stoull(argv[++i]);
        else if (a == "--fp" && i + 1 < argc) fp = std::stod(argv[++i]);
        else if (a == "--seed" && i + 1 < argc) seed = static_cast<unsigned int>(std::stoul(argv[++i]));
        else if (a == "--check") check = true;
        else path = a;
    }
    if (path.empty()) { usage(); return 2; }

    bloom_parameters params;
    params.projected_element_count = projected;
    params.false_positive_probability = fp;
    params.random_seed = seed;
    if (!params) { std::cerr << "invalid bloom parameters\n"; return 2; }
    params.compute_optimal_parameters();

    persistent_bloom filter(params);
    bool loaded = load(path, filter);

    std::string line;
    std::size_t seen = 0, inserted = 0;
    while (std::getline(std::cin, line)) {
        if (line.empty() && std::cin.eof()) break;
        if (check) {
            std::cout << (filter.contains(line) ? "[dup]" : "[new]") << "\t" << line << "\n";
            continue;
        }
        if (!filter.contains(line)) {
            std::cout << line << "\n";
            filter.insert(line);
            ++inserted;
        }
        ++seen;
    }

    if (!check) {
        if (!save(filter, path)) { std::cerr << "write failed: " << path << "\n"; return 3; }
        std::cerr << (loaded ? "loaded " : "created ") << filter.table_bytes()
                  << "B filter; lines=" << seen << " new=" << inserted
                  << " fps=" << params.false_positive_probability << "\n";
    }
    return 0;
}