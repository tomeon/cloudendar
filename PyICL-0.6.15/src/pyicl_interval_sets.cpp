/** Copyright John Reid 2010, 2011
*/


#include <pyicl/interval_set.h>
#include <pyicl/object.h>


/**
 * Expose interval sets.
 */
void
expose_interval_sets()
{
	using namespace ::pyicl;
	namespace bp = ::boost::python;
	namespace icl = ::boost::icl;

    interval_set_exposer< icl::interval_set< boost::python::object > >::expose();
    interval_set_exposer< icl::split_interval_set< boost::python::object > >::expose();
    interval_set_exposer< icl::separate_interval_set< boost::python::object > >::expose();
    interval_set_exposer< icl::interval_set< int > >::expose();
	interval_set_exposer< icl::interval_set< float > >::expose();
}
