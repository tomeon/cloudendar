/** Copyright John Reid 2012
*/

#include <boost/python.hpp>

struct Outer1 {};
struct Outer2 {};
struct Inner {};

BOOST_PYTHON_MODULE( _sandbox )
{
    namespace bp = ::boost::python;
    {
        bp::scope scope = bp::class_< Outer1 >( "Outer1" );
        bp::class_< Inner >( "Inner" );
    }

    {
        bp::object class_Outer2 = bp::class_< Outer2 >( "Outer2" );
        bp::type_info info = boost::python::type_id< Inner >();
        const bp::converter::registration * reg = bp::converter::registry::query( info );
        if( NULL == reg ) {
            bp::class_< Inner >( "Inner" );
        } else {
            // Some magic here!
        }
    }
}
