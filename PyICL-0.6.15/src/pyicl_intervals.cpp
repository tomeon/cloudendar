/** Copyright John Reid 2010, 2011, 2012, 2013
*/


#include <pyicl/interval_bounds.h>
#include <pyicl/interval.h>
#include <pyicl/object.h>


/**
 * Expose interval bounds and intervals.
 */
void
expose_intervals()
{
	using namespace ::pyicl;
	namespace bp = ::boost::python;
	namespace icl = ::boost::icl;

    interval_bounds_exposer::expose( "IntervalBounds", "Types of bounds on intervals." );

    expose_interval_types< bp::object, ICL_COMPARE_INSTANCE( std::less, bp::object ) >();
    expose_interval_types< float     , ICL_COMPARE_INSTANCE( std::less, float ) >();
	expose_interval_types< int       , ICL_COMPARE_INSTANCE( std::less, int   ) >();
}
