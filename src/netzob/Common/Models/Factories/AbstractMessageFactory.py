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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory
from netzob.Common.Models.Factories.OldFormatNetworkMessageFactory import OldFormatNetworkMessageFactory
from netzob.Common.Models.Factories.L2NetworkMessageFactory import L2NetworkMessageFactory
from netzob.Common.Models.Factories.L3NetworkMessageFactory import L3NetworkMessageFactory
from netzob.Common.Models.Factories.L4NetworkMessageFactory import L4NetworkMessageFactory
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory
from netzob.Common.Models.Factories.IRPMessageFactory import IRPMessageFactory
from netzob.Common.Models.Factories.IRPDeviceIoControlMessageFactory import IRPDeviceIoControlMessageFactory
from netzob.Common.Models.Factories.RawMessageFactory import RawMessageFactory


class AbstractMessageFactory(object):
    """Factory dedicated to the manipulation of file messages"""

    @staticmethod
    def save(message, root, namespace_project, namespace_common):
        """Generate an XML representation of a message"""
        if message.getType() == "File":
            return FileMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "L2Network":
            return L2NetworkMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "L3Network":
            return L3NetworkMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "L4Network":
            return L4NetworkMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "IPC":
            return IPCMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "IRP":
            return IRPMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "IRPDeviceIoControl":
            return IRPDeviceIoControlMessageFactory.save(message, root, namespace_project, namespace_common)
        elif message.getType() == "RAW":
            return RawMessageFactory.save(message, root, namespace_project, namespace_common)
        else:
            raise NameError('''There is no factory which would support
            the generation of an xml representation of the message : ''' + str(message))

    @staticmethod
    def loadFromXML(rootElement, namespace, version):
        """loadFromXML:
           Function which parses an XML and extract from it
           the definition of a file message
           @param rootElement: XML root of the file message
           @return an instance of a message
           @throw NameError if XML invalid"""

        # Computes which type is it
        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "abstract":
            raise NameError("The parsed xml doesn't represent a valid type message.")

        if rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:FileMessage":
            return FileMessageFactory.loadFromXML(rootElement, namespace, version)
        # Preserve compatibility with former traces
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:NetworkMessage":
            return OldFormatNetworkMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:L2NetworkMessage":
            return L2NetworkMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:L3NetworkMessage":
            return L3NetworkMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:L4NetworkMessage":
            return L4NetworkMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:IPCMessage":
            return IPCMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:IRPMessage":
            return IRPMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:IRPDeviceIoControlMessage":
            return IRPDeviceIoControlMessageFactory.loadFromXML(rootElement, namespace, version)
        elif rootElement.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob-common:RawMessage":
            return RawMessageFactory.loadFromXML(rootElement, namespace, version)
        else:
            raise NameError("The parsed xml doesn't represent a valid type message.")
            return None
