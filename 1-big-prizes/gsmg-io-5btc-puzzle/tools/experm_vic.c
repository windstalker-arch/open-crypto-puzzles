// experm_vic.c -- exhaustive 9! permutations of the stream symbols a..i -> digits 0..8
// through the CERTIFIED phase-3.2.2 straddling checkerboard decoder, closing the gap
// left by interpreter_perm_sweep.py (section 145: permutation read as raw strings, NO
// VIC decode layer) and mapping_hillclimb.py (section 76: heuristic, not exhaustive).
//
// Certified decoder convention (tools/certified_vic.py, SELFCERT 3.2.2 PASS):
//   board        = "FUBCDORA.LETHINGKYMVPS.JQZXW"  (28 chars)
//   row0 = B[0:8]  -> letters on ascending non-escape digits {0,2,3,5,6,7,8,9}
//   row1 = B[8:18] -> (escape1=1, 0..9)
//   row2 = B[18:28]-> (escape2=4, 0..9)
// For each of the 362,880 permutations of "012345678", the permutation maps
// stream symbol a..i (index c-'a') to its digit, the resulting digit string is
// VIC-decoded through the certified board, and the decode is emitted (dbbib line,
// then faed line) for the certified gates (oracle.py / oracle_dualite.py --stdin).
//
// Usage:  gcc -O2 -o experm_vic experm_vic.c && ./experm_vic > cands.txt
//         python3 tools/oracle.py --stdin < cands.txt
//         python3 tools/oracle_dualite.py --stdin < cands.txt
//
// Witness (performed 2026-09-08): identity perm 012345678 -> dbbib decode
// "BLRIGUUHDKOFHHROHDDQVVNZOVOOC.DDPHBURIICDRDH.FH" and CANON map 815063742 ->
// "FLUTHCCNOEXNNUVDOODODNLOD.DHSKOODCNFCUTTBOUONDDRN", both byte-exact vs the
// certified Python decoder (25 random permutations also matched).
// Result: 725,760 lines (362,880 perms x dbbib+faed) -> 0 MATCH on BOTH funded
// gates (oracle.py small 1GSMG1JC9 and oracle_dualite.py 17ucy1K9).
#include <stdio.h>

static const char *B = "FUBCDORA.LETHINGKYMVPS.JQZXW";
static const char *DBBIB =
 "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbaggecbedcibfbffgigbeeeabe";
static const char *FAED =
 "faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic";

static char out[2048];

static int sval(char c, const char *p) {
    int idx = c - 'a';
    if (idx < 0 || idx > 8) return -1;
    return p[idx] - '0';
}

static void vic_decode(const char *d, int n, char *out) {
    const char *r0 = B, *r1 = B + 8, *r2 = B + 18;
    int e1 = 1, e2 = 4, oi = 0, i = 0;
    while (i < n) {
        int dd = d[i] - '0';
        if (dd == e1) {
            if (i + 1 >= n) { out[oi++] = '?'; i += 1; continue; }
            int d2 = d[i + 1] - '0';
            out[oi++] = r1[d2];
            i += 2;
            continue;
        }
        if (dd == e2) {
            if (i + 1 >= n) { out[oi++] = '?'; i += 1; continue; }
            int d2 = d[i + 1] - '0';
            out[oi++] = r2[d2];
            i += 2;
            continue;
        }
        int pos = 0, k = 0;
        for (int t = 0; t < 10; t++) {
            if (t == e1 || t == e2) continue;
            if (t == dd) { pos = k; break; }
            k++;
        }
        if (pos >= 0 && pos < 8) { out[oi++] = r0[pos]; i += 1; continue; }
        out[oi++] = '?'; i += 1;
    }
    out[oi] = 0;
}

static void emit_stream(const char *s, const char *p) {
    char digits[1500];
    int n = 0;
    for (; s[n]; n++) {
        int v = sval(s[n], p);
        digits[n] = (v < 0) ? '?' : ('0' + v);
    }
    vic_decode(digits, n, out);
    printf("%s\n", out);
}

int main(void) {
    char p[10] = "012345678";
    while (1) {
        emit_stream(DBBIB, p);
        emit_stream(FAED, p);
        int i = 8;
        while (i > 0 && p[i - 1] >= p[i]) i--;
        if (i == 0) break;
        int j = 8;
        while (p[j] <= p[i - 1]) j--;
        { char t = p[i - 1]; p[i - 1] = p[j]; p[j] = t; }
        { int lo = i, hi = 8; while (lo < hi) { char t = p[lo]; p[lo] = p[hi]; p[hi] = t; lo++; hi--; } }
    }
    return 0;
}