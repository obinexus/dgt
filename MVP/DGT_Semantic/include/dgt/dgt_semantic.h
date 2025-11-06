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
 *  Convenience: allocate a fresh state block
 *--------------------------------------------------------------------*/
#define DGT_STATE_NEW(type)  ((void*)malloc(sizeof(type)))

#endif /* DGT_SEMANTIC_H */
