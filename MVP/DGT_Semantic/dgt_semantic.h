/*=====================================================================
 *  dgt_semantic.h  –  Directed Semantic Macro System
 *  ------------------------------------------------
 *  • Dual-model (interior / exterior) macro bindings
 *  • Functor-based, O(1) dispatch
 *  • Built-in “fail-safe, not silent” error reporting
 *  • Works with any C99 compiler
 *====================================================================*/

#ifndef DGT_SEMANTIC_H
#define DGT_SEMANTIC_H

#include <stdio.h>
#include <stdlib.h>

/*--------------------------------------------------------------------
 *  Compile-time direction tags
 *--------------------------------------------------------------------*/
#define __DGT_IN__   0x01   /* interior → exterior  (top-down)   */
#define __DGT_OUT__  0x02   /* exterior → interior (bottom-up) */

/*--------------------------------------------------------------------
 *  Core functor type – a pure transformation of a void* state
 *--------------------------------------------------------------------*/
typedef void* (*dgt_functor_t)(void* state);

/*--------------------------------------------------------------------
 *  Helper: safe invocation with explicit error path
 *--------------------------------------------------------------------*/
#define DGT_INVOKE(dir, fn, state, on_err)          \
    do {                                            \
        void* __res = (fn)(state);                  \
        if (!__res && (on_err)) {                   \
            fprintf(stderr,                         \
                    "[DGT %s] %s failed → %s\n",    \
                    (dir)==__DGT_IN__ ? "IN" : "OUT", \
                    #fn, (char*)(on_err));          \
            exit(EXIT_FAILURE);                     \
        }                                           \
        state = __res;                              \
    } while (0)

/*====================================================================
 *  USER-FACING MACROS
 *====================================================================*/

/*--------------------------------------------------------------------
 *  DGT_IN_…   –  top-down, informative, full-form
 *--------------------------------------------------------------------*/
#define DGT_IN_BIND(name, functor) \
    static inline void* name##_in(void* __s) { return (functor)(__s); }

#define DGT_IN_CALL(name, state, on_err) \
    DGT_INVOKE(__DGT_IN__, name##_in, state, on_err)

/*--------------------------------------------------------------------
 *  DGT_OUT_…  –  bottom-up, phenomenological, insight-to-act
 *--------------------------------------------------------------------*/
#define DGT_OUT_BIND(name, functor) \
    static inline void* name##_out(void* __s) { return (functor)(__s); }

#define DGT_OUT_CALL(name, state, on_err) \
    DGT_INVOKE(__DGT_OUT__, name##_out, state, on_err)

/*--------------------------------------------------------------------
 *  Convenience: allocate a fresh state block (size must be known)
 *--------------------------------------------------------------------*/
#define DGT_STATE_NEW(type)  ((void*)malloc(sizeof(type)))

/*--------------------------------------------------------------------
 *  Example functors (you will replace these with your real logic)
 *--------------------------------------------------------------------*/
static void* example_fossil_fold(void* s) {
    /* fossil-fold → compression → oxygen for new ecosystem */
    printf("[IN] fossil_fold → compressing...\n");
    return s;               /* identity for demo */
}

static void* example_microbractio(void* s) {
    /* micro-bractio → palan-carbon → dioxide → oxygen */
    printf("[OUT] microbractio → oxygen release...\n");
    return s;
}

/*====================================================================
 *  QUICK-START DEMO (compile with: gcc -std=c99 demo.c -o demo)
 *====================================================================*/
#if defined(DGT_DEMO)

int main(void) {
    void* ecosystem = DGT_STATE_NEW(char[64]);

    /* Bind the directed semantics */
    DGT_IN_BIND (fossil,   example_fossil_fold);
    DGT_OUT_BIND(micro,    example_microbractio);

    /* Top-down interior → exterior */
    DGT_IN_CALL (fossil, ecosystem,
                 "fossil_fold failed – ecosystem cannot compress");

    /* Bottom-up exterior → interior */
    DGT_OUT_CALL(micro, ecosystem,
                 "microbractio failed – oxygen cycle broken");

    free(ecosystem);
    return 0;
}
#endif /* DGT_DEMO */

#endif /* DGT_SEMANTIC_H */
