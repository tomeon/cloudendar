/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_SET_H_JORE_110217
#define PYICL_INTERVAL_SET_H_JORE_110217

#include <pyicl/base.h>
#include <pyicl/type_name.h>
#include <pyicl/combining_style.h>
#include <pyicl/interval_bounds.h>
#include <pyicl/interval_container_base.h>
#include <boost/icl/interval_set.hpp>
#include <boost/icl/split_interval_set.hpp>
#include <boost/icl/separate_interval_set.hpp>
#include <boost/foreach.hpp>

namespace boost {
namespace icl {

//
// Make interval sets hashable.
//
template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
std::size_t
hash_value(
    interval_set< DomainT, Compare, Interval, Alloc > const & x
) {
    std::size_t seed = 0;
    BOOST_FOREACH( Interval const & i, x ) {
        hash_combine( seed, i );
    }
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
std::size_t
hash_value(
    split_interval_set< DomainT, Compare, Interval, Alloc > const & x
) {
    std::size_t seed = 0;
    BOOST_FOREACH( Interval const & i, x ) {
        hash_combine( seed, i );
    }
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
std::size_t
hash_value(
    separate_interval_set< DomainT, Compare, Interval, Alloc > const & x
) {
    std::size_t seed = 0;
    BOOST_FOREACH( Interval const & i, x ) {
        hash_combine( seed, i );
    }
    return seed;
}


} // namespace icl
} // namespace boost



namespace pyicl {


/// Specialisation
template<>
template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
struct combining_style_selector< boost::icl::interval_set< DomainT, Compare, Interval, Alloc > > {
    static const char * tag() { return ""; }
    static const char * description() { return "joining"; }
};


/// Specialisation
template<>
template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
struct combining_style_selector< boost::icl::split_interval_set< DomainT, Compare, Interval, Alloc > > {
    static const char * tag() { return "Split"; }
    static const char * description() { return "splitting"; }
};


/// Specialisation
template<>
template<
    typename DomainT,
    ICL_COMPARE Compare,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
struct combining_style_selector< boost::icl::separate_interval_set< DomainT, Compare, Interval, Alloc > > {
    static const char * tag() { return "Separate"; }
    static const char * description() { return "separating"; }
};



/**
 * Expose a interval set.
 */
template< typename IntervalSet >
struct interval_set_exposer
: interval_container_base< interval_set_exposer< IntervalSet >, IntervalSet >
{

    typedef interval_set_exposer< IntervalSet >              this_t;       ///< This type.
    typedef interval_container_base< this_t, IntervalSet >   base_t;       ///< Base type.
	typedef IntervalSet                                      exposed_t; ///< The type to be exposed.
	typedef typename exposed_t::domain_type                  domain_t; ///< The domain of the set.
	typedef typename exposed_t::interval_type                interval_t; ///< The interval type of the set.
	typedef boost::shared_ptr< exposed_t >                    exposed_ptr; ///< Pointer to exposed type.
	typedef boost::python::class_< exposed_t, exposed_ptr >   bp_class_t; ///< Boost.python class type.
	typedef domain_t ( * domain_1_fn )( const exposed_t & ); ///< Function taking exposed type, returning domain type.


	/// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple();
        }

        static
        boost::python::tuple
        getstate( const exposed_t & x )
        {
            boost::python::list l;
            for( typename exposed_t::iterator it = x.begin(); it != x.end(); ++it ) {
                //...so this iterates over intervals
                l.append( *it );
            }
            return boost::python::tuple( l );
        }

        static
        void
        setstate( exposed_t & x, boost::python::tuple state )
        {
            for( unsigned i = 0; boost::python::len( state ) != i; ++i ) {
                x.add( boost::python::extract< const interval_t & >( state[ i ] ) );
            }
        }
    };


    /// Expose the exposed_t using boost.python.
	static
	void
	expose() {
		namespace bp = boost::python;
		namespace icl = boost::icl;

		// Class and construct.
        const std::string class_name = PYICL_MAKE_STRING(
            type_name_selector< domain_t >::tag()
                << combining_style_selector< exposed_t >::tag()
                << "IntervalSet"
        );
        const std::string doc = PYICL_MAKE_STRING(
            "A " << combining_style_selector< exposed_t >::description()
                << " interval set of "
                << type_name_selector< domain_t >::name() << " intervals."
        );
		bp_class_t bp_class(
		    class_name.c_str(),
			doc.c_str(),
			bp::init<>( "Contructs an empty interval set." )
		);
	    bp_class.def( bp::init< domain_t >( "Constructor for a interval set with the given element." ) );
	    bp_class.def( bp::init< interval_t >( "Constructor for a interval set with the given interval." ) );
	    bp_class.def( bp::init< exposed_t >( "Copy constructor." ) );

	    // expose all methods that are can be exposed in base class
        base_t::expose( bp_class );

        // make hashable
        bp_class.def( "__hash__",                 &my_hash< exposed_t >, "Hash value." );

        // Subtraction
        bp_class.def( "subtract",                 minus_equals, "Remove from this container.", bp::return_self<>() );
        bp_class.def( "__isub__",                 minus_equals, "Remove from this container.", bp::return_self<>() );
        bp_class.def( "__sub__",                  minus, "Create a new container by removing from this container." );
	}

    typedef domain_t _e;
    typedef interval_t _i;
    typedef exposed_t _S;

    // Containedness
    PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));

    // Equivalences and ordering - not quite sure what these do yet so don't expose them.
//    PYICL_DECLARE_FN_1(bool, is_element_equal, ::boost::icl::is_element_equal, const exposed_t, (exposed_t, BOOST_PP_NIL));
//    PYICL_DECLARE_FN_1(bool, is_element_less, ::boost::icl::is_element_less, const exposed_t, (exposed_t, BOOST_PP_NIL));
//    PYICL_DECLARE_FN_1(bool, is_element_greater, ::boost::icl::is_element_greater, const exposed_t, (exposed_t, BOOST_PP_NIL));

	// Addition
	PYICL_DECLARE_FN_1(exposed_t &, plus_equals, ::boost::icl::operator+=, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(exposed_t, plus, ::boost::icl::operator+, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));

	// Subtraction
	PYICL_DECLARE_FN_1(exposed_t &, minus_equals, ::boost::icl::operator-=, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(exposed_t, minus, ::boost::icl::operator-, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));

    // Erasure
    PYICL_DECLARE_FN_1(exposed_t &, erase, ::boost::icl::erase, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));

    // Intersection
    PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
    PYICL_DECLARE_FN_1(exposed_t, and_equals, ::boost::icl::operator&=, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(bool, disjoint, ::boost::icl::disjoint, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(bool, intersects, ::boost::icl::intersects, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));

	// Symmetric difference
	PYICL_DECLARE_FN_1(exposed_t &, xor_equals, ::boost::icl::operator^=, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(exposed_t, xor_, ::boost::icl::operator^, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
};







} // namespace pyicl

#endif //PYICL_INTERVAL_SET_H_JORE_110217


