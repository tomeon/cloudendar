/** Copyright John Reid 2011, 2012
*/

/**
 * \file Code to expose pairs, both icl and standard library pairs.
 */



#ifndef PYICL_PAIR_H_JORE_120520
#define PYICL_PAIR_H_JORE_120520

#include <pyicl/base.h>
#include <pyicl/container_base.h>

namespace pyicl {



/// Exposes pair like objects (std::pair and icl::mapping_pair)
template< typename Pair >
struct pair_exposer {
};



/// Specialisation for mapping_pair
template<>
template< typename DomainT, typename CodomainT >
struct pair_exposer< ::boost::icl::mapping_pair< DomainT, CodomainT > > {
    typedef ::boost::icl::mapping_pair< DomainT, CodomainT > exposed_t; ///< Exposed type.

    /// Already exposed/registered?
    static
    bool
    already_exposed() {
        boost::python::type_info info = boost::python::type_id< exposed_t >();
        const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
        return reg != NULL;
    }


    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.key, x.data );
        }
    };


    static
    void
    expose( const char * name, const char * docstring, const char * key_name = "key", const char * data_name = "data" ) {
        namespace bp = ::boost::python;

        //if( ! already_exposed() ) {
        // expose the segment type inside the class scope
        bp::class_<
            exposed_t
        > bp_class(
            name,
            docstring,
            bp::init< DomainT, CodomainT >( bp::args( "key", "data" ), "Construct a key-data pair." )
        );
        bp_class.def_pickle( _pickle_suite() );
        bp_class.def( "__str__", _convert_to_str, "String representation." );
        bp_class.def_readonly( key_name, &exposed_t::key,  "The key." );
        bp_class.def_readonly( data_name, &exposed_t::data, "The data." );
        //}
    }

    /// String representation
    static
    std::string
    _convert_to_str( exposed_t const & x ) {
        return PYICL_MAKE_STRING(
            extract_str_if_object( x.key )
            << "; "
            << extract_str_if_object( x.data )
        );
    }
};




/// Specialisation for std::pair
template<>
template< typename T1, typename T2 >
struct pair_exposer< ::std::pair< T1, T2 > > {
    typedef ::std::pair< T1, T2 > exposed_t; ///< Exposed type.

    /// Already exposed/registered?
    static
    bool
    already_exposed() {
        boost::python::type_info info = boost::python::type_id< exposed_t >();
        const boost::python::converter::registration * reg = boost::python::converter::registry::query( info );
        return reg != NULL;
    }


    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.first, x.second );
        }
    };


    static
    void
    expose( const char * name, const char * docstring, const char * first_name = "first", const char * second_name = "second" ) {

        //if( ! already_exposed() ) {
        namespace bp = ::boost::python;

        // expose the segment type inside the class scope
        bp::class_<
            exposed_t
        > bp_class(
            name,
            docstring,
            bp::init< T1, T2 >( bp::args( first_name, second_name ), "Construct a pair." )
        );
        bp_class.def_pickle( _pickle_suite() );
        bp_class.def( "__str__", _convert_to_str, "String representation." );
        bp_class.def_readonly( first_name, &exposed_t::first );
        bp_class.def_readonly( second_name, &exposed_t::second );
        //}
    }

    /// String representation
    static
    std::string
    _convert_to_str( exposed_t const & x ) {
        return PYICL_MAKE_STRING(
            extract_str_if_object( x.first )
            << "; "
            << extract_str_if_object( x.second )
        );
    }
};

} // namespace pyicl

#endif //PYICL_PAIR_H_JORE_120520
