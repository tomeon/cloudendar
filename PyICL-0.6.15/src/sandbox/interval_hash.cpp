
#include <boost/icl/interval.hpp>
#include <boost/functional/hash.hpp>

namespace boost {
namespace icl {

//
// Make intervals hashable.
//
inline
std::size_t
hash_value(
    const interval_bounds & x
) {
    return hash< bound_type >()( x.bits() );
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    right_open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    left_open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    closed_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    open_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    discrete_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    hash_combine( seed, x.bounds() );
    return seed;
}


template<
    typename DomainT,
    ICL_COMPARE Compare
>
std::size_t
hash_value(
    continuous_interval< DomainT, Compare > const & x
) {
    std::size_t seed = 0;
    hash_combine( seed, x.lower() );
    hash_combine( seed, x.upper() );
    hash_combine( seed, x.bounds() );
    return seed;
}

} // namespace icl
} // namespace boost


/** Wrapper hash function to make sure boost.python can pick the right one. */
template< typename T >
std::size_t
my_hash( const T & x ) {
    //return boost::icl::hash_value< int >( x );
    return boost::hash< T >()( x );
}


int
main( int argc, char * argv[] ) {
    boost::icl::discrete_interval< int, std::less > i( 0, 10 );
    return my_hash( i );
}
