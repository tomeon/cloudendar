/** Copyright John Reid 2011, 2012, 2013
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_MAP_H_JORE_110217
#define PYICL_INTERVAL_MAP_H_JORE_110217

#include <pyicl/base.h>
#include <pyicl/pair.h>
#include <pyicl/object.h>
#include <pyicl/maximiser.h>
#include <pyicl/type_name.h>
#include <pyicl/combining_style.h>
#include <pyicl/interval_container_base.h>
#include <boost/icl/interval_map.hpp>

namespace pyicl {


/// Specialisation
template<>
template<
    typename DomainT,
    typename CodomainT,
    typename Traits,
    ICL_COMPARE Compare,
    ICL_COMBINE Combine,
    ICL_SECTION Section,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
struct combining_style_selector< boost::icl::interval_map< DomainT, CodomainT, Traits, Compare, Combine, Section, Interval, Alloc > > {
    static const char * tag() { return ""; }
    static const char * description() { return "joining"; }
};


/// Specialisation
template<>
template<
    typename DomainT,
    typename CodomainT,
    typename Traits,
    ICL_COMPARE Compare,
    ICL_COMBINE Combine,
    ICL_SECTION Section,
    ICL_INTERVAL(ICL_COMPARE) Interval,
    ICL_ALLOC Alloc
>
struct combining_style_selector< boost::icl::split_interval_map< DomainT, CodomainT, Traits, Compare, Combine, Section, Interval, Alloc > > {
    static const char * tag() { return "Split"; }
    static const char * description() { return "splitting"; }
};


/**
 * Expose an interval map.
 */
template< typename IntervalMap >
struct interval_map_exposer
: interval_container_base< interval_map_exposer< IntervalMap >, IntervalMap >
{

    typedef interval_map_exposer< IntervalMap >             this_t;       ///< This type.
    typedef interval_container_base< this_t, IntervalMap >   base_t;       ///< Base type.
	typedef IntervalMap                                      exposed_t; ///< The container type to be exposed.
	typedef typename exposed_t::domain_type                  domain_t; ///< The domain type.
	typedef typename exposed_t::codomain_type                codomain_t; ///< The codomain type.
	typedef typename exposed_t::traits                       traits_t; ///< The traits type.
	typedef typename exposed_t::interval_type                interval_t; ///< Interval type.
	typedef boost::shared_ptr< exposed_t >                    exposed_ptr; ///< A type for a pointer to the container.
	typedef typename exposed_t::element_type                 element_t; ///< element-value pair.
	typedef typename exposed_t::segment_type                 segment_t; ///< interval-value pair.
	typedef typename ::boost::icl::interval_set< domain_t >  set_t; ///< An equivalent set type.
	typedef boost::python::class_<
		exposed_t,
		exposed_ptr
	>                                                    bp_class_t; ///< Boost.python class type.
	typedef bool ( * bool_2_fn )( const exposed_t &, const exposed_t & ); ///< Function taking 2 exposed types, returning bool.
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
            for( typename exposed_t::const_iterator it = x.begin(); it != x.end(); ++it ) {
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
                typename exposed_t::const_iterator::value_type segment = boost::python::extract< typename exposed_t::const_iterator::value_type >( state[ i ] );
                x.add( segment );
            }
        }
    };


    /// Expose/register the interval container.
	static
	void
	expose() {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;

		bp::scope enclosing_scope; // overall scope

		// define the segment type if needed
        const std::string segment_class_name = PYICL_MAKE_STRING(
            "_Segment"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), segment_class_name.c_str() ) ) {
            pair_exposer< segment_t >::expose(
                segment_class_name.c_str(),
                "A segment in an interval map, that is an interval and an associated value.",
                "interval",
                "value"
            );
        }

        // define the const segment type if needed
        const std::string const_segment_class_name = PYICL_MAKE_STRING(
            "_ConstSegment"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), const_segment_class_name.c_str() ) ) {
            pair_exposer< typename exposed_t::iterator::value_type >::expose(
                const_segment_class_name.c_str(),
                "A const segment in an interval map, that is an interval and an associated value.",
                "interval",
                "value"
            );
        }

        // define the element type if needed
		const std::string element_class_name = PYICL_MAKE_STRING(
            "_Pair"
                << type_name_selector< domain_t >::name()
                << type_name_selector< codomain_t >::name()
        );
        if( ! PyObject_HasAttrString( enclosing_scope.ptr(), element_class_name.c_str() ) ) {
            pair_exposer< element_t >::expose(
                element_class_name.c_str(),
                PYICL_MAKE_STRING(
                    "A pair of a "
                        << type_name_selector< domain_t >::lower()
                        << " and a "
                        << type_name_selector< codomain_t >::lower() << "."
                ).c_str(),
                "key",
                "value"
            );
        }

		// Class and construct.
		bp_class_t bp_class(

		    // the class name
            PYICL_MAKE_STRING(
                type_name_selector< domain_t >::tag()
                    << combining_style_selector< exposed_t >::tag()
                    << "Interval"
                    << type_name_selector< codomain_t >::tag()
                    << "Map"
            ).c_str(),

            // the docstring
			PYICL_MAKE_STRING(
			    "A " << combining_style_selector< exposed_t >::description() << " map from "
			        << type_name_selector< domain_t >::lower()
			        << " intervals to "
			        << type_name_selector< codomain_t >::lower() << "s."
			).c_str(),

			// the constructor
			bp::init<>( "Contructs an empty interval map." )
		);
	    bp_class.def( bp::init< segment_t >( "Constructor for a interval set with the given segment." ) );
	    bp_class.def( bp::init< exposed_t >( "Copy constructor." ) );

        // expose all methods that are can be exposed in base class
        base_t::expose( bp_class );

	    // Expose auxiliary types inside the map class.
		bp::scope _scope( bp_class );
        bp_class.attr( "Segment" ) = enclosing_scope.attr( segment_class_name.c_str() );
        bp_class.attr( "ConstSegment" ) = enclosing_scope.attr( const_segment_class_name.c_str() );
        bp_class.attr( "Element" ) = enclosing_scope.attr( element_class_name.c_str() );

        // Subtraction
        bp_class.def( "subtract",                 operator_minus_selector< codomain_t >::minus_equals, "Remove from this container.", bp::return_self<>() );
        bp_class.def( "__isub__",                 operator_minus_selector< codomain_t >::minus_equals, "Remove from this container.", bp::return_self<>() );
        bp_class.def( "__sub__",                  operator_minus_selector< codomain_t >::minus, "Create a new container by removing from this container." );

        // Insertion
        bp_class.def( "insert",                   &insert, "Insert into the map where there is no collision with existing members of the map.", bp::return_self<>() );
        bp_class.def( "set",                      &set, "Set value(s) in the map.", bp::return_self<>() );
	}

	typedef domain_t _e;
    typedef interval_t _i;
    typedef typename exposed_t::interval_set_type _S;
    typedef element_t _b;
    typedef segment_t _p;
    typedef exposed_t _M;

    // Containedness
	PYICL_DECLARE_FN_1(bool, contains, ::boost::icl::contains, const exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));

    // Addition
	PYICL_DECLARE_FN_1(exposed_t &, plus_equals, ::boost::icl::operator+=, exposed_t, (_M, (_p, (_b, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(exposed_t, plus, ::boost::icl::operator+, const exposed_t, (_M, (_p, (_b, BOOST_PP_NIL))));

	// Insertion
    PYICL_DECLARE_FN_1(exposed_t &, insert, ::boost::icl::insert, exposed_t, (_M, (_p, (_b, BOOST_PP_NIL))));
    PYICL_DECLARE_FN_1(exposed_t &, set, ::boost::icl::set_at, exposed_t, (_p, (_b, BOOST_PP_NIL)));

    // Erasure
    PYICL_DECLARE_FN_1(exposed_t &, erase, ::boost::icl::erase, exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));

    // Intersection
    PYICL_DECLARE_FN_1(exposed_t, and_, ::boost::icl::operator&, const exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));
    PYICL_DECLARE_FN_1(exposed_t, and_equals, ::boost::icl::operator&=, exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));
	PYICL_DECLARE_FN_1(bool, disjoint, ::boost::icl::disjoint, const exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));
	PYICL_DECLARE_FN_1(bool, intersects, ::boost::icl::intersects, const exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));

    // Symmetric difference
	PYICL_DECLARE_FN_1(exposed_t &, xor_equals, ::boost::icl::operator^=, exposed_t, (_M, (_p, (_b, BOOST_PP_NIL))));
	PYICL_DECLARE_FN_1(exposed_t, xor_, ::boost::icl::operator^, exposed_t, (_M, (_p, (_b, BOOST_PP_NIL))));

    template< typename Codomain, typename Enable = void >
    struct operator_minus_selector {
        // codomain has no operator- so *cannot* subtract values from values
        PYICL_DECLARE_FN_1(exposed_t &, minus_equals, ::boost::icl::operator-=, exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
        PYICL_DECLARE_FN_1(exposed_t, minus, ::boost::icl::operator-, const exposed_t, (_S, (_i, (_e, BOOST_PP_NIL))));
    };

    // specialisation when we have operator-
    template< typename Codomain >
    struct
    operator_minus_selector<
        Codomain,
        typename boost::enable_if_c< boost::has_minus< Codomain, Codomain, Codomain >::value >::type
    > {
        // codomain has no operator- so *can* subtract values from values
        PYICL_DECLARE_FN_1(exposed_t &, minus_equals, ::boost::icl::operator-=, exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));
        PYICL_DECLARE_FN_1(exposed_t, minus, ::boost::icl::operator-, const exposed_t, (_M, (_p, (_b, (_S, (_i, (_e, BOOST_PP_NIL)))))));
    };

};




} // namespace pyicl


#endif //PYICL_INTERVAL_MAP_H_JORE_110217


