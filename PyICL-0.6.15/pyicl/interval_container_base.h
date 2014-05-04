/** Copyright John Reid 2011, 2012
*/

/**
 * \file Code to expose members of intervals, interval sets and interval maps
 */



#ifndef PYICL_INTERVAL_CONTAINER_BASE_H_JORE_120519
#define PYICL_INTERVAL_CONTAINER_BASE_H_JORE_120519

#include <pyicl/base.h>
#include <pyicl/container_base.h>
#include <pyicl/interval.h>

namespace pyicl {



/**
 * Base class for exposers of containers of interval classes: interval_set and interval_map.
 *
 * Uses CRTP idiom.
 */
template< typename Derived, typename Exposed >
struct interval_container_base
: container_base< Derived, Exposed >
{
    typedef container_base< Derived, Exposed > base_t;
    typedef Exposed exposed_t;
    typedef typename exposed_t::domain_type domain_t;
    typedef typename exposed_t::interval_type interval_t;
    typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.

    /// Expose/register the container.
    template< typename BPClass >
    static
    void
    expose( BPClass & bp_class ) {

        namespace bp = boost::python;
        namespace icl = boost::icl;

        bp::scope enclosing_scope; // overall scope

        // define the interval type if needed
        const std::string interval_class_name = interval_exposer< interval_t >::name();
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), interval_class_name.c_str() ) ) {
            interval_exposer< interval_t >::expose();
        }

        base_t::expose( bp_class );


        // miscellaneous
        bp_class.attr( "Interval" )               = enclosing_scope.attr( interval_class_name.c_str() );
        bp_class.add_property( "hull",            &icl::hull< exposed_t >, "The smallest interval that spans this interval container." );

        // Equivalences and ordering
//        bp_class.def( "is_element_equal",         &Derived::is_element_equal, "Find the interval for the given element." );
//        bp_class.def( "is_element_less",          &Derived::is_element_less, "Find the interval for the given element." );
//        bp_class.def( "is_element_greater",       &Derived::is_element_greater, "Find the interval for the given element." );

        // Selection/iterator stuff
        bp_class.def( "__iter__",                 bp::iterator< exposed_t >(), "Iterate (by-interval) over the container." );
        bp_class.def( "find",                     &find_wrapper, "Find the interval for the given element." );

        // Iterative size
        bp_class.add_property( "iterative_size",  &icl::iterative_size< exposed_t >, "The number of intervals in this container that can be iterated over." );
        bp_class.add_property( "interval_count",  &icl::interval_count< exposed_t >, "The number of intervals in this interval container." );

        // Addition
        bp_class.def( "add",                      Derived::plus_equals, "Add to this container.", bp::return_self<>() );
        bp_class.def( "__iadd__",                 Derived::plus_equals, "Add to this container.", bp::return_self<>() );
        bp_class.def( "__ior__",                  Derived::plus_equals, "Add to this container.", bp::return_self<>() );
        bp_class.def( "__add__",                  Derived::plus, "Create a new container by adding to this one." );
        bp_class.def( "__or__",                   Derived::plus, "Create a new container by adding to this one." );

        // Erasure
        bp_class.def( "erase",                    Derived::erase, "Erase elements from this container.", bp::return_self<>() );

        // Intersection
        bp_class.def( "__iand__",                 Derived::and_equals, "Update this container to be the intersection of itself with the argument." );

        // Symmetric difference
        bp_class.def( "flip",                     Derived::xor_equals, "Update this container to be the symmetric difference of itself with the other.", bp::return_self<>() );
        bp_class.def( "__ixor__",                 Derived::xor_equals, "Update this container to be the symmetric difference of itself with the other.", bp::return_self<>() );
        bp_class.def( "__xor__",                  Derived::xor_, "The symmetric difference of this container with the other." );

        bp_class.def( "clear",                    &exposed_t::clear, "Clear this container." );

    }

    /// Wrapper for find.
    static ::boost::python::object
    find_wrapper( const exposed_t & exposed, domain_t key ) {
        namespace bp = ::boost::python;
        namespace icl = ::boost::icl;

        typename exposed_t::const_iterator i = exposed.find( key );
        if( exposed.end() == i ) {
            return bp::object();
        } else {
            return bp::object( *i );
        }
    }


};


} // namespace pyicl

#endif //PYICL_INTERVAL_CONTAINER_BASE_H_JORE_120519
