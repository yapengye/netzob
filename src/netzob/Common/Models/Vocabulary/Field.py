#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken


class InvalidDomainException(Exception):
    pass


class Field(AbstractField):
    """A symbol structure follows a format that specifies a sequence of expected fields:
    e.g. TCP segments contains expected fields as sequence number and checksum.

    Fields have either a fixed or variable size.
    A field can similarly be composed of sub-elements (such as a payload field).
    Therefore, by considering the concept of protocol layer as a kind of particular field,
    it is possible to retrieve the protocol stack (e.g. TCP encapsulated in IP, itself encapsulated in
    Ethernet) each layer having its own vocabulary and grammar.

    To model this, a field is part of a tree which root is field’s symbol and made of leaf of layer fields.
    Hence, a field always has a parent which can be another field or a symbol if its the root. A field can optionally have children.

    The value that can take the field is defined by its definition domain.
    It can be a simple static value such an ASCII or a decimal but also more complex such as including transformation or encoding filters and relations.

    Here are few examples of 'simple' fields:

    a field containing the decimal value 100

    >>> from netzob.all import *
    >>> f = Field(100)

    a field containing a specific binary: '1000' = 8 in decimal

    >>> f = Field(0b1000)

    a field containing a raw value of 8 bits (1 byte)

    >>> f = Field(Raw(size=(8, 9)))

    a field representing a random IPv4

    >>> f = Field(IPv4())

    a field representing a random ASCII of 6 characters length

    >>> f = Field(ASCII(size=(6, 7)))

    a field representing a random ASCII with between 5 and 20 characters

    >>> payloadField = Field(ASCII(size=(5, 20)))



    Here are few examples of 'alternative' fields:

    a field representing two differents ASCII, "netzob" or "zoby"

    >>> f = Field(["netzob", "zoby"])

    a field representing a decimal (10) or an ASCII of 10 chars,

    >>> f = Field([10, ASCII(size=(10, 11))])


    a field which value is the size of the payloadField

    >>> f = Field([Raw(Size(payloadField))])

    """

    def __init__(self, domain=None, name=None, layer=False):
        """
        :keyword domain: the definition domain of the field (see domain property to get more information)
        :type domain: a :class:`list` of :class:`object`, default is Raw(None)
        :keyword name: the name of the field
        :type name: :class:`str`
        :keyword layer: a flag indicating if field is a layer
        :type layer: :class:`bool`

        """
        super(Field, self).__init__(name, None, layer)
        if domain is None:
            domain = Raw(None)
        self.domain = domain

    def generate(self, generationStrategy=None):
        """Generate an hexastring which content
        follows the fields definitions attached to current element.

        This method allows to generate some content following the field definition:

        >>> from netzob.all import *
        >>> f = Field("hello")
        >>> print f.generate()
        hello

        This method also applies on multiple fields using a Symbol

        >>> fHello = Field("hello ")
        >>> fName = Field("zoby")
        >>> s = Symbol([fHello, fName])
        >>> print s.generate()
        hello zoby

        :keyword generatorStrategy: if set, this generation strategy will be used to pilot this generation process
        :type generatorStrategy: :class:`object`

        :return: a generated content represented with an hexastring
        :rtype: :class:`str``
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.GenerationException` if an error occurs while generating a message
        """
        if self.__domain is None:
            raise InvalidDomainException("The domain is not defined.")

        # Create a Variable Writing Token
        writingToken = VariableWritingToken(generationStrategy=generationStrategy)
        self.domain.write(writingToken)
        wroteData = writingToken.value
        return wroteData.tobytes()

    @property
    def domain(self):
        """This defines the definition domain of a field.

        This definition domain is made of a list of typed values which can optionally have a static value.
        More information on the available types and their specificities are available on their documentations.

        :type: a :class:`list` of :class:`object` -- By object we refer to a primitive object (:class:`int`, :class:`str`, :class:`hex`, :class:`binary`) and netzob types objects inherited from :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :raises: :class:`netzob.Common.Models.Vocabulary.Field.InvalidDomainException` if domain invalid.
        """

        return self.__domain

    @domain.setter
    def domain(self, domain):
        normalizedDomain = DomainFactory.normalizeDomain(domain)
        self.regex = normalizedDomain.buildRegex()
        self.__domain = normalizedDomain

    @property
    def messages(self):
        """A list containing all the messages that the parents of this field have.
        In reality, a field doesn't have messages, it just returns the messages of its symbol

        :type : a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        """
        messages = []
        try:
            messages.extend(self.getSymbol().messages)
        except Exception, e:
            self._logger.warning("The field is attached to no symbol and so it has no messages: {0}".format(e))

        return messages
