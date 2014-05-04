/** Copyright John Reid 2011
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_BASE_H_JORE_110217
#define PYICL_BASE_H_JORE_110217

#include <boost/python.hpp>
#include <boost/functional/hash.hpp>
#include <boost/test/utils/wrap_stringstream.hpp>
#include <boost/preprocessor/list/for_each.hpp>
#include <boost/icl/interval_set.hpp>
#include <boost/icl/interval_map.hpp>
#include <boost/icl/split_interval_set.hpp>
#include <boost/icl/split_interval_map.hpp>
#include <boost/icl/separate_interval_set.hpp>
#include <boost/type_traits/has_minus.hpp>

/// Make a string from the streamed arguments.
#define PYICL_MAKE_STRING( x ) ( boost::wrap_stringstream().ref() << x ).str()

/// Used to define repetitive methods.
#define PYICL_TRY_EXTRACT_AND_APPLY(R, apply, extracted_type) \
	{ \
		boost::python::extract< extracted_type > extractor( o ); \
		if( extractor.check() ) { \
			return apply( s, extractor() ); \
		} \
	} \
	/**/

/// Used to define repetitive methods.
#define PYICL_COULD_NOT_EXTRACT_THROW \
	throw std::invalid_argument( "Type error." ) \
	/**/

/// Used to define repetitive methods.
#define PYICL_DECLARE_FN_1(ret_type, fn_name, apply, subject_type, contained_types) \
	static ret_type fn_name( subject_type & s, boost::python::object o ) { \
		BOOST_PP_LIST_FOR_EACH(PYICL_TRY_EXTRACT_AND_APPLY, apply, contained_types); \
		PYICL_COULD_NOT_EXTRACT_THROW; \
	} \
	/**/




namespace pyicl {



/// If argument is a boost python object, then extract a string from it.
template< typename T >
struct extract_str_if_object_ {
	typedef T return_type;
	T operator()( T t ) { return t; }
};


/// If argument is a boost python object, then extract a string from it. Specialisation for boost::python::object.
template<>
struct extract_str_if_object_< boost::python::object > {
	typedef std::string return_type;
	std::string operator()( boost::python::object t ) {
		namespace bp = boost::python;
		return bp::extract< std::string >( bp::str( t ) )();
	}
};


/// If argument is a boost python object, then extract a string from it, otherwise return the argument unchanged.
template< typename T >
typename extract_str_if_object_< T >::return_type
extract_str_if_object( T t ) {
	return extract_str_if_object_< T >()( t );
}


/// As string
template< typename T >
std::string
convert_to_str( const T & t ) {
    return PYICL_MAKE_STRING( t );
}

/// As string - specialisation
template<>
inline
std::string
convert_to_str( const boost::python::object & t ) {
    return boost::python::extract< std::string >( boost::python::str( t ) );
}


} // namespace pyicl


namespace boost {
namespace python {

inline
std::size_t
hash_value(
    object const & x
) {
    return extract< std::size_t >( x.attr( "__hash__" )() )();
}

} // namespace python
} // namespace boost



#endif //PYICL_BASE_H_JORE_110217


