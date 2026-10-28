/* Independent test caller: encryption must never happen after RNG failure. */
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int generate_key_iv(unsigned char key[16], unsigned char iv[16]);
int __real_RAND_priv_bytes(unsigned char *, int);
int __real_RAND_bytes(unsigned char *, int);
static int mode, priv_calls, public_calls;

int __wrap_RAND_priv_bytes(unsigned char *p, int n) {
    ++priv_calls;
    if (n != 16) return 0;
    if (mode == 1) return 0;
    if (mode == 3) return -1;
    return __real_RAND_priv_bytes(p, n);
}
int __wrap_RAND_bytes(unsigned char *p, int n) {
    ++public_calls;
    if (n != 16) return 0;
    if (mode == 2) return 0;
    if (mode == 4) return -1;
    return __real_RAND_bytes(p, n);
}
static void hex(const char *name, const unsigned char *p, int n) {
    printf("%s ", name);
    for (int i = 0; i < n; ++i) printf("%02x", p[i]);
    putchar('\n');
}
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    mode = atoi(argv[1]);
    unsigned char key[16] = {0}, iv[16] = {0}, message[4096], cipher[4128];
    if (generate_key_iv(key, iv) != 1) { puts("RNG_REJECTED"); return 1; }
    if (priv_calls != 1 || public_calls != 1) { puts("WRONG_RNG_API"); return 2; }
    FILE *f = fopen(argv[2], "rb");
    if (!f) return 2;
    size_t size = fread(message, 1, sizeof(message), f);
    int bad = ferror(f) || !feof(f); fclose(f);
    if (bad) return 2;
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int n = 0, final = 0;
    if (!ctx || EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv) != 1 ||
        EVP_EncryptUpdate(ctx, cipher, &n, message, (int)size) != 1 ||
        EVP_EncryptFinal_ex(ctx, cipher+n, &final) != 1) { EVP_CIPHER_CTX_free(ctx); return 2; }
    EVP_CIPHER_CTX_free(ctx);
    hex("KEY", key, 16); hex("IV", iv, 16); hex("CIPHER", cipher, n+final);
    OPENSSL_cleanse(key, sizeof(key));
    return 0;
}
