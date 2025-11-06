#include <stdio.h>
#include <string.h>
#include "../include/dgt/dgt_semantic.h"

/* ------------------------------------------------------------------
 *  Ecosystem state – simple struct for demo
 * ------------------------------------------------------------------*/
typedef struct {
    char name[32];
    int  carbon;
    int  oxygen;
} Ecosystem;

/* ------------------------------------------------------------------
 *  Top-down: compress carbon (interior → exterior)
 * ------------------------------------------------------------------*/
void* compress_ecosystem(void* s)
{
    Ecosystem* e = (Ecosystem*)s;
    if (e->carbon >= 10) {
        e->carbon -= 10;
        printf("[IN]  compress: carbon %d → %d\n", e->carbon + 10, e->carbon);
        return s;
    }
    return NULL;   /* fail */
}

/* ------------------------------------------------------------------
 *  Bottom-up: release oxygen (exterior → interior)
 * ------------------------------------------------------------------*/
void* release_oxygen(void* s)
{
    Ecosystem* e = (Ecosystem*)s;
    e->oxygen += 5;
    printf("[OUT] release: oxygen → %d\n", e->oxygen);
    return s;
}

/* ------------------------------------------------------------------
 *  Bind the directed semantics (file scope!)
 * ------------------------------------------------------------------*/
DGT_IN_BIND (compress, compress_ecosystem);
DGT_OUT_BIND(oxygen,  release_oxygen);
