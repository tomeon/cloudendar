/** Copyright John Reid 2011, 2012
*/

/**
 * \file Code for maximising values.
 */



#ifndef PYICL_MAXIMISER_H_JORE_120518
#define PYICL_MAXIMISER_H_JORE_120518

#include <pyicl/base.h>
#include <pyicl/type_name.h>

namespace pyicl {


/**
 * Class that implements += as a max operation
 */
template< typename Value >
struct maximiser
: boost::addable< maximiser< Value > >
, boost::equality_comparable< maximiser< Value > >
, boost::equality_comparable< maximiser< Value >, Value >
, boost::less_than_comparable< maximiser< Value > >
, boost::less_than_comparable< maximiser< Value >, Value >
{
public:
    typedef Value value_t;
    typedef maximiser< value_t > self_t;

    maximiser() : _value( Value() ) {}
    maximiser( value_t value ) : _value( value ) {}

    value_t value() const { return _value; }

    self_t operator+=( const self_t & right ) {
        return maximiser< value_t >( std::max( _value, right._value ) );
    }

    bool operator==( const self_t & right ) const {
        return _value == right._value;
    }

    bool operator<( const self_t & right ) const {
        return _value < right._value;
    }

    //operator value_t() const { return _value; }

    friend
    std::ostream &
    operator<<( std::ostream & os, const self_t & m ) {
        return os << m.value();
    }

    Value _value;
};


template< typename Value >
struct compare {
    static
    Value
    __cmp__( const maximiser< Value > & left, const maximiser< Value > * right ) {
        if( 0 == right ) {
            return Value( 1 );
        }
        return left._value - right->_value;
    }
};

// Specialise for objects
template<>
struct compare< boost::python::object > {
    static
    boost::python::object
    __cmp__( maximiser< boost::python::object > left, maximiser< boost::python::object > * right ) {
        if( 0 == right ) {
            return boost::python::object( 1 );
        }
        return left._value.attr( "__cmp__" )( right->_value );
    }
};

template< typename Value >
std::size_t
hash_value( maximiser< Value > const & m )
{
    boost::hash< Value > hasher;
    return hasher( m.value() );
}


/**
 * Helper struct to make operators visible for boost.python.
 */
template< typename T >
struct less_than_comparable
{
    static bool lt( const T & x, const T * y ) { return 0 != y && x < *y; }
    static bool le( const T & x, const T * y ) { return 0 != y && x <= *y; }
    static bool gt( const T & x, const T * y ) { return 0 == y && x > *y; }
    static bool ge( const T & x, const T * y ) { return 0 == y && x >= *y; }
};



/**
 * Helper struct to make operators visible for boost.python.
 */
template< typename T >
struct equality_comparable
{
    static bool eq( const T & x, const T * y ) { return 0 != y && x == *y; }
    static bool ne( const T & x, const T * y ) { return 0 != y && x != *y; }
};


template< typename Value >
maximiser< Value >
iadd( maximiser< Value > & left, const maximiser< Value > * right ) {
    return 0 == right
        ? maximiser< Value >( left._value )
        : left += *right;
}


template< typename Value >
maximiser< Value >
add( maximiser< Value > & left, const maximiser< Value > * right ) {
    return 0 == right
        ? maximiser< Value >( left._value )
        : left + *right;
}



/**
 * Expose a maximiser.
 */
template< typename Maximiser >
struct maximiser_exposer {

    typedef Maximiser exposed_t;
    typedef typename exposed_t::value_t value_t;

    /// For pickling
    struct _pickle_suite : boost::python::pickle_suite
    {
        static
        boost::python::tuple
        getinitargs( const exposed_t & x )
        {
            return boost::python::make_tuple( x.value() );
        }
    };

    /// Expose/register the interval container.
    static
    void
    expose() {
        namespace bp = ::boost::python;
        namespace icl = ::boost::icl;

        bp::class_< exposed_t > bp_class(
            PYICL_MAKE_STRING( type_name_selector< value_t >::tag() << "Max" ).c_str(),
            "Holds a value where += operation is implemented as maximisation.",
            bp::init< value_t >( "Contructs a maximiser." )
        );

        // pickling
        bp_class.def_pickle( _pickle_suite() );

        bp_class.add_property( "value", &exposed_t::value, "The value of the maximiser." );
        bp_class.def( "__iadd__", &iadd< value_t >, "+= operator implemented as maximisation." );
        bp_class.def( "__add__", &add< value_t >, "+ operator implemented as maximisation." );
        bp_class.def( "__str__", &::pyicl::convert_to_str< exposed_t >, "String representation." );
        bp_class.def( "__cmp__", &compare< value_t >::__cmp__ );
        bp_class.def( "__lt__", &less_than_comparable< exposed_t >::lt );
        bp_class.def( "__le__", &less_than_comparable< exposed_t >::le );
        bp_class.def( "__gt__", &less_than_comparable< exposed_t >::gt );
        bp_class.def( "__ge__", &less_than_comparable< exposed_t >::ge );
        bp_class.def( "__eq__", &equality_comparable< exposed_t >::eq );
        bp_class.def( "__ne__", &equality_comparable< exposed_t >::ne );

        bp::implicitly_convertible< typename exposed_t::value_t, exposed_t >();
    }

};



/// Specialisation
template<>
struct type_name_selector< maximiser< float > > {
    static const char * tag() { return "FloatMax"; }
    static const char * name() { return "FloatMax"; }
    static const char * lower() { return "floatmax"; }
};




} // namespace pyicl

#endif //PYICL_MAXIMISER_H_JORE_120518
