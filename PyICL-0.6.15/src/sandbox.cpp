// The next line includes <boost/gregorian/date.hpp>
// and a few lines of adapter code.
#include <boost/icl/gregorian.hpp>
#include <iostream>
#include <boost/icl/interval_map.hpp>

using namespace std;
using namespace boost::gregorian;
using namespace boost::icl;

// Type icl::set<string> collects the names a user group's members. Therefore
// it needs to implement operator += that performs a set union on overlap of
// intervals.
typedef std::set<string> MemberSetT;

// boost::gregorian::date is the domain type the interval map.
// It's key values are therefore time intervals: discrete_interval<date>. The content
// is the set of names: MemberSetT.
typedef interval_map<date, MemberSetT> MembershipT;

// Collect user groups for medical and administrative staff and perform
// union and intersection operations on the collected membership schedules.
void user_groups()
{
    MemberSetT mary_harry;
    mary_harry.insert("Mary");
    mary_harry.insert("Harry");

    MemberSetT diana_susan;
    diana_susan.insert("Diana");
    diana_susan.insert("Susan");

    MemberSetT chief_physician;
    chief_physician.insert("Dr.Jekyll");

    MemberSetT director_of_admin;
    director_of_admin.insert("Mr.Hyde");

    //----- Collecting members of user group: med_users -------------------
    MembershipT med_users;

    med_users.add( // add and element
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-01-01"), from_string("2008-12-31")), mary_harry));

    med_users +=  // element addition can also be done via operator +=
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-01-15"), from_string("2008-12-31")),
          chief_physician);

    med_users +=
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-02-01"), from_string("2008-10-15")),
          director_of_admin);

    //----- Collecting members of user group: admin_users ------------------
    MembershipT admin_users;

    admin_users += // element addition can also be done via operator +=
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-03-20"), from_string("2008-09-30")), diana_susan);

    admin_users +=
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-01-15"), from_string("2008-12-31")),
          chief_physician);

    admin_users +=
      make_pair(
        discrete_interval<date>::closed(
          from_string("2008-02-01"), from_string("2008-10-15")),
          director_of_admin);

    MembershipT all_users   = med_users + admin_users;

    MembershipT super_users = med_users & admin_users;

    MembershipT::iterator med_ = med_users.begin();
    cout << "----- Membership of medical staff -----------------------------------\n";
    while(med_ != med_users.end())
    {
        discrete_interval<date> when = (*med_).first;
        // Who is member of group med_users within the time interval 'when' ?
        MemberSetT who = (*med_++).second;
        cout << "[" << first(when) << " - " << last(when) << "]"
             << ": " << who << endl;
    }

    MembershipT::iterator admin_ = admin_users.begin();
    cout << "----- Membership of admin staff -------------------------------------\n";
    while(admin_ != admin_users.end())
    {
        discrete_interval<date> when = (*admin_).first;
        // Who is member of group admin_users within the time interval 'when' ?
        MemberSetT who = (*admin_++).second;
        cout << "[" << first(when) << " - " << last(when) << "]"
             << ": " << who << endl;
    }

    MembershipT::iterator all_ = all_users.begin();
    cout << "----- Membership of all users (med + admin) -------------------------\n";
    while(all_ != all_users.end())
    {
        discrete_interval<date> when = (*all_).first;
        // Who is member of group med_users OR admin_users ?
        MemberSetT who = (*all_++).second;
        cout << "[" << first(when) << " - " << last(when) << "]"
             << ": " << who << endl;
    }

    MembershipT::iterator super_ = super_users.begin();
    cout << "----- Membership of super users: intersection(med,admin) ------------\n";
    while(super_ != super_users.end())
    {
        discrete_interval<date> when = (*super_).first;
        // Who is member of group med_users AND admin_users ?
        MemberSetT who = (*super_++).second;
        cout << "[" << first(when) << " - " << last(when) << "]"
             << ": " << who << endl;
    }

}


int main()
{
    cout << ">>Interval Container Library: Sample user_groups.cpp <<\n";
    cout << "-------------------------------------------------------\n";
    user_groups();
    return 0;
}

// Program output:
/*-----------------------------------------------------------------------------
>>Interval Container Library: Sample user_groups.cpp <<
-------------------------------------------------------
----- Membership of medical staff -----------------------------------
[2008-Jan-01 - 2008-Jan-14]: Harry Mary
[2008-Jan-15 - 2008-Jan-31]: Dr.Jekyll Harry Mary
[2008-Feb-01 - 2008-Oct-15]: Dr.Jekyll Harry Mary Mr.Hyde
[2008-Oct-16 - 2008-Dec-31]: Dr.Jekyll Harry Mary
----- Membership of admin staff -------------------------------------
[2008-Jan-15 - 2008-Jan-31]: Dr.Jekyll
[2008-Feb-01 - 2008-Mar-19]: Dr.Jekyll Mr.Hyde
[2008-Mar-20 - 2008-Sep-30]: Diana Dr.Jekyll Mr.Hyde Susan
[2008-Oct-01 - 2008-Oct-15]: Dr.Jekyll Mr.Hyde
[2008-Oct-16 - 2008-Dec-31]: Dr.Jekyll
----- Membership of all users (med + admin) -------------------------
[2008-Jan-01 - 2008-Jan-14]: Harry Mary
[2008-Jan-15 - 2008-Jan-31]: Dr.Jekyll Harry Mary
[2008-Feb-01 - 2008-Mar-19]: Dr.Jekyll Harry Mary Mr.Hyde
[2008-Mar-20 - 2008-Sep-30]: Diana Dr.Jekyll Harry Mary Mr.Hyde Susan
[2008-Oct-01 - 2008-Oct-15]: Dr.Jekyll Harry Mary Mr.Hyde
[2008-Oct-16 - 2008-Dec-31]: Dr.Jekyll Harry Mary
----- Membership of super users: intersection(med,admin) ------------
[2008-Jan-15 - 2008-Jan-31]: Dr.Jekyll
[2008-Feb-01 - 2008-Oct-15]: Dr.Jekyll Mr.Hyde
[2008-Oct-16 - 2008-Dec-31]: Dr.Jekyll
-----------------------------------------------------------------------------*/



#if 0

#include <boost/icl/interval.hpp>
#include <iostream>

int main( int argc, char * argv[] ) {
	return boost::icl::has_dynamic_bounds<boost::icl::continuous_interval<float, std::less> >::value;
}

template< typename IntervalT >
void
check_equals() {
	IntervalT interval( 0, 0 );
	interval == interval;
}

template< typename IntervalT >
void
check_contains() {
	IntervalT interval;
	typedef typename IntervalT::domain_type domain_t;
	::boost::icl::contains( interval, domain_t() );
}

void h() {
	namespace icl = ::boost::icl;
	check_contains< icl::continuous_interval< float > >();
	check_contains< icl::discrete_interval< int > >();
	check_contains< icl::right_open_interval< float > >();
	check_contains< icl::left_open_interval< float > >();
	//check_contains< icl::closed_interval< float > >();
	//check_contains< icl::open_interval< float > >();
	//check_equals< icl::closed_interval< float > >();
	//check_equals< icl::open_interval< float > >();
}

int main_( int argc, char * argv[] ) {
  namespace icl = ::boost::icl;

  std::cout << "Float is continuous: " << icl::is_continuous< float >::value << "\n";

  return 0;
}
#endif

#if 0
void f() {
  namespace icl = ::boost::icl;

  icl::interval_set<int> int_set;
  icl::add( int_set, 0 );
  icl::add( int_set, icl::interval<  int>::type( 0, 1 ) );
  int_set += 0;
  int_set += icl::interval<  int>::type( 0, 1 );

  icl::subtract( int_set, 0 );
  icl::subtract( int_set, icl::interval< int >::type( 0, 1 ) );
  int_set -= 0;
  int_set -= icl::interval< int >::type( 0, 1 );

  int_set &= 0;
  int_set &= icl::interval< int >::type( 0, 1 );

  int_set ^= ( icl::interval< int >::type( 0, 1 ) );
}

void g() {
	namespace icl = ::boost::icl;
	typedef float type_;
	icl::interval_set< type_ > set;
	set.add( icl::interval< type_ >::type( 0, 2 ) );
	set.add( icl::interval< type_ >::type( 5, 7 ) );
	set.find( icl::interval< type_ >::type( 0, 9 ) );

#if 0
	icl::interval_map< float, int >().find( 0 );

	icl::interval_set< float >().find( 0 );

	icl::contains( icl::interval_set< float >(), 0 );

	icl::add( icl::interval_set< int >(), 0 );
	icl::add( icl::interval_set< int >(), icl::interval< int >::type( 0, 1 ) );
	icl::interval_set< int >() += 0;
	icl::interval_set< int >() += icl::interval< int >::type( 0, 1 );

	icl::subtract( icl::interval_set< int >(), 0 );
	icl::subtract( icl::interval_set< int >(), icl::interval< int >::type( 0, 1 ) );
	icl::interval_set< int >() -= 0;
	icl::interval_set< int >() -= icl::interval< int >::type( 0, 1 );

	icl::interval_set< int >() &= 0;
	icl::interval_set< int >() &= icl::interval< int >::type( 0, 1 );

	icl::interval_set< int >() ^= ( icl::interval< int >::type( 0, 1 ) );
#endif
}
#endif


#if 0
#include <boost/type_traits/has_operator_minus.hpp>
#include <string>

template< typename T >
T g( T x, T y ) {
	if( boost::has_operator_minus<T, T, T>::value ) {
		return x - y;
	} else {
		return T();
	}
}

template void g< std::string >( std::string, std::string );


template< typename T >
struct A {
    void register_fns() {
    	&A::subtract;
    }

    T subtract( T x, T y ) {
    	if( boost::has_operator_minus<T, T, T>::value ) {
    		return x - y;
    	} else {
    		return T();
    	}
    }
};

void test() {
	A< int >().register_fns(); // Fine
	//A< std::string >().register_fns(); // Compile error
}


#include <boost/icl/interval.hpp>
#include <boost/icl/interval_set.hpp>
#include <boost/icl/interval_map.hpp>
namespace icl = ::boost::icl;

void f() {
	icl::interval< int > int_interval;
	icl::interval_set< int > int_set;
	icl::interval_map< int, int > int_map;
	icl::interval_map< int, int >::element_type int_element;
	icl::interval_map< int, int >::segment_type int_segment;

	// AFAICT none of the following lines compiles
	icl::lower( int_interval );
	icl::upper( int_interval );
	icl::first( int_interval );
	icl::last( int_interval );
	icl::add( int_set, int_set );
	icl::add( int_map, int_map );
	icl::subtract( int_set, int_set );
	icl::subtract( int_map, int_map );
	int_set += int_interval;
	icl::disjoint( int_map, int_element );
	icl::disjoint( int_map, int_segment );
	icl::intersects( int_map, int_segment );
	icl::intersects( int_map, int_element );
}

void f() {
	icl::lower( icl::interval_set< int >() );
}

#include <boost/icl/interval_set.hpp>
void interval_set_intersects() {
	icl::intersects( icl::interval_set< int >(), 1 );
}

#include <boost/icl/continuous_interval.hpp>
#include <boost/icl/interval.hpp>
void hull_typename() {
	typedef icl::interval< float >::type interval_type;

	icl::hull( interval_type(), interval_type() );
}
#endif
