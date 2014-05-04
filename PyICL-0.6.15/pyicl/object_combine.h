/** Copyright John Reid 2012
 *
 * \file Code to combine python objects.
 */

#ifndef PYICL_COMBINE_OBJECT_H_JORE_110217
#define PYICL_COMBINE_OBJECT_H_JORE_110217

#include <boost/icl/functors.hpp>

namespace pyicl {



/**
 * Functor to combine objects.
 *
 * See file:///home/john/Dev/ThirdParty/boost/boost_1_49_0/libs/icl/doc/html/boost/icl/inplace_plus.html
 * for example
 */
template< typename Type >
struct combine_objects
: public ::boost::icl::identity_based_inplace_combine< Type >
{
    // types
    typedef combine_objects< Type > type;

    // public member functions
    void operator()( Type & x, const Type & operand ) const {
        if( x.is_none() ) {
            x = operand;
            return;
        }
        if( operand.is_none() ) {
            return;
        }
        x += operand;
    }

    // public static functions
    static void version( Type & );
};


/**
 * Functor for inverse of object combine.
 *
 * See file:///home/john/Dev/ThirdParty/boost/boost_1_49_0/libs/icl/doc/html/boost/icl/inplace_plus.html
 * for example
 */
template< typename Type >
struct combine_objects_inverse
: public ::boost::icl::identity_based_inplace_combine< Type >
{
    // types
    typedef combine_objects_inverse< Type > type;

    // public member functions
    void operator()( Type & x, const Type & operand ) const {
        if( operand.is_none() ) {
            return;
        }
        x -= operand;
    }

    // public static functions
    static void version( Type & );
};




} // namespace pyicl



// Define the traits that boost.icl needs to use the above functors
namespace boost {
namespace icl {

template< typename Type >
struct inverse< pyicl::combine_objects< Type > >
{
    typedef pyicl::combine_objects_inverse< Type > type;
};


} // namespace icl
} // namespace boost

#endif //PYICL_COMBINE_OBJECT_H_JORE_110217

