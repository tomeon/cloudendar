/** Copyright John Reid 2012
*/

/**
 * \file Code to select combining styles.
 */



#ifndef PYICL_COMBINING_STYLE_H_JORE_120518
#define PYICL_COMBINING_STYLE_H_JORE_120518

#include <pyicl/base.h>

namespace pyicl {


/**
 * Struct we specialise to decide type of combining style.
 */
template< typename T >
struct combining_style_selector {
    static const char * tag() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct combining_style_selector must be specialised for this type." );
        return 0;
    }
    static const char * description() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct combining_style_selector must be specialised for this type." );
        return 0;
    }
};


} // namespace pyicl

#endif //PYICL_COMBINING_STYLE_H_JORE_120518
