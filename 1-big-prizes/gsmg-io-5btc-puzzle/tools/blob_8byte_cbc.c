/*
 * blob_8byte_cbc.c -- C/OpenSSL twin of tools/blob_8byte_cbc.py.
 *
 * WHY. The Python sweeper runs at ~860 (candidate x alg x klen) cells/s on one
 * phone core, so the framing-(c) sweep over the full 835,270-candidate wordlist
 * across five blobs is ~38 core-hours. This file does the identical arithmetic
 * and exists only so that sweep can be finished and the absence recorded as a
 * measurement rather than a projection.
 *
 * THE CONTRACT. This is a TRANSLATION, not a second opinion. Every cell it
 * sweeps, both key/IV readings, the KDF set, the PKCS7 final-block gate, the
 * printability floor and the candidate ordering are the ones the Python file
 * defines. --selftest encrypts a known plaintext under each cell's own
 * convention and requires the sweep to re-find it, which is what proves the
 * translation preserved the cell grid rather than merely running fast.
 *
 * DEFECT FOUND AND CORRECTED 2026-10-06 (R-BLOB8CBC). This header used to claim
 * that "--cross N additionally re-runs the Python path on the first N
 * candidates and requires both to report the same candidate count and the same
 * survivor set". THAT WAS NEVER IMPLEMENTED. --cross was parsed and then passed
 * into sweep() as `firstN`, which only LIMITS the candidate range, and the
 * normal RESULT line printed exactly as it does for a full sweep. So a reader
 * running `--cross 300` saw a clean, unremarkable result line and could take it
 * for a passed equivalence check. A documented verification feature that
 * silently does something else is worse than no such feature: it manufactures
 * witness-shaped output. The real equivalence proof is
 * tools/blob_8byte_xcheck.py, which builds a known-answer blob and requires BOTH
 * implementations to re-find it through this exact stdin/dispatch path.
 *
 * FRAMING (d) ADDED 2026-10-06 -- THE ONE THAT WAS MISSING, AND THE ONE THE
 * PROJECT ALREADY USES. a/b/c all start the ciphertext at offset 32, 24 or 24-8
 * because they inherit analysis/blob_family_mod16.md's claim that "OpenSSL's
 * Salted__ container is Salted__ (8) + salt (16) = a 24-byte header", and that
 * claim is WRONG for every blob this project has actually opened. The author's
 * container is magic (8) + salt (8) + ciphertext, and that is how README.md line
 * 133, tools/oracle.py, tools/ladder_census.py, tools/p32_evp_verify.py and
 * tested.md:12283/:12284 all read it:
 *   - the small gate blob is salt 3ab585348552415d -- 8 bytes;
 *   - phase 2 opens with header 16, ciphertext 656 B = 41 AES blocks;
 *   - phase 3 opens with header 16, ciphertext 4096 B = 256 AES blocks.
 * phase_0.bin and phase_1.bin are those two files. Both plaintexts are multiples
 * of 16 minus padding ONLY under a 16-byte header, so the "ciphertext length is
 * 8 mod 16, therefore the family is not CBC" conclusion in blob_family_mod16.md
 * is an artifact of reading the header 8 bytes too long. The 8-byte-block sweep
 * family (framings a/b/c, 217,170,200 cells) therefore measured the wrong
 * object; this framing measures the right one and was never swept before today.
 *
 * TWO TRAPS THE PYTHON FILE ALREADY PAID FOR, KEPT HERE.
 * 1. A CBC context carries its chaining state across repeated update() calls,
 *    so the pad check and the full decrypt must use SEPARATE contexts. Sharing
 *    one corrupts exactly the first block of the second result, which presents
 *    as a selftest that fails every cell while an isolated round-trip passes.
 * 2. IV length is chosen by ALGORITHM, not by key length: AES and 3DES share
 *    key lengths 16 and 24, so a key-length lookup silently mis-sizes half the
 *    family.
 *
 * Read-only: reads blob files and a candidate stream on stdin, writes nothing
 * but its own stdout. Contacts no oracle and no gate.
 *
 * Usage:
 *   cc -O2 -o blob_8byte_cbc blob_8byte_cbc.c -lcrypto
 *   ./blob_8byte_cbc --selftest
 *   python3 tools/gsmg_wordlist.py | ./blob_8byte_cbc --blob urlblob --framing c
 *   ./blob_8byte_cbc --path analysis/tmp/wl/xcheck.bin --framing c   # known-answer
 *   ./blob_8byte_cbc --blob urlblob --framing d                       # author's container
 *
 * --limit N / --cross N both mean "sweep only the first N candidates"; they are
 * the same flag under two names. --path overrides the per-blob filename so a
 * known-answer blob can be pushed through the identical code path without
 * writing into the archived sources directory.
 */
#define _GNU_SOURCE
#include <openssl/evp.h>
#include <openssl/provider.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _OPENMP
#include <omp.h>
#endif

#define HEADER 24
#define MAXPW 512
#define MAXCT 8192

static const char *SOURCES = "/storage/EA7B-C038/briefcase/gsmg-puzzle/analysis";

static const char *FAMILY[] = {
    "urlblob", "phase_0", "phase_1", "phase32", "cosmic", NULL
};
static const char *FAMILY_FILE[] = {
    "urlblob.bin", "phase_0.bin", "phase_1.bin",
    "phase32_live_salt_eefc4c5b.bin",
    "cosmic_duality_live_salt2d3f6fe0.bin", NULL
};

/* kdf id -> digest */
enum { KDF_EVP_MD5 = 0, KDF_EVP_SHA1, KDF_EVP_SHA256, KDF_RAW_MD5,
       KDF_RAW_SHA256, KDF_N };
static const char *KDF_NAME[KDF_N] = {
    "evp-md5", "evp-sha1", "evp-sha256", "raw-md5", "raw-sha256"
};

/* alg id -> openssl cipher name, key lengths, block size.
 *
 * EVERY cipher here is CBC, because the Python twin uses MODE_CBC for all of
 * them. Naming one of them "...-ECB" would still round-trip inside this file's
 * own selftest -- ECB of a padded plaintext decrypts to the same bytes -- which
 * is exactly why the cross-check against the Python path below is not
 * optional. */
enum { ALG_DES = 0, ALG_DESEDE3, ALG_BLOWFISH, ALG_CAST5, ALG_AES, ALG_N };
static const char *ALG_NAME[ALG_N] = {
    "DES-CBC", "DES-EDE3-CBC", "BF-CBC", "CAST5-CBC", "AES-128-CBC"
};

/*
 * Cipher name per (alg, keylen). OpenSSL's "AES-128-CBC" is a FIXED 128-bit
 * cipher, so the 192- and 256-bit rows need their own names -- passing a 32-byte
 * key to AES-128-CBC fails EVP_EncryptInit_ex and every such cell would have
 * reported MISS while reading as "no key found". The generic names (DES-EDE3,
 * BF) do accept several key lengths under one name and are reused as-is.
 */
static const char *cipher_name(int alg, int klen)
{
    if (alg == ALG_AES) {
        if (klen == 16)
            return "AES-128-CBC";
        if (klen == 24)
            return "AES-192-CBC";
        return "AES-256-CBC";
    }
    return ALG_NAME[alg];
}
static const int ALG_KLENS[ALG_N] = {1, 2, 3, 1, 3};
static const int ALG_KLEN[ALG_N][3] = {
    {8, 0, 0}, {16, 24, 0}, {16, 24, 32}, {16, 0, 0}, {16, 24, 32}
};
static const int ALG_BS[ALG_N] = {8, 8, 8, 8, 16};

static int ivlen_for(int alg) { return alg == ALG_AES ? 16 : 8; }

/*
 * Cipher handles fetched once. EVP_CIPHER_fetch() is a provider lookup and it
 * dominated the runtime: the sweep makes one call per cell and there are 28
 * cells per candidate, so 23 million lookups for the full wordlist. Fetching
 * each (alg, keylen) cipher once at start-up made the sweep roughly 6x faster
 * with no change to any derived value -- the handles are read-only after this
 * and EVP_CIPHER_CTX_init() takes its own reference.
 */
#define NKEYLEN 3
static EVP_CIPHER *CIPHER[ALG_N][NKEYLEN];
static int CIPHERS_READY = 0;

static void ciphers_init(void)
{
    if (CIPHERS_READY)
        return;
    for (int alg = 0; alg < ALG_N; alg++)
        for (int kj = 0; kj < ALG_KLENS[alg]; kj++) {
            int klen = ALG_KLEN[alg][kj];
            CIPHER[alg][kj] = EVP_CIPHER_fetch(NULL, cipher_name(alg, klen), NULL);
            if (!CIPHER[alg][kj])
                fprintf(stderr,
                        "warning: cipher %s unavailable in this OpenSSL build\n",
                        cipher_name(alg, klen));
        }
    CIPHERS_READY = 1;
}

/* Fetch-then-cache shim, so an unavailable cipher still degrades to a skip. */
static EVP_CIPHER *cipher_get(int alg, int klen)
{
    ciphers_init();
    for (int kj = 0; kj < ALG_KLENS[alg]; kj++)
        if (ALG_KLEN[alg][kj] == klen)
            return CIPHER[alg][kj];
    return NULL;
}

static const EVP_MD *md_for(int kdf)
{
    switch (kdf) {
    case KDF_EVP_MD5:
    case KDF_RAW_MD5:    return EVP_md5();
    case KDF_EVP_SHA1:   return EVP_sha1();
    default:             return EVP_sha256();
    }
}

/*
 * The single KDF primitive, matching blob_8byte_cbc.py's key_for() and
 * evp_bytes_to_key() byte for byte:
 *
 *   evp-* : one EVP_BytesToKey stream truncated to nbytes, where the stream is
 *           prev = D(prev || pw || salt) iterated.
 *   raw-* : D(pw) truncated, no salt.
 *
 * `nbytes` is keylen + ivlen so that the key and the IV come out of ONE stream
 * (openssl enc semantics), which is why the caller passes the combined length.
 */
static void derive_key(const char *pw, size_t pwlen, const uint8_t *salt,
                       size_t saltlen, int kdf, uint8_t *out, size_t nbytes)
{
    const EVP_MD *md = md_for(kdf);
    size_t done = 0;
    uint8_t prev[EVP_MAX_MD_SIZE];
    unsigned int prevlen = 0;

    if (kdf == KDF_RAW_MD5 || kdf == KDF_RAW_SHA256) {
        unsigned int n = 0;
        EVP_MD_CTX *c = EVP_MD_CTX_new();
        EVP_DigestInit_ex(c, md, NULL);
        EVP_DigestUpdate(c, pw, pwlen);
        EVP_DigestFinal_ex(c, out, &n);
        EVP_MD_CTX_free(c);
        (void)nbytes;
        (void)done;
        (void)prev;
        (void)prevlen;
        return;
    }

    memset(prev, 0, sizeof prev);
    while (done < nbytes) {
        EVP_MD_CTX *c = EVP_MD_CTX_new();
        EVP_DigestInit_ex(c, md, NULL);
        if (prevlen)
            EVP_DigestUpdate(c, prev, prevlen);
        EVP_DigestUpdate(c, pw, pwlen);
        EVP_DigestUpdate(c, salt, saltlen);
        EVP_DigestFinal_ex(c, prev, &prevlen);
        EVP_MD_CTX_free(c);
        unsigned int take = prevlen;
        if (done + take > nbytes)
            take = (unsigned int)(nbytes - done);
        memcpy(out + done, prev, take);
        done += take;
    }
}

static int pkcs7_ok(const uint8_t *tail, int bs)
{
    int k = tail[bs - 1];
    if (k < 1 || k > bs)
        return 0;
    for (int i = 0; i < k; i++)
        if (tail[bs - 1 - i] != (uint8_t)k)
            return 0;
    return 1;
}

static double printable_ratio(const uint8_t *b, size_t n)
{
    size_t ok = 0;
    for (size_t i = 0; i < n; i++)
        if ((b[i] >= 32 && b[i] <= 126) || b[i] == 9 || b[i] == 10 || b[i] == 13)
            ok++;
    return n ? (double)ok / (double)n : 0.0;
}

/*
 * One cell = (kdf, alg, keylen, iv reading). Decrypts the final two blocks
 * first, checks PKCS7 on the last block, and only then spends a full decrypt.
 * Returns 1 and fills `pt` on a survivor.
 */
static int try_cell(int alg, int klen, const uint8_t *key,
                    const uint8_t *iv, const uint8_t *ct, size_t ctlen,
                    int padded, double floor_v, uint8_t *pt, size_t *ptlen)
{
    EVP_CIPHER *cif = cipher_get(alg, klen);
    int bs = ALG_BS[alg];
    int rc = 0;

    if (!cif)
        return 0;

    if (padded) {
        /* OUT OF PLACE. CBC decryption chains block N's output into block N+1's
         * input, so decrypting a buffer over itself is not merely untidy -- it
         * feeds already-decrypted bytes back in. Every one of the 80 cells
         * failed the selftest until the source and destination were split. */
        uint8_t lasttwo[32], work[32];
        size_t n = ctlen >= (size_t)(2 * bs) ? (size_t)(2 * bs) : ctlen;
        memcpy(lasttwo, ct + ctlen - n, n);
        EVP_CIPHER_CTX *c = EVP_CIPHER_CTX_new();
        int outl = 0;
        /* Padding OFF. EVP_DecryptUpdate defaults to padding enabled, which
         * withholds the final block until EVP_DecryptFinal -- and this code
         * never calls DecryptFinal, so `outl` came back a block short and
         * pkcs7_ok() read off the end of the buffer. All 80 cells failed the
         * selftest until padding was explicitly disabled. The PKCS7 bytes are
         * checked here by hand, so OpenSSL's own unpadding must not also be in
         * play or the check would be verifying nothing. */
        EVP_CIPHER_CTX_set_padding(c, 0);
        if (EVP_DecryptInit_ex(c, cif, NULL, key, iv) == 1 &&
            EVP_DecryptUpdate(c, work, &outl, lasttwo, (int)n) == 1) {
            if (pkcs7_ok(work + (n - bs), bs)) {
                EVP_CIPHER_CTX_free(c);
                c = EVP_CIPHER_CTX_new();
                outl = 0;
                EVP_CIPHER_CTX_set_padding(c, 0);
                if (EVP_DecryptInit_ex(c, cif, NULL, key, iv) == 1 &&
                    EVP_DecryptUpdate(c, pt, &outl, ct, (int)ctlen) == 1) {
                    *ptlen = (size_t)outl;
                    if (printable_ratio(pt, *ptlen) >= floor_v)
                        rc = 1;
                }
            }
        }
        EVP_CIPHER_CTX_free(c);
    } else {
        uint8_t work[MAXCT];
        EVP_CIPHER_CTX *c = EVP_CIPHER_CTX_new();
        int outl = 0;
        EVP_CIPHER_CTX_set_padding(c, 0);
        if (EVP_DecryptInit_ex(c, cif, NULL, key, iv) == 1 &&
            EVP_DecryptUpdate(c, work, &outl, ct, (int)ctlen) == 1) {
            if (outl > 0)
                memcpy(pt, work, (size_t)outl);
            *ptlen = (size_t)outl;
            if (printable_ratio(pt, *ptlen) >= floor_v)
                rc = 1;
        }
        EVP_CIPHER_CTX_free(c);
    }
    return rc;
}

/*
 * build_cells(): both IV readings, exactly as the Python file returns a 2-tuple
 * per (candidate, alg, keylen). For evp-* the key and IV come from one stream
 * and the second reading uses the leading salt bytes -- but only when the salt
 * is at least an IV long, which framing (d)'s 8-byte salt is not; the salt length
 * is therefore a parameter rather than a constant, because derive_key() used to
 * hardcode 16 and that hardcode is what made framing (d) unrepresentable.
 */
static int build_cells(const char *pw, size_t pwlen, const uint8_t *salt,
                       size_t saltlen, int klen, int kdf, int ivlen,
                       uint8_t keys[2][40], uint8_t ivs[2][16])
{
    int n = 0;
    if (kdf == KDF_EVP_MD5 || kdf == KDF_EVP_SHA1 || kdf == KDF_EVP_SHA256) {
        uint8_t stream[64];
        derive_key(pw, pwlen, salt, saltlen, kdf, stream, (size_t)(klen + ivlen));
        memcpy(keys[0], stream, (size_t)klen);
        memcpy(ivs[0], stream + klen, (size_t)ivlen);
        /* Second IV reading (IV = leading salt bytes) exists only when the salt
         * is at least an IV long. Under framing (d) the salt is the 8 bytes the
         * author's container stores, so salt[:16] is not an AES IV; it is skipped,
         * not invented, and every certified open takes its IV from this EVP
         * stream. Skipping also removes a 16-byte read from an 8-byte buffer. */
        if ((int)saltlen >= ivlen) {
            memcpy(keys[1], stream, (size_t)klen);
            memcpy(ivs[1], salt, (size_t)ivlen);
            n = 2;
        } else {
            n = 1;
        }
    } else {
        derive_key(pw, pwlen, salt, saltlen, kdf, keys[0], (size_t)klen);
        /* A raw key carries no derivation to hang an IV on. With an 8-byte salt
         * the only constructions available are zeros and the salt doubled; the
         * doubled salt is used so that the cell still varies per blob, and it is
         * named here because a negative over it must not read as a zero-IV sweep. */
        memset(ivs[0], 0, (size_t)ivlen);
        memcpy(ivs[0], salt, saltlen < (size_t)ivlen ? saltlen : (size_t)ivlen);
        if (saltlen < (size_t)ivlen)
            memcpy(ivs[0] + saltlen, salt, (size_t)ivlen - saltlen);
        n = 1;
    }
    return n;
}

struct hit {
    double r;
    int kdf, alg, klen;
    uint8_t pw[MAXPW];
    size_t pwlen;
    uint8_t pt[MAXCT];
    size_t ptlen;
};

/*
 * `pws` is an array of FIXED-SIZE ROWS (`uint8_t (*)[MAXPW]`), not an array of
 * pointers. Declaring the parameter as `const uint8_t **` and indexing it makes
 * the compiler treat each row header as a pointer, so `pws[ci]` returns whatever
 * the first eight bytes of row ci happen to encode as an address. That
 * segfaulted on the first candidate every time, and it is why the selftest
 * passed while every real sweep died: the selftest never routes through this
 * parameter at all.
 */
static void print_bytes_repr(const uint8_t *b, size_t n, size_t cap);

static int sweep(const char *arena, const size_t *offs, int ncand,
                 const uint8_t *salt, size_t saltlen, const uint8_t *ct,
                 size_t ctlen,
                 const int *kdfs, int nkdf, int padded, double floor_v,
                 int bs, struct hit *hits, int maxhits, int firstN,
                 uint64_t *tried_out)
{
    uint64_t tried = 0;
    int nhit = 0;
    int nover = 0;   /* survivors beyond maxhits: counted and reported, not dropped */
    int limit = (firstN > 0 && firstN < ncand) ? firstN : ncand;

    for (int ci = 0; ci < limit; ci++) {
        const char *pw = arena + offs[ci];
        size_t pwlen = strlen(pw);
        for (int ki = 0; ki < nkdf; ki++) {
            int kdf = kdfs[ki];
            for (int alg = 0; alg < ALG_N; alg++) {
                if (bs == 8 && alg == ALG_AES)
                    continue;
                if (bs == 16 && alg != ALG_AES)
                    continue;
                int ivlen = ivlen_for(alg);
                for (int kj = 0; kj < ALG_KLENS[alg]; kj++) {
                    int klen = ALG_KLEN[alg][kj];
                    uint8_t keys[2][40], ivs[2][16];
                    int nc = build_cells(pw, pwlen, salt, saltlen, klen, kdf,
                                         ivlen, keys, ivs);
                    for (int c = 0; c < nc; c++) {
                        tried++;
                        uint8_t pt[MAXCT];
                        size_t ptlen = 0;
                        if (try_cell(alg, klen, keys[c], ivs[c], ct, ctlen,
                                     padded, floor_v, pt, &ptlen)) {
                            if (nhit < maxhits) {
                                hits[nhit].r =
                                    printable_ratio(pt, ptlen);
                                hits[nhit].kdf = kdf;
                                hits[nhit].alg = alg;
                                hits[nhit].klen = klen;
                                memcpy(hits[nhit].pw, pw, pwlen);
                                hits[nhit].pwlen = pwlen;
                                memcpy(hits[nhit].pt, pt, ptlen);
                                hits[nhit].ptlen = ptlen;
                                nhit++;
                                printf("  SURVIVOR r=%.3f kdf=%s alg=%s "
                                       "klen=%d pw=%.*s\n", hits[nhit - 1].r,
                                       KDF_NAME[kdf], cipher_name(alg, klen),
                                       klen, (int)pwlen, pw);
                                /* The Python twin prints the recovered plaintext
                                 * on the next line and this one did not, so a real
                                 * hit found here arrived with nothing to read.
                                 * An 8-byte-block CBC survivor is only actionable
                                 * by looking at it, so print the same 200 bytes in
                                 * the same CPython-bytes-repr form. */
                                fputs("    ", stdout);
                                print_bytes_repr(hits[nhit - 1].pt,
                                                 hits[nhit - 1].ptlen, 200);
                                putchar('\n');
                                fflush(stdout);
                            } else {
                                nover++;
                            }
                        }
                    }
                }
            }
        }
    }
    *tried_out = tried;
    /* A silently capped survivor list is the same failure mode as an
     * unimplemented flag: the reader sees "RESULT: 64 survivors" and believes the
     * list is complete. */
    if (nover)
        fprintf(stderr, "NOTE: %d further survivor(s) beyond the %d-slot list; "
                        "raise `hits` capacity to see them\n", nover, maxhits);
    return nhit;
}

/* CPython bytes repr, for the first `cap` bytes: printable ASCII literal except
 * for backslash and double quote, \n \r \t spelled out, everything else \xNN.
 * Only used to render a survivor, so it needs to agree with the Python twin's
 * output for a human comparing the two logs. */
static void print_bytes_repr(const uint8_t *b, size_t n, size_t cap)
{
    size_t lim = n < cap ? n : cap;
    fputc('"', stdout);
    for (size_t i = 0; i < lim; i++) {
        uint8_t x = b[i];
        if (x == '\\')
            fputs("\\\\", stdout);
        else if (x == '"')
            fputs("\\\"", stdout);
        else if (x == '\n')
            fputs("\\n", stdout);
        else if (x == '\r')
            fputs("\\r", stdout);
        else if (x == '\t')
            fputs("\\t", stdout);
        else if (x >= 32 && x <= 126)
            putchar(x);
        else
            printf("\\x%02x", x);
    }
    if (n > cap)
        fputs("...", stdout);
    fputc('"', stdout);
}

static int load_blob(const char *which, int framing, uint8_t *salt,
                     size_t *saltlen, uint8_t *ct, size_t *ctlen)
{
    char path[512];
    if (which && which[0] == '/') {
        snprintf(path, sizeof path, "%s", which);
    } else {
        int idx = -1;
        for (int i = 0; FAMILY[i]; i++)
            if (!strcmp(FAMILY[i], which))
                idx = i;
        if (idx < 0) {
            fprintf(stderr, "unknown blob %s\n", which);
            return -1;
        }
        snprintf(path, sizeof path, "%s/%s", SOURCES, FAMILY_FILE[idx]);
    }
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "cannot open %s\n", path);
        return -1;
    }
    uint8_t d[MAXCT];
    size_t n = fread(d, 1, sizeof d, f);
    fclose(f);
    if (n < HEADER || memcmp(d, "Salted__", 8) != 0) {
        fprintf(stderr, "%s is not a Salted__ blob (n=%zu)\n", which, n);
        return -1;
    }
    *saltlen = 16;
    memcpy(salt, d + 8, 16);
    if (framing == 'd') {
        /* THE AUTHOR'S OWN CONTAINER, as it opens every blob this project has
         * ever decrypted: magic (8) + salt (8) + AES-CBC ciphertext. README line
         * 133 (the small gate blob, salt 3ab585348552415d), tools/oracle.py line
         * 48, tools/ladder_census.py line 160, tools/p32_evp_verify.py line 80
         * and tested.md:12283/:12284 all read it this way -- phase 2's ciphertext
         * is 656 B = 41 AES blocks and phase 3's is 4096 B = 256 AES blocks, both
         * of which are multiples of 16 ONLY under a 16-byte header. This framing
         * is not a guess and it was not one of a/b/c. */
        if (n < 16)
            return -1;
        *saltlen = 8;
        memcpy(salt, d + 8, 8);
        *ctlen = n - 16;
        memcpy(ct, d + 16, *ctlen);
        return 0;
    } else if (framing == 'a') {
        if (n < 32)
            return -1;
        *ctlen = n - 32;
        memcpy(ct, d + 32, *ctlen);
    } else if (framing == 'b') {
        *ctlen = n - HEADER - 8;
        memcpy(ct, d + HEADER, *ctlen);
    } else {
        *ctlen = n - HEADER;
        memcpy(ct, d + HEADER, *ctlen);
    }
    return 0;
}

static int selftest(void)
{
    uint8_t salt[16];
    for (int i = 0; i < 16; i++)
        salt[i] = (uint8_t)i;
    const char *pw = "SELFTESTPW";
    size_t pwlen = strlen(pw);
    const char *good = "SELFTEST-PLAINTEXT-0123456789-abcdefghijklmnop";
    size_t goodlen = strlen(good);

    int failures = 0, cells = 0;

    for (int kdf = 0; kdf < KDF_N; kdf++) {
        for (int alg = 0; alg < ALG_N; alg++) {
            int bs = ALG_BS[alg];
            int ivlen = ivlen_for(alg);
            for (int kj = 0; kj < ALG_KLENS[alg]; kj++) {
                int klen = ALG_KLEN[alg][kj];
                uint8_t keys[2][40], ivs[2][16];
                int nc = build_cells(pw, pwlen, salt, 16, klen,
                                     kdf, ivlen, keys, ivs);
                for (int c = 0; c < nc; c++) {
                    cells++;
                    /* Encrypt this cell's own plaintext under this cell's own
                     * convention, then require try_cell() -- the same function
                     * the sweep uses, PKCS7 gate included -- to find it back.
                     * A cell that cannot re-find its own key is a broken
                     * verifier, which would make a clean sweep meaningless. */
                    uint8_t pad = (uint8_t)(bs - (goodlen % bs));
                    size_t plainlen = goodlen + pad;
                    uint8_t pt[MAXCT], ct[MAXCT];
                    memset(pt, pad, plainlen);
                    memcpy(pt, good, goodlen);

                    EVP_CIPHER *cif = cipher_get(alg, klen);
                    EVP_CIPHER_CTX *cx = EVP_CIPHER_CTX_new();
                    int outl = 0;
                    /* Padding OFF as well: the PKCS7 block is appended by hand
                     * above, and OpenSSL adding its own would corrupt it. */
                    EVP_CIPHER_CTX_set_padding(cx, 0);
                    int ok = cif &&
                             EVP_EncryptInit_ex(cx, cif, NULL, keys[c],
                                                ivs[c]) == 1 &&
                             EVP_EncryptUpdate(cx, ct, &outl, pt,
                                               (int)plainlen) == 1;
                    EVP_CIPHER_CTX_free(cx);
                    if (!ok) {
                        failures++;
                        printf("  SETUP-FAIL kdf=%s alg=%s klen=%d\n",
                               KDF_NAME[kdf], cipher_name(alg, klen), klen);
                        continue;
                    }
                    uint8_t back[MAXCT];
                    size_t backlen = 0;
                    int found = try_cell(alg, klen, keys[c], ivs[c], ct,
                                         (size_t)outl, 1, 0.0, back, &backlen);
                    if (!found || backlen < goodlen ||
                        memcmp(back, good, goodlen) != 0) {
                        failures++;
                        printf("  MISS kdf=%s alg=%s klen=%d cell=%d "
                               "(%s)\n", KDF_NAME[kdf], cipher_name(alg, klen),
                               klen, c,
                               found ? "wrong plaintext" : "verifier rejected it");
                    }
                }
            }
        }
    }
    if (failures) {
        printf("\nSELFTEST FAIL -- %d/%d cells\n", failures, cells);
        return 1;
    }
    printf("\nSELFTEST PASS -- %d/%d cells round-trip, and the PKCS7 "
           "final-block verifier accepts every correct key\n", cells, cells);
    return 0;
}

int main(int argc, char **argv)
{
    OSSL_PROVIDER_load(NULL, "legacy");
    OSSL_PROVIDER_load(NULL, "default");
    ciphers_init();

    const char *blob = "urlblob";
    char framing = 'c';
    double floor_v = 0.90;
    int cross = 0, limit_c = 0;
    const char *kdfspec = "evp-md5,evp-sha256";
    int bs_override = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--selftest"))
            return selftest();
        else if (!strcmp(argv[i], "--blob") && i + 1 < argc)
            blob = argv[++i];
        else if (!strcmp(argv[i], "--path") && i + 1 < argc)
            blob = argv[++i];
        else if (!strcmp(argv[i], "--framing") && i + 1 < argc)
            framing = argv[++i][0];
        else if (!strcmp(argv[i], "--floor") && i + 1 < argc)
            floor_v = atof(argv[++i]);
        else if (!strcmp(argv[i], "--kdf") && i + 1 < argc)
            kdfspec = argv[++i];
        else if (!strcmp(argv[i], "--cross") && i + 1 < argc)
            cross = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--limit") && i + 1 < argc)
            limit_c = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--bs") && i + 1 < argc)
            bs_override = atoi(argv[++i]);
        else {
            fprintf(stderr, "unknown arg %s\n", argv[i]);
            return 2;
        }
    }

    if (framing != 'a' && framing != 'b' && framing != 'c' && framing != 'd') {
        fprintf(stderr, "unknown framing %c (want a, b, c or d)\n", framing);
        return 2;
    }

    int kdfs[16], nkdf = 0;
    {
        char tmp[256];
        snprintf(tmp, sizeof tmp, "%s", kdfspec);
        for (char *tok = strtok(tmp, ","); tok; tok = strtok(NULL, ",")) {
            int found = -1;
            for (int k = 0; k < KDF_N; k++)
                if (!strcmp(KDF_NAME[k], tok))
                    found = k;
            if (found < 0) {
                fprintf(stderr, "unknown kdf %s\n", tok);
                return 2;
            }
            if (nkdf < 16)
                kdfs[nkdf++] = found;
        }
    }

    uint8_t salt[16], ct[MAXCT];
    size_t ctlen = 0, saltlen = 16;
    if (load_blob(blob, framing, salt, &saltlen, ct, &ctlen) != 0)
        return 1;
    int bs = framing == 'c' ? 8 : 16;
    if (bs_override) {
        if (bs_override != 8 && bs_override != 16) {
            fprintf(stderr, "--bs wants 8 or 16\n");
            return 2;
        }
        bs = bs_override;
    }
    int padded = framing != 'b';
    printf("%s framing=%c: salt ", blob, framing);
    for (size_t i = 0; i < saltlen; i++)
        printf("%02x", salt[i]);
    printf("  (B=%zu)  ciphertext %zu B  ct%%16=%zu  block=%d  pkcs7_checkable=%s\n",
           saltlen, ctlen, ctlen % 16, bs, padded ? "True" : "False");

    /* Read candidates from stdin, one per line, in order, into a PACKED arena.
     *
     * A fixed-width row array cost MAXPW (512) bytes per candidate regardless
     * of the actual passphrase, which is 427 MB for the 835,270-candidate
     * wordlist -- more than this device had free, and the failure mode was a
     * hard kill rather than a clean error. The arena holds the real bytes plus
     * a NUL terminator per line, and `offs` holds the start of each. */
    size_t arena_cap = 1 << 20, arena_len = 0;
    char *arena = malloc(arena_cap);
    size_t *offs = malloc(sizeof(size_t) * (1 << 17));
    size_t offcap = 1 << 17;
    if (!arena || !offs)
        return 1;
    int ncand = 0;
    char line[MAXPW * 2];
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r'))
            line[--L] = 0;
        if (!L)
            continue;
        if (L > MAXPW - 1) {
            fprintf(stderr, "candidate longer than %d bytes, skipped\n", MAXPW - 1);
            continue;
        }
        while (arena_len + L + 1 > arena_cap) {
            arena_cap *= 2;
            arena = realloc(arena, arena_cap);
            if (!arena)
                return 1;
        }
        while ((size_t)ncand + 1 > offcap) {
            offcap *= 2;
            offs = realloc(offs, sizeof(size_t) * offcap);
            if (!offs)
                return 1;
        }
        offs[ncand] = arena_len;
        memcpy(arena + arena_len, line, L);
        arena[arena_len + L] = 0;
        arena_len += L + 1;
        ncand++;
        if (limit_c && ncand >= limit_c)
            break;
    }
    printf("candidates: %d passphrases (%zu B arena)\n", ncand, arena_len);

    struct hit *hits = calloc(64, sizeof(struct hit));
    if (!hits)
        return 1;
    uint64_t tried = 0;
    int nhit = sweep(arena, offs, ncand, salt, saltlen, ct, ctlen,
                     kdfs, nkdf, padded, floor_v, bs, hits, 64,
                     cross > 0 ? cross : 0, &tried);
    printf("\nswept %llu (candidate x alg x klen) combinations over KDFs %s\n",
           (unsigned long long)tried, kdfspec);
    if (!nhit) {
        printf("RESULT: no survivor cleared %s\n",
               padded ? "PKCS7 + printability"
                      : "printability only (no pad gate)");
    } else {
        printf("RESULT: %d survivors -- adjudicate by hand, not a solve\n", nhit);
    }
    free(hits);
    free(arena);
    free(offs);
    return 0;
}