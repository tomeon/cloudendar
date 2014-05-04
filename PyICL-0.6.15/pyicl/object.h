/** Copyright John Reid 2011
*/


/**
 * \file Code to let boost.icl know how the boost.python object type behaves.
 */


#ifndef PYICL_OBJECT_H_JORE_120517
#define PYICL_OBJECT_H_JORE_120517

#include <boost/python.hpp>
#include <boost/icl/type_traits/identity_element.hpp>
#include <boost/icl/type_traits/is_discrete.hpp>
#include <boost/icl/type_traits/difference_type_of.hpp>
#include <boost/icl/type_traits/size_type_of.hpp>

namespace boost{
namespace python {

inline
std::ostream &
operator<<( std::ostream & os, boost::python::object o ) {
    return os << static_cast< const std::string & >( boost::python::extract< std::string >( boost::python::str( o ) ) );
}

} // namespace icl
} // namespace boost



namespace boost{
namespace icl {

template<>
struct is_discrete< boost::python::object >
{
    typedef is_discrete type;
    BOOST_STATIC_CONSTANT( bool, value = false );
};

template<>
struct identity_element< boost::python::object >
{
    static boost::python::object _value;

    static
    boost::python::object value()
    {
        return _value;
    }
};

template<>
struct has_difference< boost::python::object >
{
    typedef has_difference type;
    BOOST_STATIC_CONSTANT( bool, value = true );
};

template<>
struct difference_type_of< boost::python::object >
{
    typedef boost::python::object type;
};

template<>
struct has_set_semantics< boost::python::object >
{
    typedef has_set_semantics type;
    BOOST_STATIC_CONSTANT( bool, value = true );
};

template<>
struct size_type_of< boost::python::object >
{
    typedef boost::python::object type;
};

inline
boost::python::object
operator++( boost::python::object & x )
{
    return x += boost::python::object( 1 );
}

inline
boost::python::object
operator--( boost::python::object & x )
{
    return x -= boost::python::object( 1 );
}

} // namespace icl
} // namespace boost



#endif //PYICL_OBJECT_H_JORE_120517
