#include "dgt/dgt_semantic.h"

/* Your real functors */
void* compress_ecosystem(void* s) { … }
void* release_oxygen(void* s)      { … }

DGT_IN_BIND (compress, compress_ecosystem);
DGT_OUT_BIND(oxygen,  release_oxygen);
