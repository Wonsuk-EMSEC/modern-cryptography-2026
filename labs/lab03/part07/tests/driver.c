/* File I/O and an inert update action; submitted packages are never executed. */
#include "pss.h"
#include <openssl/pem.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int inject_error;
int __real_EVP_DigestVerifyFinal(EVP_MD_CTX *, const unsigned char *, size_t);
int __wrap_EVP_DigestVerifyFinal(EVP_MD_CTX *ctx, const unsigned char *sig, size_t len) {
    if (inject_error) return -1;
    return __real_EVP_DigestVerifyFinal(ctx, sig, len);
}
static unsigned char *read_file(const char *path, size_t *n) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    unsigned char *p = OPENSSL_malloc(1048577);
    if (!p) { fclose(f); return NULL; }
    *n = fread(p, 1, 1048577, f);
    int bad = ferror(f) || *n > 1048576;
    fclose(f);
    if (bad) { OPENSSL_free(p); return NULL; }
    return p;
}
int main(int argc, char **argv) {
    if (argc != 5) { fprintf(stderr, "usage: driver sign|verify|update|update-error key message signature\n"); return 2; }
    int signing = strcmp(argv[1], "sign") == 0;
    FILE *kf = fopen(argv[2], "rb");
    if (!kf) return 2;
    EVP_PKEY *key = signing ? PEM_read_PrivateKey(kf, NULL, NULL, NULL) : PEM_read_PUBKEY(kf, NULL, NULL, NULL);
    fclose(kf);
    if (!key) { puts("REJECT"); return 1; }
    size_t mlen = 0, slen = 0;
    unsigned char *msg = read_file(argv[3], &mlen), *sig = NULL;
    int code = 2;
    if (!msg) goto done;
    if (signing) {
        if (sign_message(key, msg, mlen, &sig, &slen) != 1 || !sig || slen != 256) goto done;
        FILE *sf = fopen(argv[4], "wb");
        if (!sf) goto done;
        int ok = fwrite(sig, 1, slen, sf) == slen;
        if (fclose(sf) != 0) ok = 0;
        if (!ok) goto done;
        puts("SIGNED"); code = 0;
    } else {
        sig = read_file(argv[4], &slen);
        if (!sig) goto done;
        inject_error = strcmp(argv[1], "update-error") == 0 || strcmp(argv[1], "verify-error") == 0;
        if (strcmp(argv[1], "verify") == 0 || strcmp(argv[1], "verify-error") == 0) {
            printf("%d\n", verify_message(key, msg, mlen, sig, slen));
        } else {
            puts(process_update(key, msg, mlen, sig, slen) == 1 ? "ACCEPT" : "REJECT");
        }
        code = 0;
    }
done:
    OPENSSL_free(msg); OPENSSL_free(sig); EVP_PKEY_free(key);
    return code;
}
