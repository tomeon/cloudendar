..
.. Copyright John Reid 2012
..
.. This is a reStructuredText document. If you are reading this in text format, it can be 
.. converted into a more readable format by using Docutils_ tools such as rst2html.
..

.. _Docutils: http://docutils.sourceforge.net/docs/user/tools.html




Introduction to PyICL
=====================

The PyICL module exposes the functionality of the C++
`Boost Interval Container Library`_ to python. The author Joachim Faulhaber introduces
his C++ library thus:

    Intervals are almost ubiquitous in software development. Yet they are very easily coded into 
    user defined classes by a pair of numbers so they are only implicitly used most of the time. 
    The meaning of an interval is simple. They represent all the elements between their lower and 
    upper bound and thus a set. But unlike sets, intervals usually can not be added to a single 
    new interval. If you want to add intervals to a collection of intervals that does still 
    represent a set, you arrive at the idea of interval_sets provided by this library.

    Interval containers of the ICL have been developed initially at
    `Cortex Software GmbH <http://www.cortex-software.de/desktopdefault.aspx>`_
    to solve problems related to date and time interval computations in the context of a Hospital 
    Information System. Time intervals with associated values like amount of invoice or set 
    of therapies had to be manipulated in statistics, billing programs and therapy scheduling 
    programs. So the ICL emerged out of those industrial use cases. It extracts generic code 
    that helps to solve common problems from the date and time problem domain and can be 
    beneficial in other fields as well.

    One of the most advantageous aspects of interval containers is their very compact 
    representation of sets and maps. Working with sets and maps of elements can be very 
    inefficient, if in a given problem domain, elements are typically occurring in 
    contiguous chunks. Besides a compact representation of associative containers, 
    that can reduce the cost of space and time drastically, the ICL comes with a 
    universal mechanism of aggregation, that allows to combine associated values 
    in meaningful ways when intervals overlap on insertion.


.. _Boost Interval Container Library: http://www.boost.org/libs/icl/doc/html




Table of Contents
=================

.. toctree::
   :maxdepth: 2
   
   installation
   usage
   types
   examples
   boost-differences





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

