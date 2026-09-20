// experm_vic_trans.c -- lead-A: full 9! permutations x certified checkerboard x
// digit-level columnar de-transposition. Extends the row-199 verified core
// (experm_vic.c) with full-rectangle de-transpose widths. Cells NOT covered by
// row 199 (which swept 9! x no-trans only): dbbib91 (live) widths {0,7,13},
// dbbib69 widths {3,23}, faed570 widths {15,38}.
//
// Certified decoder identically as experm_vic.c (board FUBCDORA.LETHINGKYMVPS.JQZXW,
// escapes e1=1, e2=4; SELFCERT 3.2.2 PASS, byte-exact witnesses documented in
// expert_vic.c header).
//
// Usage:  gcc -O2 -o experm_vic_trans experm_vic_trans.c && ./experm_vic_trans > cands
#include <stdio.h>
#include <string.h>

static const char *B = "FUBCDORA.LETHINGKYMVPS.JQZXW";
static const char *DBBIB69 =
 "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbaggecbedcibfbffgigbeeeabe";
static const char *DBBIB91 =
 "dbbibfbhccbegbihabebeihbeggegebebbgehhebhhfbabfdhbeffcdbbfcccgbfbeeggecbedcibfbffgigbeeeabe";
static const char *FAED =
 "faedggeedfcbdabhhggcadcfeddgfdgbgigaaedggiafaecghggcdaihehahbahigceifgbfgefgaifabifagaegeacgbbeagfggeeggafbacgfcdbeiffaafcidahgdeefghhcggaegdebhhegeghcegadfbdiagefcicggifdcgaaggfbigaicfbhecaecbceiaicebgbgiecdeggfgegaedggfiiciiififhggcgfgdcdggefcbeeigefibgibggghhfbcgifdehedfdagicdbhicgaiedaehahghhcihdghfhbiicecbiichihiiigiddgehhdfdchcbafgfbhaheagegecafehgcfggggcagfhhghbaihidiehhfdeggdgcihggggghadahigigbgecgedfcdggaccdehiicigfbffhggaeidbbeibbeiifdgfdhieeeieeecifdgdahdiggfhegfiaffiggbcbcehceabfbedbiibfbfdedeehgigfaaiggagbeiichiedifbehgbccahhbiibibbibdcbahaidhfahiihic";

static char out[2048];
static char wbuf[1500];
static char tbuf[1500];

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

/* de-transpose: digits written row-major into w columns, read column-major. */
static void detr(const char *d, int n, int w, char *o) {
    int rows = n / w;
    for (int c = 0; c < w; c++)
        for (int r = 0; r < rows; r++)
            o[r * w + c] = d[c * rows + r];
}

static void emit_stream(const char *s, const char *p, int w) {
    int n = 0;
    for (; s[n]; n++) {
        int v = sval(s[n], p);
        wbuf[n] = (v < 0) ? '?' : ('0' + v);
    }
    if (w > 0) {
        detr(wbuf, n, w, tbuf);
        vic_decode(tbuf, n, out);
    } else {
        vic_decode(wbuf, n, out);
    }
    printf("%s\n", out);
}

int main(void) {
    char p[10] = "012345678";
    while (1) {
        emit_stream(DBBIB69, p, 3);
        emit_stream(DBBIB69, p, 23);
        emit_stream(DBBIB91, p, 0);
        emit_stream(DBBIB91, p, 7);
        emit_stream(DBBIB91, p, 13);
        emit_stream(FAED, p, 15);
        emit_stream(FAED, p, 38);
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