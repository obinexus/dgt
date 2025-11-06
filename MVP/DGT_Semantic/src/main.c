#include <stdio.h>
#include "../include/dgt/dgt_semantic.h"
#include "ecosystem.c"   /* pulls in bindings + functors */

int main(void)
{
    /* Allocate and initialize state */
    void* world = DGT_STATE_NEW(Ecosystem);
    Ecosystem* e = (Ecosystem*)world;
    strcpy(e->name, "Earth-v1");
    e->carbon = 50;
    e->oxygen = 0;

    printf("=== Di-RAM Directed Semantic Demo ===\n");

    /* Top-down: compress carbon */
    DGT_IN_CALL(compress, world,
                "compression step failed – not enough carbon");

    /* Bottom-up: release oxygen */
    DGT_OUT_CALL(oxygen, world,
                 "oxygen step failed – cycle broken");

    printf("Final state: %s | C:%d O:%d\n",
           e->name, e->carbon, e->oxygen);

    free(world);
    return 0;
}
