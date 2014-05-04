/** Copyright John Reid 2011, 2012, 2013
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_H_JORE_110217
#define PYICL_INTERVAL_H_JORE_110217

#include <pyicl/base.h>
#include <pyicl/type_name.h>
#include <pyicl/container_base.h>
#include <pyicl/interval_bounds.h>
#include <boost/icl/interval.hpp>

namespace boost {
namespace icl {

//
// Make intervals hashable.
//
template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    right_open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    left_open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    closed_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    discrete_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    hash_combine( seed, x.bounds() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    continuous_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    hash_combine( seed, x.bounds() );
    return seed;
}

} // namespace icl
} // namespace boost



namespace pyicl {
namespace { //anonymous

/**
 * Exposes functionality depending on whether the interval is symmetric.
 */
template < bool IsAsymmetric >
struct symmetry_exposer
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;
		typedef typename Exposer::exposed_t exposed_t;
		typedef typename Exposer::bool_2_fn bool_2_fn;

	}
};

/// Enabled only if symmetric
template <>
struct symmetry_exposer< false >
{
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
	}
};




/**
 * Exposer different things depending on whether is dynamic or static.
 */
template< bool IsDynamic >
struct dynamic_static_exposer {
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		typedef typename Exposer::domain_t domain_t;
	    bp_class.def( bp::init< domain_t, domain_t >( "Constructor for an interval with default bounds." ) );
	}
};

// specialization
template<>
struct dynamic_static_exposer< true > {
	template< typename Exposer >
	static void expose( typename Exposer::bp_class_t & bp_class ) {
		namespace bp = ::boost::python;
		typedef typename Exposer::domain_t domain_t;
		bp_class.def( bp::init<>( "Contructs an empty interval." ) );
	    bp_class.def( bp::init< domain_t >( "Constructor for a closed singleton interval [val,val]." ) );
	    bp_class.def( bp::init< domain_t, domain_t >( "Constructor for an interval with default bounds." ) );
	    bp_class.def( bp::init< domain_t, domain_t, ::boost::icl::interval_bounds >( "Interval from lower to upper with given bounds." ) );
	    bp_class.add_property( "bounds", &Exposer::exposed_t::bounds, "The bounds." );
	}
};




/// Specialised for interval names.
template< typename Interval >
struct interval_strings {
};

/// Specialisation.
template<>
template< typename DomainT, ICL_COMPARE Compare >
struct interval_strings< ::boost::icl::right_open_interval< DomainT, Compare > > {
    static std::string name() { return PYICL_MAKE_STRING( type_name_selector< DomainT >::tag() << "IntervalRightOpen" ); }
    static std::string docstring() { return PYICL_MAKE_STRING( "A right-open interval of " << type_name_selector< DomainT >::lower() << "s." ); }
};

/// Specialisation.
template<>
template< typename DomainT, ICL_COMPARE Compare >
struct interval_strings< ::boost::icl::left_open_interval< DomainT, Compare > > {
    static std::string name() { return PYICL_MAKE_STRING( type_name_selector< DomainT >::tag() << "IntervalLeftOpen" ); }
    static std::string docstring() { return PYICL_MAKE_STRING( "A left-open interval of " << type_name_selector< DomainT >::lower() << "s." ); }
};

/// Specialisation.
template<>
template< typename DomainT, ICL_COMPARE Compare >
struct interval_strings< ::boost::icl::continuous_interval< DomainT, Compare > > {
    static std::string name() { return PYICL_MAKE_STRING( type_name_selector< DomainT >::tag() << "Interval" ); }
    static std::string docstring() { return PYICL_MAKE_STRING( "A dynamically bounded continuous interval of " << type_name_selector< DomainT >::lower() << "s." ); }
};

/// Specialisation.
template<>
template< typename DomainT, ICL_COMPARE Compare >
struct interval_strings< ::boost::icl::discrete_interval< DomainT, Compare > > {
    static std::string name() { return PYICL_MAKE_STRING( type_name_selector< DomainT >::tag() << "Interval" ); }
    static std::string docstring() { return PYICL_MAKE_STRING( "A dynamically bounded discrete interval of " << type_name_selector< DomainT >::lower() << "s." ); }
};

} //anonymous



/**
 * Expose an interval.
 */
template< typename IntervalT >
struct interval_exposer
: container_base< interval_exposer< IntervalT >, IntervalT >
{

    typedef container_base< interval_exposer< IntervalT >, IntervalT >  base_t;       ///< Base type.
	typedef interval_exposer< IntervalT >                                this_t;       ///< This type.
	typedef IntervalT                                                    exposed_t;    ///< Interval type to be exposed.
	typedef ::boost::icl::interval_traits< exposed_t >                    traits_t;     ///< Interval traits.
    typedef typename ::boost::icl::difference_type_of< traits_t >::type  difference_t; ///< Difference type.
    typedef typename ::boost::icl::domain_type_of< traits_t >::type      domain_t;     ///< Domain type.
    typedef typename ::boost::icl::size_type_of< traits_t >::type        size_t;       ///< Size type.
	typedef ::boost::python::class_< exposed_t >                          bp_class_t;   ///< Boost.python class type.
	typedef interval_strings< exposed_t >                                 strings_t;    ///< Type used for name and docstring.

	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.

	static std::string name() { return strings_t::name(); }

	/// To pickle intervals
	struct _pickle_suite : boost::python::pickle_suite
    {
	    static
	    boost::python::tuple
	    getinitargs( const exposed_t & x )
	    {
	        return boost::python::make_tuple( x.lower(), x.upper() );
	    }
    };

	/// Already exposed/registered?
	static
	bool
	already_exposed() {
	    boost::python::type_info info = boost::python::type_id< exposed_t >();
	    const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
	    return reg != NULL;
	}


	/// Expose/register the interval.
	static
	void
	expose() {

        namespace bp = ::boost::python;
        namespace icl = ::boost::icl;

        // Class and constructors.
        bp_class_t bp_class(
            strings_t::name().c_str(),
            strings_t::docstring().c_str(),
            bp::no_init
        );

        base_t::expose( bp_class );

        // make hashable
        bp_class.def( "__hash__",                 &my_hash< exposed_t >, "Hash value." );

        // set attributes for the traits of the class
//		bp::scope( bp_class ).attr( "__dynamic_bounds__" ) = icl::has_dynamic_bounds< exposed_t >::value;
//		bp::scope( bp_class ).attr( "__continuous__" ) = icl::is_continuous< domain_t >::value;
//		bp::scope( bp_class ).attr( "__asymmetric__" ) = icl::is_asymmetric_interval< domain_t >::value;

        // Expose those methods that are dependent on traits.
        symmetry_exposer< icl::is_asymmetric_interval< exposed_t >::value >::template expose< this_t >( bp_class );
        dynamic_static_exposer< icl::has_dynamic_bounds< exposed_t >::value >::template expose< this_t >( bp_class );

        // Miscellaneous
        bp_class.def( "hull",                     &hull, "The smallest interval that contains intervals this interval and the argument." );
        bp_class.def( "distance",                 &distance, "The distance between two intervals." );
        bp_class.def( "touches",                  bool_2_fn( icl::touches< exposed_t > ), "There is no gap between the 2 intervals and they have no element in common." );
        bp_class.def( "inner_complement",         inner_complement );

        // Subtraction
        bp_class.def( "left_subtract",            &icl::left_subtract< exposed_t >, "Left subtract." );
        bp_class.def( "right_subtract",           &icl::right_subtract< exposed_t >, "Right subtract." );

        // Additional interval orderings
        bp_class.def( "exclusive_less",           bool_2_fn( icl::exclusive_less< exposed_t > ), "Maximal element of self is less than the minimal element of argument." );
        bp_class.def( "lower_less",               bool_2_fn( boost::icl::lower_less< exposed_t > ), "Compares the beginning of self and argument." );
        bp_class.def( "lower_equal",              bool_2_fn( boost::icl::lower_equal< exposed_t > ), "Compares the beginning of self and argument." );
        bp_class.def( "lower_less_equal",         bool_2_fn( boost::icl::lower_less_equal< exposed_t > ), "Compares the beginning of self and argument." );
        bp_class.def( "upper_less",               bool_2_fn( boost::icl::upper_less< exposed_t > ), "Compares the end of self and argument." );
        bp_class.def( "upper_equal",              bool_2_fn( boost::icl::upper_equal< exposed_t > ), "Compares the end of self and argument." );
        bp_class.def( "upper_less_equal",         bool_2_fn( boost::icl::upper_less_equal< exposed_t > ), "Compares the end of self and argument." );
	}

    PYICL_DECLARE_FN_1(exposed_t, hull, ::boost::icl::hull, const exposed_t, (const exposed_t, BOOST_PP_NIL));
    PYICL_DECLARE_FN_1(difference_t, distance, ::boost::icl::distance, const exposed_t, (const exposed_t, BOOST_PP_NIL));
    PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (exposed_t, (domain_t, BOOST_PP_NIL)));
	PYICL_DECLARE_FN_1(exposed_t, inner_complement, ::boost::icl::inner_complement, const exposed_t, (const exposed_t &, BOOST_PP_NIL));

	// Intersection
    PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (const exposed_t, BOOST_PP_NIL));
    PYICL_DECLARE_FN_1(bool, disjoint, ::boost::icl::disjoint, const exposed_t, (const exposed_t, BOOST_PP_NIL));
    PYICL_DECLARE_FN_1(bool, intersects, ::boost::icl::intersects, const exposed_t, (const exposed_t, BOOST_PP_NIL));

};







/**
 * Expose static interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_static_interval_types() {
	namespace icl = ::boost::icl;
	interval_exposer< icl::right_open_interval< DomainT, Compare > >::expose();
    interval_exposer< icl::left_open_interval< DomainT, Compare > >::expose();
//    interval_exposer< icl::closed_interval< DomainT, Compare > >::expose();
//    interval_exposer< icl::open_interval< DomainT, Compare > >::expose();
}


/**
 * Expose dynamic interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_dynamic_interval_type() {
	interval_exposer< typename ::boost::icl::interval< DomainT, Compare >::type >::expose();
}

/**
 * Expose all interval types.
 */
template< typename DomainT, ICL_COMPARE Compare >
void
expose_interval_types() {
	expose_static_interval_types< DomainT, Compare >();
	expose_dynamic_interval_type< DomainT, Compare >();
}



} // namespace pyicl

#endif //PYICL_INTERVAL_H_JORE_110217


