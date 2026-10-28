/* Deliberately vulnerable update policy for local analysis. */
#include "pss.h"

int process_update(EVP_PKEY *key, const unsigned char *message, size_t message_len,
                   const unsigned char *signature, size_t signature_len) {
    int result = verify_message(key, message, message_len, signature, signature_len);
    if (result < 0) return 0;
    /* BUG: a normal verification failure (0) reaches the update action. */
    return 1; /* Simulated update processing; never executes package contents. */
}
