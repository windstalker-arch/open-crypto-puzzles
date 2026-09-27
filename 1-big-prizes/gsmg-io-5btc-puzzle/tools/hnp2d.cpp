/*
 * hnp2d.c - fast kernel for the 2-D nonce-relation search on issue #78's
 *           two ECDSA signatures (GSMG 5-BTC puzzle).
 *
 * Search space (both families are EXHAUSTIVE over the stated box):
 *
 *   family A:  R1 == a*R0 + b*G      for |a| <= B, |b| <= B
 *   family B:  a*R0 == b*R1          for |a| <= B, |b| <= B
 *
 * Method: the b dimension is hashed (open addressing on a 64-bit
 * fingerprint of the affine x), so the cost is O(B) point operations to
 * cover O(B^2) relations - not O(B^2).  The table holds b in [0, B] only
 * and both signs of b are reported, which is exact because
 * x(i*G) == x(-i*G).
 *
 * The search is split over 8 threads: each thread takes a contiguous
 * slice of the sweep range and starts from one scalar multiplication,
 * because the sweep is a sequential add-chain and cannot be interleaved.
 *
 * This file NEVER decides anything.  It only prints candidate
 * coefficient pairs; tools/hnp_2d_relation.py re-verifies every one of
 * them exactly (point equality, then d, then hash160(dG) against the
 * target).  A 64-bit fingerprint collision would therefore be reported
 * and rejected, never accepted.
 *
 * EC arithmetic is Jean Luc PONS' validated secp256k1 (~/Kangaroo/SECPK1).
 * Build:  clang++ -O2 -o hnp2d hnp2d.cpp <SECPK1 sources> -lpthread
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

#include "Int.h"
#include "Point.h"
#include "SECP256k1.h"

#define NTHREADS 8

static Secp256K1 *secp = NULL;
static long long BOUND = 0;
static int MODE = 0; /* 0 = family A, 1 = family B */

static Point P_RA, P_RB; /* affine inputs */

/* ------------------------------------------------------------------ */
/* hash table                                                          */
/* ------------------------------------------------------------------ */
typedef struct {
  uint64_t *keys;
  uint32_t *vals;
  size_t mask;
} HT;

static HT hts[NTHREADS];
static long long g_remap = 0;
static long long g_entries = 0;

static uint64_t fingerprint(Int *x) {
  uint64_t k = x->bits64[0];
  if (k == 0) {
    k = x->bits64[1] ^ 0x9E3779B97F4A7C15ULL;
    if (k == 0) {
      fprintf(stderr, "FATAL: degenerate 128-bit-zero x; aborting so that no "
                      "negative can be certified from a broken table\n");
      exit(3);
    }
    g_remap++;
  }
  return k;
}

static size_t slot_of(uint64_t k, size_t mask) {
  uint64_t h = k * 0x9E3779B97F4A7C15ULL;
  h ^= h >> 29;
  return (size_t)((h >> 17) & (uint64_t)mask);
}

static void ht_init(HT *h, long long expect) {
  size_t cap = 1024;
  while (cap < (size_t)expect * 2 + 16) cap <<= 1;
  h->mask = cap - 1;
  h->keys = (uint64_t *)calloc(cap, sizeof(uint64_t));
  h->vals = (uint32_t *)malloc(cap * sizeof(uint32_t));
  if (!h->keys || !h->vals) {
    fprintf(stderr, "FATAL: out of memory for %zu slots\n", cap);
    exit(4);
  }
}

static void ht_put(HT *h, uint64_t k, uint32_t v) {
  size_t i = slot_of(k, h->mask);
  while (h->keys[i] != 0) {
    if (h->keys[i] == k) return; /* keep the first */
    i = (i + 1) & h->mask;
  }
  h->keys[i] = k;
  h->vals[i] = v;
}

static int ht_get(HT *h, uint64_t k, uint32_t *out) {
  size_t i = slot_of(k, h->mask);
  while (h->keys[i] != 0) {
    if (h->keys[i] == k) {
      *out = h->vals[i];
      return 1;
    }
    i = (i + 1) & h->mask;
  }
  return 0;
}

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */
static Point negp(Point *p) {
  Point r;
  Int yy;
  yy.Set(&p->y);
  yy.ModNeg();
  r.x.Set(&p->x);
  r.y.Set(&yy);
  r.z.SetInt32(1);
  return r;
}

/* acc += q.  Kangaroo's Jacobian Add returns z3 == 0 (infinity) when
 * acc == q, so fall back to a real doubling in that case - otherwise the
 * whole chain silently dies on its first step. */
static Point step_add(Point *acc, Point *q) {
  Point nx = secp->Add(*acc, *q);
  if (nx.z.IsZero()) nx = secp->Double(*acc);
  return nx;
}

/* k*p for a possibly negative int64 k.  p must be affine. */
static Point smul(long long k, Point *p) {
  Point acc;
  int i, started = 0, neg = 0;
  if (k == 0) {
    acc.Clear();
    return acc;
  }
  if (k < 0) {
    neg = 1;
    k = -k;
  }
  acc.Clear();
  for (i = 62; i >= 0; i--) {
    /* double on EVERY bit, add only on set bits */
    if (started) acc = secp->Double(acc);
    if ((k >> i) & 1) {
      if (!started) {
        /* NB: Point::Set(Point&) does NOT copy z (verified) - use 3-arg form */
        acc.Set(&p->x, &p->y, &p->z);
        started = 1;
      } else {
        acc = secp->Add(acc, *p);
      }
    }
  }
  acc.Reduce();
  if (neg) return negp(&acc);
  return acc;
}

static void report(long long a, long long b) {
  printf("HIT %lld %lld\n", a, b);
  fflush(stdout);
}

/* ------------------------------------------------------------------ */
/* phase 1: build the baby-step table  (b in [1, B] -> i*Rstep)        */
/* ------------------------------------------------------------------ */
typedef struct {
  int id;
  long long lo, hi; /* inclusive range of the coefficient */
} slice_t;

static Point g_step; /* the point the table is built from */

static void *build_worker(void *arg) {
  slice_t *s = (slice_t *)arg;
  HT *h = &hts[s->id];
  long long cnt = s->hi - s->lo + 1;
  if (cnt <= 0) return NULL;
  ht_init(h, cnt + 2);
  Point acc = smul(s->lo, &g_step);
  for (long long i = s->lo; i <= s->hi; i++) {
    /* acc is Jacobian after the first Add: the hash key MUST be the
     * affine x, so reduce (this is also the one inversion per step). */
    if (!acc.z.IsZero()) {
      acc.Reduce();
      Int x;
      x.Set(&acc.x);
      ht_put(h, fingerprint(&x), (uint32_t)i);
    }
    acc = step_add(&acc, &g_step);
  }
  return NULL;
}

/* ------------------------------------------------------------------ */
/* phase 2: sweep                                                       */
/* ------------------------------------------------------------------ */
static Point g_base;  /* Rb for family A, R0 for family B */
static Point g_move;  /* -R0 for family A, +R0 for family B */

static void *sweep_worker(void *arg) {
  slice_t *s = (slice_t *)arg;
  long long a;
  Point acc;

  /* family A: P(a) = R1 - a*R0 = g_base + a*g_move, g_move = -R0
     family B: P(a) = a*R0 = a*g_move, g_move = +R0 */
  if (MODE == 0) {
    if (s->lo == 0) {
      acc.Set(&g_base.x, &g_base.y, &g_base.z);
    } else {
      Point t = smul(s->lo, &g_move);
      acc = secp->Add(g_base, t);
    }
  } else {
    acc = smul(s->lo, &g_move);
  }

  for (a = s->lo; a <= s->hi; a++) {
    /* family B, a == 0: 0*R0 is infinity, which has no x to hash */
    if (MODE == 1 && a == 0) {
      acc = smul(1, &g_move);
      continue;
    }
    if (!acc.z.IsZero()) {
      acc.Reduce();
      Int x;
      x.Set(&acc.x);
      uint64_t k = fingerprint(&x);
      for (int t = 0; t < NTHREADS; t++) {
        uint32_t v;
        if (ht_get(&hts[t], k, &v)) {
          if (MODE == 0) {
            report(a, (long long)v);
            report(a, -(long long)v);
          } else {
            report(a, (long long)v);
            report(a, -(long long)v);
          }
        }
      }
    }
    acc = step_add(&acc, &g_move);
  }
  return NULL;
}

/* ------------------------------------------------------------------ */
static void split(long long lo, long long hi, slice_t *out) {
  long long total = hi - lo + 1;
  long long per = total / NTHREADS;
  long long rem = total % NTHREADS;
  long long cur = lo;
  for (int i = 0; i < NTHREADS; i++) {
    out[i].id = i;
    out[i].lo = cur;
    out[i].hi = cur + per + (i < rem ? 1 : 0) - 1;
    cur = out[i].hi + 1;
  }
}

int main(int argc, char **argv) {
  if (argc < 7) {
    fprintf(stderr,
            "usage: %s A|B <bound> <R0x> <R0y> <R1x> <R1y>\n", argv[0]);
    return 2;
  }
  MODE = (argv[1][0] == 'B') ? 1 : 0;
  BOUND = atoll(argv[2]);
  if (BOUND < 1) {
    fprintf(stderr, "bad bound\n");
    return 2;
  }

  secp = new Secp256K1();
  secp->Init();

  Int ax, ay, bx, by;
  ax.SetBase16(argv[3]);
  ay.SetBase16(argv[4]);
  bx.SetBase16(argv[5]);
  by.SetBase16(argv[6]);
  P_RA.x.Set(&ax);
  P_RA.y.Set(&ay);
  P_RA.z.SetInt32(1);
  P_RB.x.Set(&bx);
  P_RB.y.Set(&by);
  P_RB.z.SetInt32(1);

  if (!secp->EC(P_RA) || !secp->EC(P_RB)) {
    fprintf(stderr, "FATAL: input point is not on secp256k1\n");
    return 3;
  }

  if (MODE == 0) {
    /* R1 == a*R0 + b*G  ->  sweep a, table on b*G */
    g_step = secp->G;
    g_step.Reduce();
    g_base = P_RB;
    g_move = negp(&P_RA);
  } else {
    /* a*R0 == b*R1  ->  sweep a*R0, table on b*R1 */
    g_step = P_RB;
    g_move = P_RA;
  }

  slice_t sl[NTHREADS];
  pthread_t th[NTHREADS];

  split(1, BOUND, sl);
  for (int i = 0; i < NTHREADS; i++) pthread_create(&th[i], NULL, build_worker, &sl[i]);
  for (int i = 0; i < NTHREADS; i++) pthread_join(th[i], NULL);
  for (int i = 0; i < NTHREADS; i++) g_entries += hts[i].mask + 1;
  fprintf(stderr, "TABLE bound=%lld slots=%lld remap=%lld\n", BOUND, g_entries,
          g_remap);

  split(-BOUND, BOUND, sl);
  for (int i = 0; i < NTHREADS; i++) pthread_create(&th[i], NULL, sweep_worker, &sl[i]);
  for (int i = 0; i < NTHREADS; i++) pthread_join(th[i], NULL);

  fprintf(stderr, "SWEEP done steps=%lld remap=%lld\n", 2 * BOUND + 1, g_remap);
  printf("DONE\n");
  return 0;
}
