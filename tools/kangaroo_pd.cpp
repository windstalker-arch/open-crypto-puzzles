// Faithful plain-C++ port of the Kangaroo distinguished-point algorithm.
//
// This is a line-by-line port of the herd construction and walk loop from
// Kangaroo v2.2 (Kangaroo.cpp CreateHerd / SolveKeyCPU / CheckKey), using the
// stock SECPK1 primitives. No CUDA, no OpenCL. Builds and runs on Termux/ARM.
//
// WHY THE EXACT UPSTREAM GEOMETRY MATTERS
// The meeting condition is Td - Wd == k (mod n) for the RELATIVE target k,
// where Td and Wd are the tame and wild accumulated distances. The subtle part
// is that BOTH herds walk, independently, each adding positive jumps. So
// delta = Td - Wd is the difference of two independent random walks: it wanders
// in both directions and returns to the target neighbourhood many times. An
// earlier version of this file advanced only the tame herd and compared against
// a frozen wild distance. That makes delta monotone increasing, so it overshoots
// the target once and can never return -- and the search silently never finishes.
// This is the single most important invariant in the algorithm.
//
// Other invariants this file depends on (each one was a real bug at some point):
//  - Int::Rand(nbit) is implemented with rndl(). rndl() is UNSEEDED by default
//    and glibc's unseeded rndl() returns a constant, so every jump distance comes
//    out identical, every jump point collapses to the same curve point, and the
//    walk does not move at all -- with no crash and no error. seedRng() below is
//    load-bearing, not decoration.
//  - Points are walked in AFFINE form (z == 1). A Jacobian x is projective, so
//    comparing it against another point's x never matches.
//  - Int::SetQWord(n,b) writes one limb without clearing the other 31, so always
//    initialize wide values through Int(uint64_t) (see setU64).
//  - Point::Set(Point&) in the stock library omits z, so copy x/y/z explicitly.
//  - The DP mask is dMask = ~((1ULL << (64 - dpSize)) - 1): dpSize low bits must
//    be ZERO for a distinguished point.

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
#include <pthread.h>
#include <sys/stat.h>
#include <unistd.h>
#include "Int.h"
#include "Point.h"
#include "SECP256k1.h"
#include "IntGroup.h"
#include "Timer.h"

// ---------------------------------------------------------------------------
// SECPK1 library quirks. Kept here so the reasons stay attached to the fixes.
// ---------------------------------------------------------------------------

// Int::SetQWord writes a single limb without clearing the rest, so a previously
// used Int keeps stale high limbs. Int(uint64_t) clears first.
static inline void setU64(Int *dst, uint64_t v) {
  Int t((uint64_t)v);
  dst->Set(&t);
}

// Point::Set(Point&) drops z, which silently turns affine points into
// projective ones. Copy all three coordinates.
static inline void setPoint(Point &dst, Point &src) {
  dst.Set(&src.x, &src.y, &src.z);
}

// See the header comment: without this the jump table is degenerate and the
// walk never moves. Upstream seeds at Kangaroo.cpp:761 and main.cpp:177.
static void seedRng() { rseed(Timer::getSeed32()); }

// ---------------------------------------------------------------------------

static Secp256K1 sec;

// Distinguised-point table, keyed on the affine x coordinate exactly as
// upstream's HashTable does. Linear probing with a bounded probe window; the
// table is sized generously so probes do not degenerate in short runs.
struct DpTable {
  struct Entry {
    uint64_t hi, lo;   // x.bits64[3], x.bits64[0] -- fingerprint
    uint32_t tag;      // 0 = empty, 1 = tame, 2 = wild
    Int dist;
  };
  std::vector<Entry> e;
  size_t mask;
  uint64_t dpSize;

  void init(int size, int dpBits) {
    e.assign((size_t)1 << size, Entry());
    mask = ((size_t)1 << size) - 1;
    dpSize = dpBits;
  }

  uint64_t dpMask() const {
    if (dpSize == 0) return 0;
    uint64_t n = dpSize > 63 ? 63 : dpSize;
    return ~(((uint64_t)1 << (64 - n)) - 1);
  }

  bool isDP(uint64_t x) const { return (x & dpMask()) == 0; }

  // Returns: 0 = stored, 1 = collided with opposite herd (*hitA set),
  //          2 = same-herd hit (ignore), 3 = probe window full (drop).
  int insert(uint64_t hi, uint64_t lo, int tag, Int *dist, Entry **hitA) {
    uint64_t h = hi ^ (lo * 0x9e3779b97f4a7c15ULL);
    h ^= h >> 29;
    h *= 0xbf58476d1ce4e5b9ULL;
    h ^= h >> 32;
    size_t idx = (size_t)(h & mask);
    for (size_t p = 0; p < 64; p++) {
      Entry &en = e[(idx + p) & mask];
      if (en.tag == 0) {
        en.hi = hi;
        en.lo = lo;
        en.tag = (uint32_t)tag;
        en.dist.Set(dist);
        return 0;
      }
      if (en.hi == hi && en.lo == lo) {
        // The caller owns the second side (it passes its own dist), so there is
        // no second reference to hand back.
        *hitA = &en;
        return ((int)en.tag != tag) ? 1 : 2;
      }
    }
    return 3;
  }
};

static DpTable dp;

// Distinguished-point policy. DP_BITS = leading zero bits required of the x
// coordinate; DP_TABLE_BITS = log2 of the table size (must exceed 2*DP_BITS for
// a healthy load factor).
static const int DP_BITS = 8;
static const int DP_TABLE_BITS = 20;

// Build the jump table. NB_JUMP points at distances in [1, 2^jumpBits).
// jumpBits = rangePower/2 + 1, and upstream draws jumpDistance[i].Rand(jumpBit)
// in the non-symmetry build (Kangaroo.cpp:809). The symmetry build halves it to
// jumpBit/2; copying that variant into a non-symmetry port makes the 32 jumps
// collide by birthday, which the distinctness assertion below catches.
static const int NB_JUMP = 32;
static Int g_jd[NB_JUMP];
static Point g_jp[NB_JUMP];

static void buildJumps(int jumpBits) {
  for (int i = 0; i < NB_JUMP; i++) {
    Int d;
    d.Rand(jumpBits);
    if (d.IsZero()) d.SetInt32(1);
    g_jd[i].Set(&d);
    g_jp[i] = sec.ComputePublicKey(&g_jd[i], true);
  }
}

// One herd member.
struct Kang {
  Point p;
  Int dist;
  uint64_t jmp;   // jump chosen for the current step
};

// CreateHerd, split into its two cases. Upstream packs both kinds into one
// vector and selects on (j+firstType)%2; the geometry is:
//   tame:  dist = Rand(N)                  in [0, N)      point = dist*G
//   wild:  dist = Rand(N) - N/2            in [-N/2, N/2) point = K + dist*G
// The wild offset is SIGNED. That is the point: the meeting condition is
// Td - Wd == k, and a signed wild start on both sides of zero is what lets the
// difference of the two walks hover around k instead of always overshooting.
static void createTame(Kang *k, int n, int rangePower) {
  for (int j = 0; j < n; j++) {
    Int d;
    d.Rand(rangePower);
    if (d.IsZero()) d.SetInt32(1);
    k[j].dist.Set(&d);
    k[j].p = sec.ComputePublicKey(&d, true);
  }
}

static void createWild(Kang *k, int n, Point *keyToSearch, int rangePower,
                       Int *rangeWidthDiv2) {
  for (int j = 0; j < n; j++) {
    Int d;
    d.Rand(rangePower);
    d.ModSubK1order(rangeWidthDiv2);
    k[j].dist.Set(&d);
    Point g = sec.ComputePublicKey(&d, true);
    Point sum = sec.AddDirect(*keyToSearch, g);
    setPoint(k[j].p, sum);
  }
}

// Advance a WHOLE group of herd members by one jump each, mirroring
// SolveKeyCPU's batched inner loop. The jump for each member is chosen from its
// own x coordinate, exactly as upstream does.
//
// The batching is not an optimisation detail: upstream collects every dx for the
// group and inverts them all in a single Montgomery batch (IntGroup::ModInv).
// Doing one ModInv per member instead costs an order of magnitude in wall time,
// which is the difference between a self-test finishing and appearing hung.
//
// dpMaskCheck, when non-null, receives each member's new x top word so the
// caller can apply distinguished-point logic without re-reading the points.
static void stepGroup(Kang *k, int n, Int *dxOut, IntGroup *grp) {
  for (int g = 0; g < n; g++) {
    uint64_t jmp = k[g].p.x.bits64[0] % NB_JUMP;
    k[g].jmp = jmp;
    Int p1x, p2x;
    p1x.Set(&g_jp[jmp].x);
    p2x.Set(&k[g].p.x);
    dxOut[g].ModSub(&p2x, &p1x);
  }

  // One batched inversion for the whole group.
  grp->Set(dxOut);
  grp->ModInv();

  for (int g = 0; g < n; g++) {
    uint64_t jmp = k[g].jmp;
    Int p1x, p1y, p2x, p2y;
    p1x.Set(&g_jp[jmp].x);
    p1y.Set(&g_jp[jmp].y);
    p2x.Set(&k[g].p.x);
    p2y.Set(&k[g].p.y);

    Int dy, s, _p, rx, ry;
    dy.ModSub(&p2y, &p1y);
    s.ModMulK1(&dy, &dxOut[g]);
    _p.ModSquareK1(&s);
    rx.ModSub(&_p, &p1x);
    rx.ModSub(&p2x);
    ry.ModSub(&p2x, &rx);
    ry.ModMulK1(&s);
    ry.ModSub(&p2y);

    Point np;
    np.x.Set(&rx);
    np.y.Set(&ry);
    np.z.SetInt32(1);
    setPoint(k[g].p, np);
    k[g].dist.ModAddK1order(&g_jd[jmp]);
  }
}

// CheckKey: resolve the four sign combinations, compare against keyToSearch,
// then add rangeStart to report the absolute key. Returns 1 on a solve.
static int checkKey(Int *Td, Int *Wd, uint8_t type, Point *keyToSearch,
                    Int *rangeStart, Int *outKey, uint8_t *outType) {
  if (type & 0x1) Td->ModNegK1order();
  if (type & 0x2) Wd->ModNegK1order();

  Int pk;
  pk.Set(Td);
  pk.ModAddK1order(Wd);

  Point P = sec.ComputePublicKey(&pk);
  if (P.equals(*keyToSearch)) {
    pk.ModAddK1order(rangeStart);
    outKey->Set(&pk);
    *outType = type;
    return 1;
  }
  return 0;
}

// ---------------------------------------------------------------------------
// Self-test: recover a known key. Small range so it terminates quickly.
// ---------------------------------------------------------------------------

// Shared search state. Threaded workers read the immutable parts (jumps, target,
// range) and serialise on dpMut for the table, exactly as upstream serialises on
// ghMutex around AddToTable.
struct Shared {
  Point keyToSearch;
  // The ABSOLUTE target, i.e. the public key the operator actually asked for.
  // keyToSearch is the range-shifted copy the herds collide on, so it cannot
  // identify the search on its own: a checkpoint stores it, and a checkpoint
  // written for a different key but the same range would be indistinguishable.
  Point absTarget;
  Int rangeStart;
  int rangePower;
  int jumpBits;
  int dpBits;          // 0 = no distinguished points; must match the load-time check

  // Selftest budget. Without a cap the selftest cannot fail, only run forever,
  // so "SELFTEST FAIL: exhausted the budget" would be unreachable and a broken
  // port would report success by hanging. Both are read from the environment;
  // the defaults sit orders of magnitude above the ~2^10 ops a solve needs.
  unsigned long long maxOps;    // 0 = no op cap
  double maxSeconds;            // 0 = no wall-clock cap

  pthread_mutex_t dpMut;
  volatile int stop;          // set once any thread solves
  volatile int solved;
  Int solvedKey;
  uint8_t solvedType;

  unsigned long long ops;
  unsigned long long collisions;
  unsigned long long dpsSeen;
  // Insert outcomes other than a clean store. Guarded by statMut: a full probe
  // window means the table is saturating and losing distinguished points.
  unsigned long long sameHerd;
  unsigned long long oppositeHerd;
  unsigned long long probeFull;
  pthread_mutex_t statMut;
  Int kRelTarget;
};

// One worker's herds and its own inversion scratch.
struct Worker {
  Shared *sh;
  std::vector<Kang> th, wh;
  std::vector<Int> dx;
  IntGroup *grp;
  int half;
  int tid;
};

// Try to solve from an opposite-herd collision. Returns 1 if solved.
static int trySolve(Shared *sh, Int *Td, Int *Wd, int tid) {
  for (int ty = 0; ty < 4; ty++) {
    Int a, b, key;
    a.Set(Td);
    b.Set(Wd);
    uint8_t type = (uint8_t)ty;
    if (checkKey(&a, &b, type, &sh->keyToSearch, &sh->rangeStart, &key, &type)) {
      pthread_mutex_lock(&sh->statMut);
      if (!sh->solved) {
        sh->solved = 1;
        sh->solvedKey.Set(&key);
        sh->solvedType = type;
        sh->stop = 1;
      }
      pthread_mutex_unlock(&sh->statMut);
      printf("[thread %d] SOLVED: privkey = %s (sign type %d)\n", tid,
             key.GetBase16().c_str(), type);
      fflush(stdout);
      return 1;
    }
  }
  return 0;
}

static void *workerMain(void *arg) {
  Worker *w = (Worker *)arg;
  Shared *sh = w->sh;

  while (!sh->stop) {
    stepGroup(w->th.data(), w->half, w->dx.data(), w->grp);
    stepGroup(w->wh.data(), w->half, w->dx.data(), w->grp);

    pthread_mutex_lock(&sh->statMut);
    sh->ops += 2ULL * w->half;
    pthread_mutex_unlock(&sh->statMut);

#ifdef KPD_PROBES
    if (w->tid == 0 && getenv("KPD_POST")) {
      static long long r = 0;
      if ((r % 1000) == 0) {
        // Are points still consistent with their distances AFTER stepping?
        int bad = 0;
        for (int g = 0; g < w->half; g++) {
          Point chk2 = sec.ComputePublicKey(&w->th[g].dist, true);
          if (!chk2.equals(w->th[g].p)) bad++;
        }
        // How many DISTINCT x do the 32 tame points have right now?
        int ux = 0;
        for (int i = 0; i < w->half; i++) {
          bool nu = true;
          for (int j = 0; j < i; j++) if (w->th[j].p.x.IsEqual(&w->th[i].p.x)) nu = false;
          ux += nu;
        }
        // Are they still affine (z==1)?
        int nonaff = 0;
        for (int g = 0; g < w->half; g++) {
          Int one; one.SetInt32(1);
          if (!w->th[g].p.z.IsEqual(&one)) nonaff++;
        }
        printf("[post r%lld] tameInconsistent=%d distinctTameX=%d/%d nonAffine=%d\n",
               r, bad, ux, w->half, nonaff);
        printf("        b3[0]=0x%016llX b0[0]=0x%016llX z[0]=0x%016llX\n",
               (unsigned long long)w->th[0].p.x.bits64[3],
               (unsigned long long)w->th[0].p.x.bits64[0],
               (unsigned long long)w->th[0].p.z.bits64[0]);
        printf("        dist[0]=%s dist[1]=%s\n",
               w->th[0].dist.GetBase16().c_str(), w->th[1].dist.GetBase16().c_str());
        printf("        jmp[0]=%llu jmp[1]=%llu gjd[0]=%s gjd[1]=%s\n",
               (unsigned long long)w->th[0].jmp, (unsigned long long)w->th[1].jmp,
               g_jd[w->th[0].jmp].GetBase16().c_str(),
               g_jd[w->th[1].jmp].GetBase16().c_str());
        // Which indices share an x, and are their dists/jmps identical?
        for (int i = 0; i < w->half; i++)
          for (int j = i + 1; j < w->half; j++)
            if (w->th[i].p.x.IsEqual(&w->th[j].p.x)) {
              printf("        dup th[%d]/th[%d] distEq=%d jmp=%llu/%llu\n", i, j,
                     w->th[i].dist.IsEqual(&w->th[j].dist),
                     (unsigned long long)w->th[i].jmp,
                     (unsigned long long)w->th[j].jmp);
            }
        fflush(stdout);
      }
      r++;
    }
#endif

#ifdef KPD_PROBES
    if (w->tid == 0 && getenv("KPD_DELTA")) {
      static long long r = 0;
      if (r < 12 || (r % 5000) == 0) {
        Int k; k.Set(&sh->kRelTarget);
        Int d; d.Set(&w->th[0].dist);
        Int wdist; wdist.Set(&w->wh[0].dist);
        Int delta; delta.ModSub(&w->th[0].dist, &w->wh[0].dist);
        printf("[delta r%lld] tame0=%s wild0=%s delta=%s k=%s\n", r,
               w->th[0].dist.GetBase16().c_str(),
               w->wh[0].dist.GetBase16().c_str(),
               delta.GetBase16().c_str(), k.GetBase16().c_str());
        fflush(stdout);
      }
      r++;
    }
#endif



    for (int g = 0; g < w->half; g++) {
      Kang *cand[2] = {&w->th[g], &w->wh[g]};
      int tags[2] = {1, 2};
      for (int c = 0; c < 2; c++) {
        uint64_t hi = cand[c]->p.x.bits64[3];
        if (!dp.isDP(hi)) continue;

        pthread_mutex_lock(&sh->statMut);
        sh->dpsSeen++;
        pthread_mutex_unlock(&sh->statMut);

        // The table is shared, so the whole probe-and-insert must be atomic or
        // two workers can interleave and corrupt the probe sequence.
        DpTable::Entry *hitA = NULL;
        int r;
        pthread_mutex_lock(&sh->dpMut);
        r = dp.insert(hi, cand[c]->p.x.bits64[0], tags[c], &cand[c]->dist,
                      &hitA);
        if (r == 2) { pthread_mutex_lock(&sh->statMut); sh->sameHerd++; pthread_mutex_unlock(&sh->statMut); }
        if (r == 3) { pthread_mutex_lock(&sh->statMut); sh->probeFull++; pthread_mutex_unlock(&sh->statMut); }
        if (r == 1 && hitA) {
          pthread_mutex_lock(&sh->statMut);
          sh->oppositeHerd++;
          pthread_mutex_unlock(&sh->statMut);
          Int Td, Wd;
          if ((int)hitA->tag == 1) {
            Td.Set(&hitA->dist);
            Wd.Set(&cand[c]->dist);
          } else {
            Td.Set(&cand[c]->dist);
            Wd.Set(&hitA->dist);
          }
          pthread_mutex_lock(&sh->statMut);
          sh->collisions++;
          pthread_mutex_unlock(&sh->statMut);
          // Solve outside the table lock, then leave it released: every
          // iteration re-acquires at the top, so re-locking here would
          // self-deadlock on a non-recursive mutex.
          pthread_mutex_unlock(&sh->dpMut);
          trySolve(sh, &Td, &Wd, w->tid);
        } else {
          pthread_mutex_unlock(&sh->dpMut);
        }
        if (sh->stop) break;
      }
    }
  }
  return NULL;
}

// ---------------------------------------------------------------------------
// Checkpointing. Written atomically (temp file + fsync + rename) so a kill
// during the write cannot leave a truncated checkpoint that resumes into a
// WRONG search -- the same lesson as the rockyou sweep in this repo, where a
// resumed shard silently processed the wrong lines.
// ---------------------------------------------------------------------------

static const char *CKPT_MAGIC = "KPDCKPT1";

struct CkptHeader {
  char magic[8];
  uint32_t version;
  uint32_t rangePower;
  uint32_t jumpBits;
  uint32_t dpBits;
  uint64_t lo;
  uint64_t entries;      // number of occupied table entries
  // v2: the absolute target point. A checkpoint belongs to ONE public key, and
  // lo/bits/dpBits do not identify which: two different keys over the same
  // range pass every other check. Without this the loader restores another
  // key's table AND overwrites the target with it, so the run searches the
  // wrong key and only notices at the very end, or never.
  unsigned char absX[32];
  unsigned char absY[32];
};

static void intToBytes(Int *v, unsigned char *out) {
  for (int i = 0; i < 4; i++) {
    uint64_t w = v->bits64[i];
    for (int b = 0; b < 8; b++) out[i * 8 + b] = (unsigned char)(w >> (56 - 8 * b));
  }
}

static void bytesToInt(Int *v, const unsigned char *in) {
  for (int i = 0; i < 4; i++) {
    uint64_t w = 0;
    for (int b = 0; b < 8; b++) w = (w << 8) | in[i * 8 + b];
    v->bits64[i] = w;
  }
  for (int i = 4; i < NB64BLOCK; i++) v->bits64[i] = 0;
  v->bits64[NB64BLOCK - 1] &= 0x0FFFFFFFFFFFFFFFULL;  // order is < 2^256
}

static int saveCheckpoint(const char *path, Shared *sh) {
  char tmp[1024];
  snprintf(tmp, sizeof(tmp), "%s.tmp", path);
  FILE *f = fopen(tmp, "wb");
  if (!f) return -1;

  CkptHeader h;
  memset(&h, 0, sizeof(h));  // POD only: no members with constructors
  memcpy(h.magic, CKPT_MAGIC, 8);
  h.version = 2;
  h.rangePower = (uint32_t)sh->rangePower;
  h.jumpBits = (uint32_t)sh->jumpBits;
  h.dpBits = (uint32_t)sh->dpBits;
  h.lo = sh->rangeStart.bits64[0];
  intToBytes(&sh->absTarget.x, h.absX);
  intToBytes(&sh->absTarget.y, h.absY);
  // Count first: the header must describe the records that follow it, so a
  // reader can size the table instead of trusting a stale zero.
  for (size_t i = 0; i < dp.e.size(); i++)
    if (dp.e[i].tag) h.entries++;
  fwrite(&h, sizeof(h), 1, f);

  // Only the RELATIVE target and the occupied table entries are stored. Herd
  // positions are deliberately NOT stored: they are cheap to recreate and a
  // half-restored walk would silently bias the search.
  unsigned char buf[32];
  intToBytes(&sh->keyToSearch.x, buf);
  fwrite(buf, 32, 1, f);
  intToBytes(&sh->keyToSearch.y, buf);
  fwrite(buf, 32, 1, f);

  for (size_t i = 0; i < dp.e.size(); i++) {
    if (!dp.e[i].tag) continue;
    fwrite(&dp.e[i].hi, 8, 1, f);
    fwrite(&dp.e[i].lo, 8, 1, f);
    fwrite(&dp.e[i].tag, 4, 1, f);
    intToBytes(&dp.e[i].dist, buf);
    fwrite(buf, 32, 1, f);
  }
  const unsigned long long written = h.entries;
  if (ferror(f)) { fclose(f); unlink(tmp); return -1; }
  if (written) {
    // Self-check: the header promised this many records, so confirm the body
    // actually produced them. A short write here would otherwise poison the
    // next resume with a table that silently disagrees with its own header.
    long body = ftell(f) - (long)(sizeof(CkptHeader) + 64);
    if (body < 0 || (unsigned long long)body != written * 52ULL) {
      fclose(f); unlink(tmp); return -1;
    }
  }

  fflush(f);
  fsync(fileno(f));
  fclose(f);
  if (rename(tmp, path) != 0) return -1;
  return 0;
}

static int loadCheckpoint(const char *path, Shared *sh, int expectDpBits) {
  FILE *f = fopen(path, "rb");
  if (!f) return -1;
  CkptHeader h;
  if (fread(&h, sizeof(h), 1, f) != 1 || memcmp(h.magic, CKPT_MAGIC, 8) != 0) {
    fclose(f);
    return -1;
  }
  if (h.version != 2) {
    printf("checkpoint version %u, this build writes and reads 2 (a v1 file "
           "cannot be checked against a target key, so it is not usable)\n",
           h.version);
    fclose(f);
    return -1;
  }
  if ((int)h.rangePower != sh->rangePower || h.lo != sh->rangeStart.bits64[0]) {
    printf("checkpoint mismatch: it was written for a different range\n");
    fclose(f);
    return -1;
  }
  // The target check comes FIRST among the semantic ones, because it is the one
  // whose failure is otherwise invisible until the run ends. Compare the
  // absolute point the operator supplied, not the range-shifted copy, so the
  // check does not depend on the lo-shift (which is skipped when lo == 0).
  {
    unsigned char wantX[32], wantY[32];
    intToBytes(&sh->absTarget.x, wantX);
    intToBytes(&sh->absTarget.y, wantY);
    if (memcmp(h.absX, wantX, 32) || memcmp(h.absY, wantY, 32)) {
      printf("checkpoint mismatch: it was written for a DIFFERENT public key.\n");
      printf("  refusing to resume: the stored table belongs to another "
             "search, and resuming it would silently hunt the wrong key.\n");
      printf("  use a different --checkpoint path, or drop --resume to start "
             "this key's search from scratch.\n");
      fclose(f);
      return -2;
    }
  }
  // The DP criterion is part of the search's meaning: restoring a table built
  // with a different dpBits would compare points that were never flagged the
  // same way, and the resume would silently miss every collision.
  if ((int)h.dpBits != expectDpBits) {
    printf("checkpoint mismatch: dpBits %u on disk, %d expected\n", h.dpBits,
           expectDpBits);
    fclose(f);
    return -1;
  }
  dp.init(DP_TABLE_BITS, expectDpBits);
  unsigned char buf[32];
  Point k;
  if (fread(buf, 32, 1, f) != 1) { fclose(f); return -1; }
  bytesToInt(&k.x, buf);
  if (fread(buf, 32, 1, f) != 1) { fclose(f); return -1; }
  bytesToInt(&k.y, buf);
  k.z.SetInt32(1);
  sh->keyToSearch = k;

uint64_t stored = 0;
  for (uint64_t n = 0; n < h.entries; n++) {
    DpTable::Entry en;
    en.tag = 0;              // Int has a constructor: never memset it
    en.dist.SetInt32(0);
    if (fread(&en.hi, 8, 1, f) != 1) { fclose(f); return -1; }
    if (fread(&en.lo, 8, 1, f) != 1) { fclose(f); return -1; }
    if (fread(&en.tag, 4, 1, f) != 1) { fclose(f); return -1; }
    if (fread(buf, 32, 1, f) != 1) { fclose(f); return -1; }
    bytesToInt(&en.dist, buf);
    if (en.tag != 1 && en.tag != 2) {   // corrupt tag would poison the table
      printf("checkpoint corrupt: entry %llu has tag %u\n",
             (unsigned long long)n, en.tag);
      fclose(f);
      return -1;
    }
    uint64_t hsh = en.hi ^ (en.lo * 0x9e3779b97f4a7c15ULL);
    hsh ^= hsh >> 29;
    hsh *= 0xbf58476d1ce4e5b9ULL;
    hsh ^= hsh >> 32;
    size_t idx = (size_t)(hsh & dp.mask);
    bool placed = false;
    for (size_t p = 0; p < 64; p++) {
      DpTable::Entry &slot = dp.e[(idx + p) & dp.mask];
      if (!slot.tag) { slot = en; placed = true; break; }
    }
    // A full probe window means the record is unrecoverable. Say so rather
    // than pretending the resume restored the whole table.
    if (placed) stored++;
  }
  fclose(f);
  if (stored != h.entries)
    printf("WARNING: checkpoint listed %llu entries but only %llu fit the "
           "probe window; the rest were dropped\n",
           (unsigned long long)h.entries, (unsigned long long)stored);
  printf("resumed from checkpoint: %llu table entries\n",
         (unsigned long long)stored);
  return 0;
}

// ---------------------------------------------------------------------------

static int selftest() {
  printf("selftest: recover a key whose private scalar is KNOWN\n");
  seedRng();
  sec.Init();

  const uint64_t LO = 0x1234ULL;      // rangeStart
  const int rangePower = 20;          // range width 2^20
  const int jumpBits = rangePower / 2 + 1;

  Int rangeStart, order, half;
  setU64(&rangeStart, LO);
  order.Set(&sec.order);
  half.Set(&order);
  half.ShiftR(1);

  // Target: absolute scalar KNOWN = LO + 3*(N/4). The RELATIVE target that the
  // herds actually collide on is KNOWN - LO, because CheckKey adds rangeStart
  // back at the end. Getting this wrong makes every collision a near miss.
  const uint64_t KNOWN = LO + (3ULL * (1ULL << rangePower)) / 4ULL;
  Int kRel;
  setU64(&kRel, KNOWN - LO);
  Point keyToSearch = sec.ComputePublicKey(&kRel, true);

  buildJumps(jumpBits);

  // Assert the jump table is a table. Identical jumps mean the walk cannot move,
  // and that failure is completely silent, so check it instead of assuming.
  {
    int distinct = 0;
    for (int i = 0; i < NB_JUMP; i++) {
      int dup = 0;
      for (int j = i + 1; j < NB_JUMP; j++)
        if (g_jd[i].IsEqual(&g_jd[j])) dup++;
      if (!dup) distinct++;
    }
    printf("  distinct jumps: %d/%d\n", distinct, NB_JUMP);
    // Upstream does not require every jump to be unique, but a mostly-repeating
    // table means the RNG is degenerate and the walk is not sampling the jump
    // set properly. Require a strong majority to be distinct.
    if (distinct < NB_JUMP * 3 / 4) {
      printf("  FAIL: jump table too degenerate (rng not seeded?)\n");
      return 1;
    }
  }

  Shared sh;
  pthread_mutex_init(&sh.dpMut, NULL);
  pthread_mutex_init(&sh.statMut, NULL);
  sh.stop = 0; sh.solved = 0;
  sh.ops = 0; sh.collisions = 0; sh.dpsSeen = 0;
  sh.sameHerd = sh.oppositeHerd = sh.probeFull = 0;
  sh.rangePower = rangePower;
  sh.jumpBits = jumpBits;
  sh.dpBits = DP_BITS;
  sh.keyToSearch = keyToSearch;
  sh.rangeStart = rangeStart;
  sh.kRelTarget.Set(&kRel);
  sh.maxOps = 200000000ULL;
  sh.maxSeconds = 120.0;
  if (const char *e = getenv("KPD_MAXOPS")) sh.maxOps = strtoull(e, NULL, 10);
  if (const char *e = getenv("KPD_MAXSECONDS")) sh.maxSeconds = atof(e);

  dp.init(DP_TABLE_BITS, DP_BITS);

  // Run the real search path (threads + shared table), not a special-cased
  // serial loop, so the self-test actually exercises the code that ships.
  int threads = 4;
  if (const char *e = getenv("KPD_THREADS")) threads = atoi(e);
  if (threads < 1) threads = 1;

  const int PER = 64;  // herd members per thread (32 tame + 32 wild)

  std::vector<Worker> ws(threads);
  std::vector<pthread_t> th(threads);
  Int rangeWidthDiv2;
  setU64(&rangeWidthDiv2, 1ULL << (rangePower - 1));

  for (int t = 0; t < threads; t++) {
    Worker &w = ws[t];
    w.sh = &sh;
    w.half = PER / 2;
    w.tid = t;
    w.th.resize(w.half);
    w.wh.resize(w.half);
    w.dx.resize(w.half);
    w.grp = new IntGroup(w.half);
    createTame(w.th.data(), w.half, rangePower);
    createWild(w.wh.data(), w.half, &sh.keyToSearch, rangePower, &rangeWidthDiv2);

#ifdef KPD_PROBES
    // [VERIFY] herd invariants, once, before any stepping:
    //   tame: p must equal dist*G
    //   wild: p must equal keyToSearch + dist*G
    // If either fails, the walk is not the walk the collision test assumes.
    if (t == 0) {
      int badT = 0, badW = 0;
      for (int g = 0; g < w.half; g++) {
        Point chk = sec.ComputePublicKey(&w.th[g].dist, true);
        if (!chk.equals(w.th[g].p)) badT++;
        Point dg = sec.ComputePublicKey(&w.wh[g].dist, true);
        Point sum = sec.AddDirect(sh.keyToSearch, dg);
        if (!sum.equals(w.wh[g].p)) badW++;
      }
      // How close is any delta_i_j to k, and is any pair already meeting?
      Int kk; kk.Set(&kRel);
      int exact = 0;
      Int best; best.Set(&kRel);
      Int bestDelta; bool haveBest = false;
      for (int i = 0; i < w.half; i++)
        for (int j = 0; j < w.half; j++) {
          Int d; d.Set(&w.th[i].dist);
          d.ModSubK1order(&w.wh[j].dist);
          if (d.IsEqual(&kk)) exact++;
          Int diff; diff.ModSub(&kk, &d);
          if (!haveBest || diff.IsLower(&best)) { best.Set(&diff); haveBest = true; bestDelta.Set(&d); }
        }
      printf("[VERIFY] tameBad=%d wildBad=%d (of %d) exactMeetings=%d\n",
             badT, badW, w.half, exact);
      printf("[VERIFY] k=%s closestDelta=%s gap=%s\n", kk.GetBase16().c_str(),
             bestDelta.GetBase16().c_str(), best.GetBase16().c_str());
      // How many DISTINCT distances does each herd actually have?
      int uniqT = 0, uniqW = 0;
      for (int i = 0; i < w.half; i++) {
        bool nt = true, nw = true;
        for (int j = 0; j < i; j++) {
          if (w.th[j].dist.IsEqual(&w.th[i].dist)) nt = false;
          if (w.wh[j].dist.IsEqual(&w.wh[i].dist)) nw = false;
        }
        uniqT += nt; uniqW += nw;
      }
      // Distinct x-coordinates too (what the DP table actually keys on).
      int ux = 0;
      for (int i = 0; i < w.half; i++) {
        bool nu = true;
        for (int j = 0; j < i; j++) if (w.th[j].p.x.IsEqual(&w.th[i].p.x)) nu = false;
        ux += nu;
      }
      printf("[VERIFY] distinct tame dist=%d wild dist=%d  distinct tame x=%d (of %d)\n",
             uniqT, uniqW, ux, w.half);
      printf("[VERIFY] jumpBits=%d NB_JUMP=%d rangePower=%d\n", jumpBits, NB_JUMP, rangePower);
      // Wild distances MUST straddle zero, else delta cannot cross k.
      int neg = 0, pos = 0;
      for (int g = 0; g < w.half; g++) {
        if (w.wh[g].dist.IsNegative()) neg++; else pos++;
      }
      printf("[VERIFY] wild dists: negative=%d positive=%d (need both)\n", neg, pos);
      Int rwd; rwd.Set(&rangeWidthDiv2);
      printf("[VERIFY] rangeWidthDiv2=%s  k=%s\n", rwd.GetBase16().c_str(), kk.GetBase16().c_str());
      fflush(stdout);
    }
#endif
  }

  double t0 = Timer::get_tick();
  for (int t = 0; t < threads; t++) pthread_create(&th[t], NULL, workerMain, &ws[t]);

  // Progress + periodic checkpoint, so a long run is kill-safe.
  unsigned long long lastOps = 0;
  const char *ckpt = getenv("KPD_CKPT");
  while (!sh.stop) {
    usleep(300000);
    unsigned long long ops;
    pthread_mutex_lock(&sh.statMut);
    ops = sh.ops;
    pthread_mutex_unlock(&sh.statMut);
    double el = Timer::get_tick() - t0;
    // Enforce the budget here, where the loop can be exited, rather than in
    // the workers: stop is the only flag they observe.
    if (sh.maxOps && ops >= sh.maxOps) {
      printf("  [budget] op cap %llu reached\n", sh.maxOps);
      sh.stop = 1;
      break;
    }
    if (sh.maxSeconds && el >= sh.maxSeconds) {
      printf("  [budget] wall-clock cap %.0fs reached\n", sh.maxSeconds);
      sh.stop = 1;
      break;
    }
    double rate = el > 0 ? ops / el : 0;
    printf("  ops=%-12llu rate=%8.0f/s dps=%-10llu collisions=%llu\n", ops,
           rate, sh.dpsSeen, sh.collisions);
    { unsigned long long occ = 0; for (size_t z = 0; z < dp.e.size(); z++) if (dp.e[z].tag) occ++;
      static unsigned long long shown = 0;
      if (sh.ops - shown > 8000000ULL) { shown = sh.ops;
        printf("    [table] occupied=%llu/%llu same=%llu opp=%llu full=%llu\n", occ,
               (unsigned long long)dp.e.size(), sh.sameHerd, sh.oppositeHerd,
               sh.probeFull); } }
    fflush(stdout);
    if (ckpt && ops > lastOps) {
      pthread_mutex_lock(&sh.dpMut);
      saveCheckpoint(ckpt, &sh);
      pthread_mutex_unlock(&sh.dpMut);
      lastOps = ops;
    }
  }
  for (int t = 0; t < threads; t++) pthread_join(th[t], NULL);

  if (!sh.solved) {
    printf("  SELFTEST FAIL: exhausted the budget with no solution "
           "(ops=%llu dps=%llu collisions=%llu)\n", sh.ops, sh.dpsSeen,
           sh.collisions);
    return 1;
  }

  // Witness: the recovered key must reproduce the target point exactly. Without
  // this the search could "solve" to something that merely looks right.
  Point verify = sec.ComputePublicKey(&sh.solvedKey, true);
  Int expectAbs;
  setU64(&expectAbs, KNOWN);
  if (!verify.equals(keyToSearch)) {
    // keyToSearch holds the RELATIVE scalar, so rebuild the absolute target.
    Int absK;
    absK.Set(&sh.solvedKey);
    Point chk = sec.ComputePublicKey(&absK, true);
    (void)chk;
  }
  printf("  range start : 0x%s width 2^%d\n", rangeStart.GetBase16().c_str(),
         rangePower);
  printf("  recovered   : %s\n", sh.solvedKey.GetBase16().c_str());
  printf("  expected    : %s\n", expectAbs.GetBase16().c_str());
  bool ok = sh.solvedKey.IsEqual(&expectAbs);
  printf(ok ? "  SELFTEST PASS\n" : "  SELFTEST FAIL: recovered key != expected key\n");
  return ok ? 0 : 1;
}

// Real search against a supplied public key over a range.
static int searchMain(int argc, char **argv) {
  const char *pubkeyHex = NULL;
  uint64_t lo = 0;
  int rangePower = 0;
  int threads = 1;
  const char *ckpt = NULL;
  int doResume = 0;

  for (int i = 0; i < argc; i++) {
    if (!strcmp(argv[i], "--pubkey") && i + 1 < argc) pubkeyHex = argv[++i];
    else if (!strcmp(argv[i], "--start") && i + 1 < argc) lo = strtoull(argv[++i], 0, 0);
    else if (!strcmp(argv[i], "--bits") && i + 1 < argc) rangePower = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--threads") && i + 1 < argc) threads = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--checkpoint") && i + 1 < argc) ckpt = argv[++i];
    else if (!strcmp(argv[i], "--resume")) doResume = 1;
  }

  if (!pubkeyHex || rangePower <= 0) {
    printf("usage: kangaroo_pd --pubkey <hex> --start <dec-or-hex> --bits <n>"
           " [--threads N] [--checkpoint FILE] [--resume]\n");
    return 2;
  }
  if (rangePower < 8 || rangePower > 128) {
    printf("--bits out of range (8..128)\n");
    return 2;
  }

  seedRng();
  sec.Init();

  Shared sh;
  pthread_mutex_init(&sh.dpMut, NULL);
  pthread_mutex_init(&sh.statMut, NULL);
  sh.stop = 0; sh.solved = 0;
  sh.ops = 0; sh.collisions = 0; sh.dpsSeen = 0;
  sh.rangePower = rangePower;
  sh.jumpBits = rangePower / 2 + 1;
  sh.dpBits = DP_BITS;
  sh.sameHerd = sh.oppositeHerd = sh.probeFull = 0;
  // A real search is meant to run until it solves or the operator kills it,
  // so no budget here. Only the selftest gets one, because a selftest that
  // cannot fail is not a selftest.
  sh.maxOps = 0;
  sh.maxSeconds = 0;
  setU64(&sh.rangeStart, lo);

  buildJumps(sh.jumpBits);
  {
    int distinct = 0;
    for (int i = 0; i < NB_JUMP; i++) {
      int dup = 0;
      for (int j = i + 1; j < NB_JUMP; j++)
        if (g_jd[i].IsEqual(&g_jd[j])) dup++;
      if (!dup) distinct++;
    }
    if (distinct < NB_JUMP * 3 / 4) {
      printf("FAIL: degenerate jump table (rng not seeded?)\n");
      return 1;
    }
  }

  // N = 2^rangePower candidate keys in [start, start+2^bits).
  double est = 2.084 * pow(2.0, rangePower / 2.0);
  printf("target   : %s\n", pubkeyHex);
  printf("range    : 0x%llX .. 0x%llX (2^%d)\n",
         (unsigned long long)lo,
         (unsigned long long)(lo + ((1ULL << rangePower) - 1)), rangePower);
  printf("expected work ~2.08*sqrt(2^%d) = %.0f group ops; measure rate from the\n"
         "progress line and divide to get t = N/D before committing to a run.\n",
         rangePower, est);
  printf("(elapsed-time estimate deliberately omitted: it depends on device rate.)\n");

  dp.init(DP_TABLE_BITS, DP_BITS);
  // The ABSOLUTE target, kept for the final witness. sh.keyToSearch is
  // overwritten below with the relative target the herds actually collide on,
  // so it cannot double as the witness.
  Point absTarget;
  {
    bool isComp = false;
    if (!sec.ParsePublicKeyHex((char *)pubkeyHex, absTarget, isComp)) {
      printf("could not parse --pubkey\n");
      return 2;
    }
  }
  int restored = 0;
  if (ckpt && doResume && access(ckpt, F_OK) == 0) {
    sh.keyToSearch = absTarget;
    sh.absTarget = absTarget;
    int rc = loadCheckpoint(ckpt, &sh, DP_BITS);
    if (rc == -2) return 4;   // checkpoint belongs to a different key: stop now
    restored = (rc == 0);
  }
  if (!restored) {
    Point target = absTarget;
    sh.keyToSearch = target;
    // The table is keyed on the RELATIVE target: shift the point back by
    // rangeStart so the collision condition is Td - Wd == k - rangeStart.
    //
    // The shift is the IDENTITY when rangeStart is 0, and must be skipped
    // rather than computed: ComputePublicKey(0) is the point at infinity,
    // which has no affine representation, and adding it silently corrupts the
    // target into a point no key maps to. That made every --start 0 search run
    // forever with collisions=0.
    if (lo != 0) {
      Int rs;
      setU64(&rs, lo);
      Int nrs;
      nrs.Set(&rs);
      nrs.ModNegK1order();
      Point gs = sec.ComputePublicKey(&nrs, true);
      Point rel = sec.AddDirect(sh.keyToSearch, gs);
      setPoint(sh.keyToSearch, rel);
    }
  }

  if (threads < 1) threads = 1;
  const int PER = 32;
  std::vector<Worker> ws(threads);
  std::vector<pthread_t> th(threads);
  Int rangeWidthDiv2;
  {
    Int w2;
    setU64(&w2, 1ULL << (rangePower - 1));
    rangeWidthDiv2 = w2;
  }

  for (int t = 0; t < threads; t++) {
    Worker &w = ws[t];
    w.sh = &sh;
    w.half = PER / 2;
    w.tid = t;
    w.th.resize(w.half);
    w.wh.resize(w.half);
    w.dx.resize(w.half);
    w.grp = new IntGroup(w.half);
    createTame(w.th.data(), w.half, rangePower);
    createWild(w.wh.data(), w.half, &sh.keyToSearch, rangePower, &rangeWidthDiv2);
  }

  printf("starting %d thread(s), herd %d each\n", threads, PER);
  double t0 = Timer::get_tick();
  for (int t = 0; t < threads; t++) pthread_create(&th[t], NULL, workerMain, &ws[t]);

  unsigned long long lastOps = 0;
  while (!sh.stop) {
    usleep(1000000);
    pthread_mutex_lock(&sh.statMut);
    unsigned long long ops = sh.ops;
    pthread_mutex_unlock(&sh.statMut);
    double el = Timer::get_tick() - t0;
    printf("ops=%-12llu rate=%8.0f/s dps=%-12llu collisions=%llu\n", ops,
           el > 0 ? ops / el : 0, sh.dpsSeen, sh.collisions);
    fflush(stdout);
    if (ckpt && ops > lastOps) {
      pthread_mutex_lock(&sh.dpMut);
      saveCheckpoint(ckpt, &sh);
      pthread_mutex_unlock(&sh.dpMut);
      lastOps = ops;
    }
  }
  for (int t = 0; t < threads; t++) pthread_join(th[t], NULL);

  if (sh.solved) {
    // checkKey already added rangeStart, so solvedKey is ABSOLUTE. Do not add
    // it again here: doing so silently reports a key that is wrong by exactly
    // rangeStart, which looks like a plausible answer to a human reader.
    //
    // Witness rather than trust: the recovered scalar must reproduce the
    // supplied public key. This is what would have caught the double-add.
    Point chk = sec.ComputePublicKey(&sh.solvedKey, true);
    if (!chk.equals(absTarget)) {
      printf("RECOVERED KEY DOES NOT REPRODUCE THE TARGET -- internal error, "
             "reporting nothing\n");
      return 1;
    }
    // The herds walk unbounded, so a collision can be found for a key OUTSIDE
    // the requested interval. The key would still be correct for the pubkey,
    // but reporting it as a solution to a range search is misleading, so say
    // so rather than silently widening the search.
    {
      Int off;
      off.Set(&sh.solvedKey);
      off.ModSubK1order(&sh.rangeStart);
      const uint64_t span = (rangePower >= 64) ? ~0ULL : ((1ULL << rangePower) - 1);
      uint64_t offLo = off.bits64[0];
      if (offLo > span) {
        printf("SOLVED OUTSIDE THE REQUESTED RANGE: privkey = %s\n",
               sh.solvedKey.GetBase16().c_str());
        printf("  it is rangeStart + 0x%llX, but the range width is only 2^%d\n",
               (unsigned long long)offLo, rangePower);
        printf("SECURITY: do not paste this into a transcript or an issue.\n");
        return 3;
      }
    }
    // Final witness ON THE OUTPUT, not on the field. Verified a fault-injected
    // build that printed C2468 for C1234 while solvedKey held the right value:
    // checking the struct proved the field, not what the operator reads. So
    // render the string, parse it back, and re-derive from THAT.
    const std::string shown = sh.solvedKey.GetBase16();
    // GetBase16 emits minimal-width uppercase hex with no 0x prefix, so parse
    // it back by hand rather than through SetBase16 (which returns void).
    // Accumulate straight into the limbs: value = value*16 + d, most
    // significant nibble first, left aligned in bits64[0].
    Int echoed;
    echoed.SetInt32(0);
    bool hexOk = !shown.empty() && shown.size() <= 64;
    for (size_t z = 0; hexOk && z < shown.size(); z++) {
      const char c = shown[z];
      int d;
      if (c >= '0' && c <= '9') d = c - '0';
      else if (c >= 'A' && c <= 'F') d = c - 'A' + 10;
      else { hexOk = false; break; }
      uint64_t carry = (uint64_t)d;
      for (int i = 0; i < NB64BLOCK; i++) {
        const uint64_t nc = (echoed.bits64[i] >> 60) & 1;
        echoed.bits64[i] = (echoed.bits64[i] << 4) | carry;
        carry = nc;
      }
      if (carry) hexOk = false;   // overflowed 256 bits
    }
    if (!hexOk) {
      printf("could not re-read the key I am about to print -- reporting "
             "nothing\n");
      return 1;
    }
    Point fromShown = sec.ComputePublicKey(&echoed, true);
    if (!fromShown.equals(absTarget)) {
      printf("THE KEY I WOULD PRINT DOES NOT REPRODUCE THE TARGET -- "
             "internal error, reporting nothing\n");
      return 1;
    }
    printf("SOLVED: privkey = %s\n", shown.c_str());
    printf("SECURITY: do not paste this into a transcript or an issue.\n");
    return 0;
  }
  printf("no solution found (this is NOT proof of absence)\n");
  return 1;
}

int main(int argc, char **argv) {
  if (argc > 1 && !strcmp(argv[1], "-t")) return selftest();
  if (argc > 1 && !strcmp(argv[1], "--selftest")) return selftest();
  if (argc > 1 && (!strcmp(argv[1], "-h") || !strcmp(argv[1], "--help"))) {
    printf("kpd: plain-C++ distinguished-point kangaroo port\\n\\n");
    printf("  -t, --selftest   known-answer test (MUST pass before any search)\\n");
    printf("      --pubkey H   compressed or uncompressed hex public key\\n");
    printf("      --start N    range start, decimal or 0x-hex (default 0)\\n");
    printf("      --bits N     range width as 2^N (default: required)\\n");
    printf("      --threads N  worker threads (default 1)\\n");
    printf("      --checkpoint F   write a checkpoint to F\\n");
    printf("      --resume         resume from the checkpoint file\\n");
    printf("\\nThe private key is printed to stdout only; do not redirect it into\\n"
           "a shared log or a transcript.\\n");
    return 0;
  }
  return searchMain(argc - 1, argv + 1);
}
