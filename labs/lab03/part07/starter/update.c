#include "pss.h"

int process_update(EVP_PKEY *key, const unsigned char *message, size_t message_len,
                   const unsigned char *signature, size_t signature_len) {
    (void)key; (void)message; (void)message_len;
    (void)signature; (void)signature_len;
    /* TODO: call verify_message; process the update only after verification
     * succeeds. Invalid signatures, malformed inputs, and API errors reject.
     */
    return 0;
}
