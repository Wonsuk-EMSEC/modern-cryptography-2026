#include <openssl/rand.h>

/* Return 1 only if BOTH cryptographic RNG operations succeed, else 0.
 * Do not implement a fallback, seed OpenSSL from time(), or call rand().
 * The caller must abort before encryption if this function returns 0.
 */
int generate_key_iv(unsigned char key[16], unsigned char iv[16]) {
    (void)key; (void)iv;
    /* TODO: RAND_priv_bytes(key, 16), RAND_bytes(iv, 16), return-value checks. */
    return 0;
}
