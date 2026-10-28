#ifndef LAB03_PSS_H
#define LAB03_PSS_H
#include <openssl/evp.h>
#include <stddef.h>

/* sign_message: 1 success, 0 failure; allocated signature freed with OPENSSL_free.
 * verify_message: 1 valid, 0 invalid, -1 API/input error.
 * Scheme: RSA-2048, PSS, SHA-256, MGF1-SHA-256, salt length exactly 32.
 */
int sign_message(EVP_PKEY *, const unsigned char *, size_t, unsigned char **, size_t *);
int verify_message(EVP_PKEY *, const unsigned char *, size_t, const unsigned char *, size_t);
int process_update(EVP_PKEY *, const unsigned char *, size_t, const unsigned char *, size_t);
#endif
