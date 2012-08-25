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
import uuid
#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| RenderingFilter :
#|     Class definition of any filter used for rendering
#+---------------------------------------------------------------------------+
class RenderingFilter(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, superType):
        self.id = uuid.uuid4()
        self.superType = superType
        self.priority = 1

    #+-----------------------------------------------------------------------+
    #| Getter & Setters
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getSuperType(self):
        return self.superType

    def getPriority(self):
        return self.priority

    def setPriority(self, priority):
        self.priority = priority

    @staticmethod
    def save(filter, root, namespace_workspace):
        print "oups"

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """loadFromXML:
           Function which parses an XML and extract from it
           the definition of a rendering filter
           @param rootElement: XML root of the filter
           @return an instance of a filter
           @throw NameError if XML invalid"""

        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract":
            raise NameError("The parsed xml doesn't represent a valid type of filter.")

        filterType = rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract")
        from netzob.Common.Filters.Mathematic.CustomFilter import CustomFilter

        if filterType == "netzob:" + CustomFilter.TYPE:
            return CustomFilter.loadFromXML(rootElement, namespace, version)
        else:
            raise NameError("The parsed xml doesn't represent a know type of filter.")
