/** Copyright John Reid 2010, 2011, 2012
*/


#include <boost/python.hpp>
#include <iostream>

void expose_intervals();
void expose_interval_sets();
void expose_interval_maps();

namespace bp = ::boost::python;

BOOST_PYTHON_MODULE( _pyicl )
{
#ifndef NDEBUG
	bp::scope().attr( "__debug__" ) = 1;
	std::cout << "WARNING: Debug version of _pyicl module loaded. If you did not intend this then check your configuration!" << std::endl;
#else //_DEBUG
	bp::scope().attr( "__debug__" ) = 0;
#endif //_DEBUG

	expose_intervals();
	expose_interval_sets();
	expose_interval_maps();
}
