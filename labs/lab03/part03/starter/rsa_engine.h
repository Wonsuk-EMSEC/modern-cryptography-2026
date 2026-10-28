#ifndef LAB03_RSA_ENGINE_H
#define LAB03_RSA_ENGINE_H
#include <openssl/bn.h>
#include <stddef.h>

typedef struct {
    BIGNUM *p, *q, *n, *e, *d, *dp, *dq, *qinv;
} LabRSA;

/* All BIGNUM fields are allocated by the driver. Input p,q are supplied
 * distinct primes, e=65537. Return 1 on success, 0 on any failure.
 * Use phi=(p-1)(q-1) to calculate d. Do not replace supplied p,q,e.
 */
int rsa_derive(LabRSA *key, BN_CTX *ctx);
int rsa_encrypt(BIGNUM *out, const BIGNUM *message, const LabRSA *key, BN_CTX *ctx);
int rsa_decrypt_direct(BIGNUM *out, const BIGNUM *ciphertext, const LabRSA *key, BN_CTX *ctx);
int rsa_decrypt_crt(BIGNUM *out, const BIGNUM *ciphertext, const LabRSA *key, BN_CTX *ctx);

/* Provided allocation, file and byte helpers contain no RSA calculations. */
int lab_rsa_init(LabRSA *key);
void lab_rsa_clear(LabRSA *key);
int lab_read_primes(const char *path, LabRSA *key);
BIGNUM *lab_from_bytes(const unsigned char *data, size_t length);
int lab_to_bytes(const BIGNUM *value, unsigned char *out, size_t length);
#endif
