#!/usr/bin/env python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+----------------------------------------------------------------------------
#| Global Imports
#+----------------------------------------------------------------------------
import sys
sys.path.insert(0, 'src/')
import os
import uuid
from setuptools import setup, Extension, find_packages
from netzob import release
from resources.sdist.manpage_command import manpage_command
from resources.sdist.pybuild_command import pybuild_command

#+----------------------------------------------------------------------------
#| Definition of variables
#+----------------------------------------------------------------------------
# Path to the resources
staticResourcesPath = os.path.join("resources", "static")
netzobStaticResourcesPath = os.path.join(staticResourcesPath, "netzob")
pluginsStaticResourcesPath = os.path.join(staticResourcesPath, "plugins")

#+----------------------------------------------------------------------------
#| C Extensions
#+----------------------------------------------------------------------------
# Includes path
libPath = "lib"
includesPath = os.path.join(libPath, "includes")
pyIncludesPath = os.path.join(includesPath, "Py_lib")
includes = [includesPath, pyIncludesPath]

# Interface path
interfacePath = os.path.join(libPath, "interface")
pyInterfacePath = os.path.join(interfacePath, "Py_lib")

# Needleman path
needlemanPath = os.path.join(libPath, "libNeedleman")
pyNeedlemanPath = os.path.join(needlemanPath, "Py_lib")

# ArgsFactories path
argsFactoriesPath = os.path.join(libPath, "argsFactories")

# Regex path
regexPath = os.path.join(libPath, "libRegex")
pyRegexPath = os.path.join(regexPath, "Py_lib")

# Tools path
toolsPath = os.path.join(libPath, "tools")

# Generate the random binary identifier BID
macros = [('BID', '"{0}"'.format(uuid.uuid4()))]

# Module Needleman
moduleLibNeedleman = Extension('_libNeedleman',
#                               extra_compile_args=["-fopenmp"],
#                               extra_link_args=["-fopenmp"],
                               sources=[os.path.join(interfacePath, "Interface.c"),
                                        os.path.join(pyInterfacePath, "libInterface.c"),
                                        os.path.join(pyNeedlemanPath, "libNeedleman.c"),
                                        os.path.join(needlemanPath, "Needleman.c"),
                                        os.path.join(needlemanPath, "scoreComputation.c"),
                                        os.path.join(argsFactoriesPath, "factory.c"),
                                        os.path.join(regexPath, "regex.c"),
                                        os.path.join(regexPath, "manipulate.c"),
                                        os.path.join(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module ScoreComputation
moduleLibScoreComputation = Extension('_libScoreComputation',
#                               extra_compile_args=["-fopenmp"],
#                               extra_link_args=["-fopenmp"],
                               sources=[os.path.join(needlemanPath, "scoreComputation.c"),
                                        os.path.join(pyNeedlemanPath, "libScoreComputation.c"),
                                        os.path.join(needlemanPath, "Needleman.c"),
                                        os.path.join(interfacePath, "Interface.c"),
                                        os.path.join(pyInterfacePath, "libInterface.c"),
                                        os.path.join(argsFactoriesPath, "factory.c"),
                                        os.path.join(regexPath, "regex.c"),
                                        os.path.join(regexPath, "manipulate.c"),
                                        os.path.join(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module Interface
moduleLibInterface = Extension('_libInterface',
                               sources=[os.path.join(interfacePath, "Interface.c"),
                                        os.path.join(pyInterfacePath, "libInterface.c"),
                                        os.path.join(toolsPath, "getBID.c")],
                               define_macros=macros,
                               include_dirs=includes)

# Module Regex
moduleLibRegex = Extension('_libRegex',
                               sources=[os.path.join(regexPath, "regex.c"),
                                        os.path.join(pyRegexPath, "libRegex.c"),
                                        os.path.join(regexPath, "manipulate.c"),
                                        os.path.join(toolsPath, "getBID.c")],
                                define_macros=macros,
                               include_dirs=includes)

#+----------------------------------------------------------------------------
#| Definition of the dependencies
#+----------------------------------------------------------------------------
dependencies = [
    'python-ptrace',
    'matplotlib',
    'pcapy',
    'bitarray',
    'lxml',
]

#+----------------------------------------------------------------------------
#| Extensions in the build operations (create manpage, i18n, ...)
#+----------------------------------------------------------------------------
CMD_CLASS = {
             'build_py': pybuild_command,
             'build_manpage': manpage_command
             }

#+----------------------------------------------------------------------------
#| Activate Babel (i18n) if available
#+----------------------------------------------------------------------------
try:
    from babel.messages import frontend as babel
    from distutils.command.build import build

    CMD_CLASS.update({'compile_catalog': babel.compile_catalog,
                      'extract_messages': babel.extract_messages,
                      'init_catalog': babel.init_catalog,
                      'update_catalog': babel.update_catalog})

    build.sub_commands.append(('compile_catalog', None))
except ImportError:
    print "Info: Babel support unavailable, translations not available"

#+----------------------------------------------------------------------------
#| Definition of Netzob for setup
#+----------------------------------------------------------------------------
setup(
    name=release.name,
    packages=find_packages(where='src'),
    package_dir={"netzob": "src" + os.sep + "netzob", "netzob_plugins": "src" + os.sep + "netzob_plugins"},
    ext_modules=[moduleLibNeedleman, moduleLibScoreComputation, moduleLibInterface, moduleLibRegex],
    data_files=[
        (os.path.join("share", "netzob"), [os.path.join(netzobStaticResourcesPath, "logo.png")]),
        (os.path.join("share", "applications"), [os.path.join(netzobStaticResourcesPath, "netzob.desktop")]),
        (os.path.join("share", "icons", "hicolor", "22x22", "apps"), [os.path.join(netzobStaticResourcesPath, "icons", "22x22", "netzob.png")]),
        (os.path.join("share", "icons", "hicolor", "48x48", "apps"), [os.path.join(netzobStaticResourcesPath, "icons", "48x48", "netzob.png")]),
        (os.path.join("share", "icons", "hicolor", "64x64", "apps"), [os.path.join(netzobStaticResourcesPath, "icons", "64x64", "netzob.png")]),
        (os.path.join("share", "netzob", "defaults"), [os.path.join(netzobStaticResourcesPath, "defaults", "repository.xml.default")]),
        (os.path.join("share", "netzob", "defaults"), [os.path.join(netzobStaticResourcesPath, "defaults", "logging.conf.default")]),
        (os.path.join("share", "netzob", "xsds", "0.1"), [os.path.join(netzobStaticResourcesPath, "xsds", "0.1", "Workspace.xsd"),
                                             os.path.join(netzobStaticResourcesPath, "xsds", "0.1", "Project.xsd"),
                                             os.path.join(netzobStaticResourcesPath, "xsds", "0.1", "common.xsd")]),
        (os.path.join("share", "locale", "fr", "LC_MESSAGES"), [os.path.join(netzobStaticResourcesPath, "locales", "fr", "LC_MESSAGES", "netzob.mo")])
        ],
    scripts=["netzob"],
    install_requires=dependencies,
    version=release.version,
    license=release.licenseName,
    description=release.description,
    platforms=release.platforms,
    author=release.author,
    author_email=release.author_email,
    url=release.url,
    download_url=release.download_url,
    keywords=release.keywords,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking",
        ],
    long_description=release.long_description,
    cmdclass=CMD_CLASS,
    entry_points="""
        [netzob.plugins]
            delemiterSeparatedImporter = netzob_plugins.Importers.DelimiterSeparatedImporter.DelimiterSeparatedImporterPlugin:DelimiterSeparatedImporterPlugin
            pcapImporter = netzob_plugins.Importers.PCAPImporter.PCAPImporterPlugin:PCAPImporterPlugin
            ospyImporter = netzob_plugins.Importers.OSpyImporter.OSpyImporterPlugin:OSpyImporterPlugin
            xmlImporter = netzob_plugins.Importers.XMLImporter.XMLImporterPlugin:XMLImporterPlugin
        """,
    # Files that should be scanned by Babel (if available)
    message_extractors={
        'src': [('**.py', 'python', None)]
        },
    )
