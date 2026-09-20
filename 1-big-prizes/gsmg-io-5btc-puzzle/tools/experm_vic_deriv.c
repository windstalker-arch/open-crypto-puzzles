// experm_vic_deriv.c -- lead-A closure of Note 35: full 9! interpreter perms
// applied to streams DERIVED from raw dbbib_91/faed_570 (position/diff/sum
// constructions mod 9), then certified checkerboard decode (board
// FUBCDORA.LETHINGKYMVPS.JQZXW, escapes 1,4; decoder identical to the row-199
// verified core, SELFCERT 3.2.2 PASS). Rows 199/201/202/204/213 closed the 9!
// x certified board over the RAW streams (no derived layer); the derived layer
// is the Note-35 (2026-09-08) stated remainder.
//
// Constructions (value map v = perm(letter)):
//   d0 fwd_diff : (v[i+1] - v[i])      mod 9
//   d1 bak_diff : (v[i]   - v[i-1])    mod 9
//   d2 cumsum   : (sum_{k<=i} v[k])    mod 9
//   d3 pos_add  : (v[i] + i)           mod 9   (i 0-based)
//   d4 pos_sub  : (v[i] - i)           mod 9
//   d5 raw      : v[i]                          (control, must equal row-204)
// Emits one decoded line per (perm, construction, stream).
//
// Usage: gcc -O2 -o experm_vic_deriv experm_vic_deriv.c && ./experm_vic_deriv
#include <stdio.h>
#include <string.h>

static const char *B = "FUBCDORA.LETHINGKYMVPS.JQZXW";
static const char *DBBIB91 =
 "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe";
static const char *FAED =
 "faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic";

static char out[2048];
static char wbuf[1500];
static char dbuf[1500];

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
            out[oi++] = r1[d[i + 1] - '0'];
            i += 2;
            continue;
        }
        if (dd == e2) {
            if (i + 1 >= n) { out[oi++] = '?'; i += 1; continue; }
            out[oi++] = r2[d[i + 1] - '0'];
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

/* build the derived digit stream for construction c (0..5) under perm p */
static void derive(const char *s, int n, const char *p, int c, char *o) {
    int vv[1500];
    for (int i = 0; i < n; i++) vv[i] = sval(s[i], p);
    if (c == 0) {          /* fwd_diff */
        for (int i = 0; i < n - 1; i++) o[i] = '0' + (((vv[i + 1] - vv[i]) % 9) + 9) % 9;
        o[n - 1] = 0;
    } else if (c == 1) {   /* adj_sum: (v[i] + v[i+1]) mod 9 */
        for (int i = 0; i < n - 1; i++) o[i] = '0' + ((vv[i] + vv[i + 1]) % 9);
        o[n - 1] = 0;
    } else if (c == 2) {   /* cumsum */
        int acc = 0;
        for (int i = 0; i < n; i++) { acc = (acc + vv[i]) % 9; o[i] = '0' + acc; }
        o[n] = 0;
    } else if (c == 3) {   /* pos_add 0-based */
        for (int i = 0; i < n; i++) o[i] = '0' + (((vv[i] + i) % 9) + 9) % 9;
        o[n] = 0;
    } else if (c == 4) {   /* pos_sub 0-based */
        for (int i = 0; i < n; i++) o[i] = '0' + (((vv[i] - i) % 9) + 9) % 9;
        o[n] = 0;
    } else {               /* c == 5 raw control */
        for (int i = 0; i < n; i++) o[i] = ('0' + vv[i]);
        o[n] = 0;
    }
}

int main(void) {
    const char *streams[2] = { DBBIB91, FAED };
    int lens[2] = { 91, 570 };
    const char *names[2] = { "dbbib91", "faed" };
    /* one header comment line is NOT emitted; candidates are pure decodes.
       Emit tag bundle on argv instead: 12 cells = 2 streams x 6 constructions.
    */
    for (int c = 0; c <= 5; c++) {           /* 6 constructions incl raw control */
        for (int si = 0; si < 2; si++) {
            // reset perm and iterate
            char p[10] = "012345678";
            long cnt = 0;
            while (1) {
                int n = lens[si];
                derive(streams[si], n, p, c, dbuf);
                vic_decode(dbuf, n > 0 ? (int)strlen(dbuf) : 0, out);
                printf("%s\n", out);
                cnt++;
                int i = 8;
                while (i > 0 && p[i - 1] >= p[i]) i--;
                if (i == 0) break;
                int j = 8;
                while (p[j] <= p[i - 1]) j--;
                { char t = p[i - 1]; p[i - 1] = p[j]; p[j] = t; }
                { int lo = i, hi = 8; while (lo < hi) { char t = p[lo]; p[lo] = p[hi]; p[hi] = t; lo++; hi--; } }
            }
            fprintf(stderr, "cell c=%d stream=%s perms=%ld\n", c, names[si], cnt);
        }
    }
    return 0;
}