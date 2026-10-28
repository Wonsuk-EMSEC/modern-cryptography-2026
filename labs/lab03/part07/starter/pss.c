#include "pss.h"
#include <openssl/rsa.h>

int sign_message(EVP_PKEY *key, const unsigned char *message, size_t message_len,
                 unsigned char **signature, size_t *signature_len) {
    (void)key; (void)message; (void)message_len;
    *signature = NULL; *signature_len = 0;
    /* TODO: EVP_DigestSign* with explicit PSS/MGF1/SHA256/salt32 settings.
     * Query required signature size, allocate, then sign. Check every result.
     */
    return 0;
}

int verify_message(EVP_PKEY *key, const unsigned char *message, size_t message_len,
                   const unsigned char *signature, size_t signature_len) {
    (void)key; (void)message; (void)message_len;
    (void)signature; (void)signature_len;
    /* TODO: EVP_DigestVerify* with the same explicit parameters.
     * Preserve the distinction between valid (1), invalid (0), and error (-1).
     */
    return -1;
}
