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

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid
import random

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.ExporterPlugin import ExporterPlugin
from netzob_plugins.Exporters.PeachExporter.EntryPoints.GlobalMenuEntryPoint import GlobalMenuEntryPoint
from netzob_plugins.Exporters.PeachExporter.PeachExportController import PeachExportController


#+---------------------------------------------------------------------------+
#| PeachExporter: Export netzob symbols to Peach pit files
#+---------------------------------------------------------------------------+
class PeachExporterPlugin(ExporterPlugin):

    __plugin_name__ = "PeachExporter"
    __plugin_version__ = "0.1"
    __plugin_description__ = _("Provide the possibility to export netzob symbols to Peach pit files.")
    __plugin_author__ = "Benjamin Dufour <benjamin.dufour@amossys.fr>"

    def __init__(self, netzob):
        ExporterPlugin.__init__(self, netzob)
        self.entryPoints = [GlobalMenuEntryPoint(self.getNetzob())]

    def getName(self):
        return self.__plugin_name__

    def getVersion(self):
        return self.__plugin_version__

    def getDescription(self):
        return self.__plugin_description__

    def getAuthor(self):
        return self.__plugin_author__

    def getEntryPoints(self):
        return self.entryPoints

    def setVal(self, val):
        self.val = val
