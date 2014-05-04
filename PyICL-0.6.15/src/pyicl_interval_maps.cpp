/** Copyright John Reid 2010, 2011, 2012
*/


#include <pyicl/interval_map.h>
#include <pyicl/object.h>
#include <pyicl/object_combine.h>

namespace bp = ::boost::python;

bp::object boost::icl::identity_element< boost::python::object >::_value = boost::python::object();



//namespace boost{
//namespace icl {
//
//template<>
//struct identity_element< int >
//{
//    static
//    int value()
//    {
//        return 0;
//    }
//};
//
//} // namespace icl
//} // namespace boost


/**
 * Expose interval maps for a particular interval domain.
 */
template< typename DomainT >
void
expose_interval_maps_for_domain() {
    using namespace ::pyicl;
    namespace icl = ::boost::icl;

    interval_map_exposer< icl::interval_map      < DomainT, bp::object, icl::partial_absorber, ICL_COMPARE_INSTANCE( std::less, bp::object ), ICL_COMBINE_INSTANCE( combine_objects, bp::object ) > >::expose();
    interval_map_exposer< icl::split_interval_map< DomainT, bp::object, icl::partial_absorber, ICL_COMPARE_INSTANCE( std::less, bp::object ), ICL_COMBINE_INSTANCE( combine_objects, bp::object ) > >::expose();
    interval_map_exposer< icl::interval_map< DomainT, int > >::expose();
    interval_map_exposer< icl::interval_map< DomainT, float > >::expose();
    interval_map_exposer< icl::interval_map< DomainT, std::string > >::expose();
}

/**
 * Expose interval maps.
 */
void
expose_interval_maps()
{
	using namespace ::pyicl;
	namespace icl = ::boost::icl;

    bp::scope().attr( "identity_element" ) = boost::icl::identity_element< boost::python::object >::_value;
    //bp::scope().attr( "identity_registry" ) = identity_registry;

    expose_interval_maps_for_domain< bp::object >();
    expose_interval_maps_for_domain< int >();
    expose_interval_maps_for_domain< float >();

    maximiser_exposer< maximiser< bp::object > >::expose();
    maximiser_exposer< maximiser< int > >::expose();
    maximiser_exposer< maximiser< float > >::expose();
}
