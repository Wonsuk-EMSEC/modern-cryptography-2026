/* Original vulnerable program, included for analysis. Never use for real data.
 * Format: magic[8] = "LAB03E1\n", IV[16], AES-128-CBC ciphertext (PKCS#7).
 * glibc rand(), not Python random(), defines this challenge's byte stream.
 */
#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s input.pdf output.enc\n", argv[0]); return 2; }
    unsigned char key[16], iv[16], in[4096], out[4096 + EVP_MAX_BLOCK_LENGTH];
    srand((unsigned int)time(NULL));
    for (int i = 0; i < 16; ++i) key[i] = (unsigned char)(rand() % 256);
    for (int i = 0; i < 16; ++i) iv[i] = (unsigned char)(rand() % 256);
    FILE *src = fopen(argv[1], "rb"), *dst = NULL;
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int ok = 0, n = 0; size_t got;
    if (!src || !ctx || !(dst = fopen(argv[2], "wb"))) goto done;
    if (fwrite("LAB03E1\n", 1, 8, dst) != 8 || fwrite(iv, 1, 16, dst) != 16 ||
        EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv) != 1) goto done;
    while ((got = fread(in, 1, sizeof(in), src)) != 0) {
        if (EVP_EncryptUpdate(ctx, out, &n, in, (int)got) != 1 ||
            fwrite(out, 1, (size_t)n, dst) != (size_t)n) goto done;
    }
    if (ferror(src) || EVP_EncryptFinal_ex(ctx, out, &n) != 1 ||
        fwrite(out, 1, (size_t)n, dst) != (size_t)n) goto done;
    ok = 1;
done:
    if (src) fclose(src);
    if (dst && fclose(dst) != 0) ok = 0;
    EVP_CIPHER_CTX_free(ctx);
    OPENSSL_cleanse(key, sizeof(key));
    if (!ok) { remove(argv[2]); fprintf(stderr, "encryption failed\n"); return 1; }
    puts("Encrypted report written");
    return 0;
}
