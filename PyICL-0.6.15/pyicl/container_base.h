/** Copyright John Reid 2011, 2012, 2013
*/

/**
 * \file Code to expose members of intervals, interval sets and interval maps
 */



#ifndef PYICL_CONTAINER_BASE_H_JORE_120519
#define PYICL_CONTAINER_BASE_H_JORE_120519

#include <pyicl/base.h>

namespace pyicl {

template< typename Exposer >
typename ::boost::enable_if< ::boost::icl::is_continuous< typename Exposer::domain_t >, void >::type
expose_discrete_continuous_methods( typename Exposer::bp_class_t & bp_class )
{
}

template< typename Exposer >
typename ::boost::disable_if< ::boost::icl::is_continuous< typename Exposer::domain_t >, void >::type
expose_discrete_continuous_methods( typename Exposer::bp_class_t & bp_class )
{
    namespace icl = ::boost::icl;
    typedef typename Exposer::exposed_t exposed_t;

    bp_class.add_property( "cardinality",     &icl::cardinality< exposed_t >, "The number of elements (equivalent to size)." );
    bp_class.add_property( "size",            &icl::size< exposed_t >, "The number of elements (equivalent to cardinality)." );

    bp_class.add_property( "first",           &icl::first< exposed_t >, "First element." );
    bp_class.add_property( "last",            &icl::last< exposed_t >, "Last element." );
}


/** Wrapper hash function to make sure boost.python can pick the right one. */
template< typename T >
std::size_t
my_hash( const T & x ) {
    return boost::hash< T >()( x );
}


/**
 * Base class for exposers of container classes: interval, interval_set and interval_map.
 *
 * Uses CRTP idiom.
 */
template< typename Derived, typename Exposed >
struct container_base {

    typedef Exposed exposed_t;
    typedef typename exposed_t::domain_type domain_t;
    typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.

    /// Expose/register the container.
    template< typename BPClass >
    static
    void
    expose( BPClass & bp_class ) {

        namespace bp = boost::python;
        namespace icl = boost::icl;

        // Python methods
        bp_class.def_pickle(                      typename Derived::_pickle_suite() );
        bp_class.def( "__str__",                  &convert_to_str< exposed_t >, "String representation." );

        // expose those things that are dependent on whether the domain is continuous or not
        expose_discrete_continuous_methods< Derived >( bp_class );

        // Containedness
        bp_class.add_property( "empty",           &icl::is_empty< exposed_t >, "Is the interval empty?" );
        bp_class.def( "__nonzero__",              &__nonzero__, "Does the interval contain anything?" );
        bp_class.def( "__contains__",             &Derived::contains, "Does the interval contain the argument?" );

        // Equivalences and Orderings
        bp_class.def( "__eq__",                   bool_2_fn( icl::operator== ), "Equality." );
        bp_class.def( "__ne__",                   bool_2_fn( icl::operator!= ), "Inequality." );
        bp_class.def( "__lt__",                   __lt__, "Self begins before other or for equal beginnings self ends before other." );
        bp_class.def( "__le__",                   __le__, "! ( other < self )" );
        bp_class.def( "__gt__",                   __gt__, "other < self." );
        bp_class.def( "__ge__",                   __ge__, "! ( self < other )." );

        // Size
        bp_class.def( "__len__",                  &icl::length< exposed_t >, "The length." );

        // Range
        bp_class.add_property( "lower",           &icl::lower< exposed_t >, "Lower bound." );
        bp_class.add_property( "upper",           &icl::upper< exposed_t >, "Upper bound." );

        // Intersection
        bp_class.def( "intersection",             Derived::and_, "The intersection of this container with the argument." );
        bp_class.def( "__and__",                  Derived::and_, "The intersection of this container with the argument." );
        bp_class.def( "disjoint",                 Derived::disjoint, "Is this set disjoint with the given element, interval or set?" );
        bp_class.def( "intersects",               Derived::intersects, "Does this set intersect the given element, interval or set?" );
    }

protected:
    static bool __lt__( const exposed_t & left, const exposed_t & right ) { return left < right; }
    static bool __le__( const exposed_t & left, const exposed_t & right ) { return ! ( right < left ); }
    static bool __gt__( const exposed_t & left, const exposed_t & right ) { return right < left; }
    static bool __ge__( const exposed_t & left, const exposed_t & right ) { return ! ( left < right ); }
    static bool __nonzero__( exposed_t const & x ) { return ! boost::icl::is_empty( x ); }


};



} // namespace pyicl

#endif //PYICL_CONTAINER_BASE_H_JORE_120519
