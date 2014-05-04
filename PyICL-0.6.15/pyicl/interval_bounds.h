/** Copyright John Reid 2011, 2012, 2013
*/

/**
 * \file Code to expose the boost interval container library to python.
 */



#ifndef PYICL_INTERVAL_BOUNDS_H_JORE_110217
#define PYICL_INTERVAL_BOUNDS_H_JORE_110217

#include <pyicl/base.h>
#include <string>
#include <boost/icl/interval_bounds.hpp>

//
// Make interval boundss hashable.
//
namespace boost {
namespace icl {

inline
std::size_t
hash_value(
    const interval_bounds & x
) {
    return hash< bound_type >()( x.bits() );
}

} // namespace icl
} // namespace boost


namespace pyicl {

struct interval_bounds_exposer {

	/// Expose/register interval bounds.
	static
	void
	expose( char const * name, char const * docstring ) {
		namespace bp = ::boost::python;
		namespace icl = ::boost::icl;

		bp::class_< icl::interval_bounds > _class(
			name,
			docstring,
			bp::no_init
		);
//        _class.add_property( "reverse_left", &icl::interval_bounds::reverse_left, "Bounds that are reversed on the left." );
//        _class.add_property( "reverse_right", &icl::interval_bounds::reverse_right , "Bounds that are reversed on the right."  );
        _class.add_property( "closed_on_right", &closed_on_right, "Is the interval open on the right?" );
        _class.add_property( "closed_on_left" , &closed_on_left , "Is the interval open on the left?"  );
        _class.def( "__str__" , &__str__ , "String representation."  );

		{
            bp::scope _scope( _class );
            bp::scope().attr( "OPEN" ) = icl::interval_bounds::open();
            bp::scope().attr( "CLOSED" ) = icl::interval_bounds::closed();
            bp::scope().attr( "RIGHT_OPEN" ) = icl::interval_bounds::right_open();
            bp::scope().attr( "LEFT_OPEN" ) = icl::interval_bounds::left_open();
		}
	}

    static bool closed_on_right( const ::boost::icl::interval_bounds & bounds ) { return ::boost::icl::interval_bounds::_right & bounds.bits(); }
    static bool closed_on_left ( const ::boost::icl::interval_bounds & bounds ) { return ::boost::icl::interval_bounds::_left  & bounds.bits(); }
    static std::string __str__( const ::boost::icl::interval_bounds & bounds ) {
        if( ::boost::icl::interval_bounds::open().bits() == bounds.bits() ) {
            return "OPEN";
        } else if( ::boost::icl::interval_bounds::right_open().bits() == bounds.bits() ) {
            return "RIGHT_OPEN";
        } else if( ::boost::icl::interval_bounds::left_open().bits() == bounds.bits() ) {
            return "LEFT_OPEN";
        } else if( ::boost::icl::interval_bounds::closed().bits() == bounds.bits() ) {
            return "CLOSED";
        } else {
            throw std::logic_error( "Unknown bounds." );
        }
    }
};

} // namespace pyicl

#endif //PYICL_INTERVAL_BOUNDS_H_JORE_110217


