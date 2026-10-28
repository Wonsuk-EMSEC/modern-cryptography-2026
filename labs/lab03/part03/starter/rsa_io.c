#include "rsa_engine.h"
#include <limits.h>
#include <stdio.h>
#include <string.h>

int lab_rsa_init(LabRSA *key) {
    memset(key, 0, sizeof(*key));
    key->p=BN_new(); key->q=BN_new(); key->n=BN_new(); key->e=BN_new();
    key->d=BN_new(); key->dp=BN_new(); key->dq=BN_new(); key->qinv=BN_new();
    return key->p && key->q && key->n && key->e && key->d && key->dp && key->dq && key->qinv
        && BN_set_word(key->e,65537);
}

void lab_rsa_clear(LabRSA *key) {
    BN_clear_free(key->p); BN_clear_free(key->q); BN_clear_free(key->n); BN_clear_free(key->e);
    BN_clear_free(key->d); BN_clear_free(key->dp); BN_clear_free(key->dq); BN_clear_free(key->qinv);
    memset(key, 0, sizeof(*key));
}

int lab_read_primes(const char *path, LabRSA *key) {
    char phex[2048], qhex[2048], extra[2];
    FILE *fp=fopen(path,"r");
    if (!fp) return 0;
    int count=fscanf(fp,"%2047s %2047s %1s",phex,qhex,extra);
    fclose(fp);
    if (count != 2) return 0;
    size_t pn=strlen(phex), qn=strlen(qhex);
    if (strspn(phex,"0123456789abcdefABCDEF")!=pn || strspn(qhex,"0123456789abcdefABCDEF")!=qn)
        return 0;
    return BN_hex2bn(&key->p,phex)>0 && BN_hex2bn(&key->q,qhex)>0;
}

BIGNUM *lab_from_bytes(const unsigned char *data, size_t length) {
    if (length>INT_MAX) return NULL;
    return BN_bin2bn(data,(int)length,NULL);
}

int lab_to_bytes(const BIGNUM *value, unsigned char *out, size_t length) {
    if (length>INT_MAX || BN_is_negative(value)) return 0;
    return BN_bn2binpad(value,out,(int)length)==(int)length;
}
