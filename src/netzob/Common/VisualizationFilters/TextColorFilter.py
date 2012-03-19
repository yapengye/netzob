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
import logging
from netzob.Common.VisualizationFilters.VisualizationFilter import VisualizationFilter
from netzob.Common.Type.Format import Format

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| TextColorFilter:
#|     Definition of a visualization filter wich colorize a text
#+---------------------------------------------------------------------------+
class TextColorFilter(VisualizationFilter):

    TYPE = "TextColorFilter"

    def __init__(self, id, name, iStart, iEnd, color):
        VisualizationFilter.__init__(self, id, TextColorFilter.TYPE, name)
        self.iStart = iStart
        self.iEnd = iEnd
        self.color = color

    def isValid(self, i, message, unitSize):
        factor = (unitSize / float(Format.getUnitSize(Format.HEX)))
        return i >= self.iStart / factor and i <= self.iEnd / factor

    def apply(self, message):
        return '<span foreground="' + self.color + '">' + message + '</span>'
