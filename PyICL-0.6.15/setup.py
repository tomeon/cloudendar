#!/usr/bin/env python
# -*- coding: latin-1 -*-


import os


def get_config_schema():
    from aksetup_helper import ConfigSchema, Option, \
            IncludeDir, LibraryDir, Libraries, BoostLibraries, \
            Switch, StringListOption, make_boost_base_options

    return ConfigSchema(make_boost_base_options() + [
        BoostLibraries("python"),

        StringListOption("CXXFLAGS", ["-Wno-sign-compare"],
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [],
            help="Any extra linker options to include"),
        ])



def read(*fnames):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...
    """
    return open(os.path.join(os.path.dirname(__file__), *fnames)).read()





def main():
    import glob
    from setuptools import Extension, find_packages
    from aksetup_helper import hack_distutils, get_config, setup

    hack_distutils()
    conf = get_config(get_config_schema())

    INCLUDE_DIRS = ["."] + conf["BOOST_INC_DIR"]
    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    EXTRA_DEFINES = { }

    ext_src = [
        "src/pyicl_module.cpp",
        "src/pyicl_intervals.cpp",
        "src/pyicl_interval_sets.cpp",
        "src/pyicl_interval_maps.cpp",
    ]

    try:
        from distutils.command.build_py import build_py_2to3 as build_py
    except ImportError:
        # 2.x
        from distutils.command.build_py import build_py

    setup(
            name                 = "PyICL",
            version              = read('Python', 'pyicl', 'VERSION').strip().split('-')[0],
            description          = "Exposes the boost.icl interval container library to python",
            long_description     = read('Python', 'pyicl', 'README'),
            author               = "John Reid",
            author_email         = "johnbaronreid@netscape.net",
            license              = "BSD",
            url                  = "http://sysbio.mrc-bsu.cam.ac.uk/johns/PyICL/docs/build/html/",
            classifiers          = [
                'Development Status :: 4 - Beta',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: BSD License',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS :: MacOS X',
                'Operating System :: Microsoft :: Windows',
                'Programming Language :: Python',
                'Programming Language :: C++',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: Scientific/Engineering',
                'Topic :: Scientific/Engineering :: Mathematics',
                'Topic :: Office/Business',
                'Topic :: Utilities',
            ],

            packages              = ['pyicl'],
            package_dir           = {'' : 'Python'},
            package_data          = {'pyicl': ['VERSION', 'README', 'LICENSE']},
            include_package_data  = True,
            install_requires      = ['cookbook'],
            ext_modules           = [
                Extension("pyicl._pyicl",
                    ext_src,
                    include_dirs=INCLUDE_DIRS,
                    library_dirs=LIBRARY_DIRS,
                    libraries=LIBRARIES,
                    define_macros=list(EXTRA_DEFINES.items()),
                    extra_compile_args=conf["CXXFLAGS"],
                    extra_link_args=conf["LDFLAGS"],
                ),
            ],

            # 2to3 invocation
            cmdclass               = {'build_py': build_py})




if __name__ == '__main__':
    main()
