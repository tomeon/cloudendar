/** Copyright John Reid 2011, 2012
*/

/**
 * \file Code to name types.
 */



#ifndef PYICL_TYPE_NAME_H_JORE_110217
#define PYICL_TYPE_NAME_H_JORE_110217

namespace pyicl {

/**
 * Struct we specialise to define type names.
 */
template< typename T >
struct type_name_selector {
    static const char * tag() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct type_name_selector must be specialised for this type." );
        return 0;
    }
    static const char * name() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct type_name_selector must be specialised for this type." );
        return 0;
    }
    static const char * lower() {
        BOOST_STATIC_ASSERT_MSG( sizeof(T) == 0, "struct type_name_selector must be specialised for this type." );
        return 0;
    }
};

/// Specialisation
template<>
struct type_name_selector< int > {
    static const char * tag() { return "Int"; }
    static const char * name() { return "Int"; }
    static const char * lower() { return "int"; }
};


/// Specialisation
template<>
struct type_name_selector< float > {
    static const char * tag() { return "Float"; }
    static const char * name() { return "Float"; }
    static const char * lower() { return "float"; }
};


/// Specialisation
template<>
struct type_name_selector< std::string > {
    static const char * tag() { return "String"; }
    static const char * name() { return "String"; }
    static const char * lower() { return "string"; }
};


/// Specialisation
template<>
struct type_name_selector< ::boost::python::object > {
    static const char * tag() { return ""; }
    static const char * name() { return "Object"; }
    static const char * lower() { return "object"; }
};


} // namespace pyicl

#endif //PYICL_TYPE_NAME_H_JORE_110217
