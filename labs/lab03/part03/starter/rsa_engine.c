#include "rsa_engine.h"

int rsa_derive(LabRSA *key, BN_CTX *ctx) {
    /* TODO: n, phi, d, dp, dq, qinv; check every API return value. */
    (void)key; (void)ctx;
    return 0;
}

int rsa_encrypt(BIGNUM *out, const BIGNUM *message, const LabRSA *key, BN_CTX *ctx) {
    /* TODO: reject message outside [0,n), then call BN_mod_exp once. */
    (void)out; (void)message; (void)key; (void)ctx;
    return 0;
}

int rsa_decrypt_direct(BIGNUM *out, const BIGNUM *ciphertext, const LabRSA *key, BN_CTX *ctx) {
    /* TODO: reject ciphertext outside [0,n); one BN_mod_exp with d,n. */
    (void)out; (void)ciphertext; (void)key; (void)ctx;
    return 0;
}

int rsa_decrypt_crt(BIGNUM *out, const BIGNUM *ciphertext, const LabRSA *key, BN_CTX *ctx) {
    /* TODO: two BN_mod_exp calls with dp,p and dq,q; reconstruct with CRT.
     * Use BN_mod_sub/BN_mod_mul to handle negative residue differences.
     */
    (void)out; (void)ciphertext; (void)key; (void)ctx;
    return 0;
}
