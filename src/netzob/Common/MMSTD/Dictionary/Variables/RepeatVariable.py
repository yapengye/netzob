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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from lxml import etree
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import \
    AbstractVariable
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class RepeatVariable(AbstractVariable):
    """RepeatVariable:
            A variable with one child that repeats a certain time every treatment on this child.
    """

    MAX_ITERATIONS = 10
    TYPE = "RepeatVariable"

    def __init__(self, id, name, mutable, random, child, minIterations, maxIterations):
        """Constructor of RepeatVariable:
                Each treatment will be repeated at most maxIterations time.
                Each function will call once by iteration its equivalent in the class on the children.
                During an iteration, if the child treatment failed, we canceled the iteration loop.
                If we had done less than minIteration, the global processing is considered failed, else it is considered successful.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable
                @param child: the unique child which treatments will be repeated.
                @type minIterations: integer
                @param minIterations: the minimum number of iteration each treatment have to be repeated.
                @type maxIterations: integer
                @param maxIterations: the maximum number of iteration each treatment will be repeated.
        """
        AbstractVariable.__init__(self, id, name, mutable, random)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.RepeatVariable.py')
        if child is not None:
            self.child = child
        else:
            self.log.info(_("Variable {0} (Repeat): Construction of RepeatVariable: no child given.").format(self.getName()))
        if minIterations is not None and minIterations >= 0:
            self.minIterations = minIterations
        else:
            self.log.info(_("Variable {0} (Repeat): Construction of RepeatVariable: minIterations undefined or < 0. minIterations value is fixed to 0.").format(self.getName()))
            self.minIterations = 0
        if maxIterations is not None and maxIterations >= minIterations:
            self.maxIterations = maxIterations
        else:
            self.log.info(_("Variable {0} (Repeat): Construction of RepeatVariable: maxIterations undefined or < minIterations. maxIterations value is fixed to minIterations.").format(self.getName()))
            self.maxIterations = self.minIterations

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getVariableType(self):
        """getVariableType:
        """
        return RepeatVariable.TYPE

    def toString(self):
        """toString:
        """
        return _("[Repeat] {0}, iterations: ({1}, {2})").format(AbstractVariable.toString(self), str(self.minIterations), str(self.maxIterations))

    def getDescription(self, processingToken):
        """getDescription:
        """
        return _("[{0}, child:\n - {1}]").format(self.toString(), self.child.getDescription(processingToken))

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        return _("[{0}, child:\n - {1}]").format(self.toString(), self.child.getUncontextualizedDescription())

    def isDefined(self):
        return self.child.isDefined()

    def read(self, readingToken):
        """read:
                The pointed variable reads the value.
        """
        self.log.debug(_("[ {0}: read access:").format(self.toString()))
        (minIterations, maxIterations) = self.getNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.read(readingToken)
            if readingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            readingToken.setOk(False)
        else:
            readingToken.setOk(True)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), readingToken.toString()))

    def write(self, writingToken):
        """write:
                The pointed variable writes its value.
        """
        self.log.debug(_("[ {0}: write access:").format(self.toString()))
        (minIterations, maxIterations) = self.getNumberIterations()
        successfullIterations = 0
        for i in range(maxIterations):
            self.child.write(writingToken)
            if writingToken.isOk():
                successfullIterations += 1
            else:
                break
        # We search if we have done the minimum number of iterations.
        if successfullIterations < minIterations:
            writingToken.setOk(False)
        else:
            writingToken.setOk(True)
        self.log.debug(_("Variable {0}: {1}. ]").format(self.getName(), writingToken.toString()))

    def toXML(self, root, namespace):
        """toXML:
            Creates the xml tree associated to this variable.
            Adds every child's own xml definition as xml child to this tree.
        """
        self.log.debug(_("[ {0}: toXML:").format(self.toString()))
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:RepeatVariable")
        xmlVariable.set("mutable", str(self.isMutable()))
        xmlVariable.set("random", str(self.isRandom()))

        # Definition of child variable
        self.child.toXML(xmlVariable, namespace)

        # minIterations
        xmlMinIterations = etree.SubElement(xmlVariable, "{" + namespace + "}minIterations")
        xmlMinIterations.text = str(self.minIterations)

        # maxIterations
        xmlMaxIterations = etree.SubElement(xmlVariable, "{" + namespace + "}maxIterations")
        xmlMaxIterations.text = str(self.maxIterations)
        self.log.debug(_("Variable {0}. ]").format(self.getName()))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getNumberIterations(self):
        if self.isRandom():
            x = random.randint(0, RepeatVariable.MAX_ITERATIONS)
            y = random.randint(0, RepeatVariable.MAX_ITERATIONS)
            self.minIterations = min(x, y)
            self.maxIterations = max(x, y)
        return (self.minIterations, self.maxIterations)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        """loadFromXML:
                Loads a repeat variable from an XML definition.
                We do not trust the user and check every field (even mandatory).
        """
        logging.debug(_("[ RepeatVariable: loadFromXML:"))
        if version == "0.1":
            xmlID = xmlRoot.get("id")
            xmlName = xmlRoot.get("name")
            xmlMutable = xmlRoot.get("mutable")
            xmlRandom = xmlRoot.get("random")

            xmlChild = xmlRoot.find("{" + namespace + "}variable")
            child = AbstractVariable.loadFromXML(xmlChild, namespace, version)

            # minIterations
            xmlMinIterations = xmlRoot.find("{" + namespace + "}minIterations")
            if xmlMinIterations is not None:
                minIterations = int(xmlMinIterations.text)
            else:
                minIterations = 0

            # maxIterations
            xmlMaxIterations = xmlRoot.find("{" + namespace + "}maxIterations")
            if xmlMaxIterations is not None:
                maxIterations = int(xmlMaxIterations.text)
            else:
                maxIterations = RepeatVariable.MAX_ITERATIONS

            result = RepeatVariable(xmlID, xmlName, xmlMutable, xmlRandom, child, minIterations, maxIterations)
            logging.debug(_("RepeatVariable: loadFromXML successes: {0} ]").format(result.toString()))
            return result
        logging.debug(_("RepeatVariable: loadFromXML fails"))
        return None
