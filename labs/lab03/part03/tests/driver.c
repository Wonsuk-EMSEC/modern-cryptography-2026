/* Trusted local feedback driver: independent answers, wrapped operation
 * checks, fresh inputs, and median timing. No CRT reconstruction is provided.
 */
#define _POSIX_C_SOURCE 200809L
#include "rsa_engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define ROUNDS 9
#define BATCH 4
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL: %s (line %d)\n",#x,__LINE__); goto fail; } } while(0)
static const LabRSA *active_key;
static const BIGNUM *active_input;
static int stage=0, calls=0, saw_p=0, saw_q=0, bad_operation=0;

int __real_BN_mod_exp(BIGNUM *,const BIGNUM *,const BIGNUM *,const BIGNUM *,BN_CTX *);
int __wrap_BN_mod_exp(BIGNUM *r,const BIGNUM *a,const BIGNUM *e,const BIGNUM *m,BN_CTX *ctx) {
    if (stage) {
        calls++;
        if (BN_cmp(a,active_input)!=0) bad_operation=1;
        if (stage==1 && (BN_cmp(e,active_key->e)!=0 || BN_cmp(m,active_key->n)!=0)) bad_operation=1;
        if (stage==2 && (BN_cmp(e,active_key->d)!=0 || BN_cmp(m,active_key->n)!=0)) bad_operation=1;
        if (stage==3) {
            if (BN_cmp(e,active_key->dp)==0 && BN_cmp(m,active_key->p)==0) saw_p++;
            else if (BN_cmp(e,active_key->dq)==0 && BN_cmp(m,active_key->q)==0) saw_q++;
            else bad_operation=1;
        }
    }
    return __real_BN_mod_exp(r,a,e,m,ctx);
}

static uint64_t now_ns(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC,&t)!=0) abort();
    return (uint64_t)t.tv_sec*1000000000ULL+(uint64_t)t.tv_nsec;
}

static int compare_double(const void *a,const void *b) {
    double x=*(const double *)a,y=*(const double *)b;
    return (x>y)-(x<y);
}

static double median(double *values) {
    qsort(values,ROUNDS,sizeof(double),compare_double);
    return values[ROUNDS/2];
}

static int invoke(int kind,BIGNUM *out,const BIGNUM *in,const LabRSA *key,BN_CTX *ctx) {
    active_key=key; active_input=in;
    calls=saw_p=saw_q=bad_operation=0;
    stage=kind;
    int ok=kind==1 ? rsa_encrypt(out,in,key,ctx) :
        kind==2 ? rsa_decrypt_direct(out,in,key,ctx) : rsa_decrypt_crt(out,in,key,ctx);
    stage=0;
    return ok==1 && !bad_operation && calls==(kind==3 ? 2:1)
        && (kind!=3 || (saw_p==1 && saw_q==1));
}

static int validate_key(const LabRSA *k,BN_CTX *ctx) {
    int ok=0;
    BN_CTX_start(ctx);
    BIGNUM *pm=BN_CTX_get(ctx),*qm=BN_CTX_get(ctx),*phi=BN_CTX_get(ctx),*tmp=BN_CTX_get(ctx);
    if (!tmp || !BN_copy(pm,k->p) || !BN_copy(qm,k->q) || !BN_sub_word(pm,1) || !BN_sub_word(qm,1)) goto end;
    if (!BN_mul(tmp,k->p,k->q,ctx) || BN_cmp(tmp,k->n)!=0 || !BN_is_word(k->e,65537)) goto end;
    if (!BN_mul(phi,pm,qm,ctx) || !BN_mod_mul(tmp,k->e,k->d,phi,ctx) || !BN_is_one(tmp)) goto end;
    if (BN_is_negative(k->d) || BN_is_zero(k->d) || BN_cmp(k->d,phi)>=0) goto end;
    if (!BN_mod(tmp,k->d,pm,ctx) || BN_cmp(tmp,k->dp)!=0) goto end;
    if (!BN_mod(tmp,k->d,qm,ctx) || BN_cmp(tmp,k->dq)!=0) goto end;
    if (!BN_mod_mul(tmp,k->q,k->qinv,k->p,ctx) || !BN_is_one(tmp)) goto end;
    ok=1;
end:
    BN_CTX_end(ctx);
    return ok;
}

static int invalid_inputs(const LabRSA *key,BN_CTX *ctx) {
    BIGNUM *x=BN_dup(key->n),*out=BN_new();
    if (!x || !out) { BN_free(x); BN_free(out); return 0; }
    int ok=!rsa_encrypt(out,x,key,ctx) && !rsa_decrypt_direct(out,x,key,ctx) && !rsa_decrypt_crt(out,x,key,ctx);
    BN_one(x); BN_set_negative(x,1);
    ok=ok && !rsa_encrypt(out,x,key,ctx) && !rsa_decrypt_direct(out,x,key,ctx) && !rsa_decrypt_crt(out,x,key,ctx);
    BN_free(x); BN_free(out);
    return ok;
}

int main(int argc,char **argv) {
    LabRSA k={0};
    BN_CTX *ctx=BN_CTX_new();
    BIGNUM *message=BN_new(),*cipher=BN_new(),*out=BN_new(),*tmp=BN_new();
    BIGNUM *saved_p=NULL,*saved_q=NULL;
    double direct[ROUNDS],crt[ROUNDS],baseline[ROUNDS],split[ROUNDS];
    CHECK(argc==2 && ctx && message && cipher && out && tmp && lab_rsa_init(&k));
    CHECK(lab_read_primes(argv[1],&k));
    CHECK(BN_num_bits(k.p)>=1024 && BN_num_bits(k.q)>=1024);
    saved_p=BN_dup(k.p); saved_q=BN_dup(k.q);
    CHECK(saved_p && saved_q && rsa_derive(&k,ctx)==1);
    CHECK(BN_cmp(saved_p,k.p)==0 && BN_cmp(saved_q,k.q)==0 && validate_key(&k,ctx));
    CHECK(invalid_inputs(&k,ctx));
    /* Algebraic edge cases include messages divisible by a prime. */
    for (int i=0;i<12;i++) {
        if (i==0) BN_zero(message);
        else if (i==1) CHECK(BN_one(message));
        else if (i==2) { CHECK(BN_copy(message,k.n)); CHECK(BN_sub_word(message,1)); }
        else if (i==3) CHECK(BN_copy(message,k.p));
        else if (i==4) CHECK(BN_copy(message,k.q));
        else CHECK(BN_priv_rand_range(message,k.n));
        CHECK(__real_BN_mod_exp(cipher,message,k.e,k.n,ctx));
        CHECK(invoke(1,out,message,&k,ctx) && BN_cmp(out,cipher)==0);
        CHECK(invoke(2,out,cipher,&k,ctx) && BN_cmp(out,message)==0);
        CHECK(invoke(3,out,cipher,&k,ctx) && BN_cmp(out,message)==0);
    }
    /* Key generation, RNG, input preparation, correctness checks and IO are
     * outside every timed interval. Each callback receives a new ciphertext.
     * Warm-up pass is discarded. Rotate measurements to reduce drift.
     */
    for (int round=-1;round<ROUNDS;round++) {
        double accum[4]={0,0,0,0};
        for (int slot=0;slot<4;slot++) {
            int mode=(slot+(round+1))%4;
            for (int j=0;j<BATCH;j++) {
                CHECK(BN_priv_rand_range(message,k.n));
                CHECK(__real_BN_mod_exp(cipher,message,k.e,k.n,ctx));
                uint64_t start=now_ns();
                int ok;
                if (mode==0) ok=invoke(2,out,cipher,&k,ctx);
                else if (mode==1) ok=invoke(3,out,cipher,&k,ctx);
                else if (mode==2) ok=__real_BN_mod_exp(out,cipher,k.d,k.n,ctx);
                else ok=__real_BN_mod_exp(out,cipher,k.dp,k.p,ctx) && __real_BN_mod_exp(tmp,cipher,k.dq,k.q,ctx);
                uint64_t elapsed=now_ns()-start;
                CHECK(ok);
                if (mode!=3) CHECK(BN_cmp(out,message)==0);
                accum[mode]+=(double)elapsed/BATCH;
            }
        }
        if (round>=0) { direct[round]=accum[0]; crt[round]=accum[1]; baseline[round]=accum[2]; split[round]=accum[3]; }
    }
    double d=median(direct),c=median(crt),b=median(baseline),s=median(split);
    double calibrated=b/s;
    CHECK(calibrated>1.05);
    double required=1.0+0.35*(calibrated-1.0);
    CHECK(d<=b*1.8 && c<=s*1.8 && d/c>=required);
    printf("{\"bits\":%d,\"direct_ns\":%.0f,\"crt_ns\":%.0f,\"baseline_direct_ns\":%.0f,\"baseline_split_ns\":%.0f,\"speedup\":%.3f,\"required_speedup\":%.3f}\n",
           BN_num_bits(k.n),d,c,b,s,d/c,required);
    BN_free(saved_p); BN_free(saved_q); BN_clear_free(message); BN_clear_free(cipher); BN_clear_free(out); BN_clear_free(tmp);
    lab_rsa_clear(&k); BN_CTX_free(ctx);
    return 0;
fail:
    BN_free(saved_p); BN_free(saved_q); BN_clear_free(message); BN_clear_free(cipher); BN_clear_free(out); BN_clear_free(tmp);
    lab_rsa_clear(&k); BN_CTX_free(ctx);
    return 1;
}
