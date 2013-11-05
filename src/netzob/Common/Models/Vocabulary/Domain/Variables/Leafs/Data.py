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
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.NetzobRegex import NetzobRegex
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.AbstractVariableLeaf import AbstractVariableLeaf
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken import AbstractVariableProcessingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken import VariableWritingToken
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw


@NetzobLogger
class Data(AbstractVariableLeaf):
    """Represents a data, meaning a portion of content in the final
    message. This representation is achieved using a definition domain.
    So the Data stores at least two things: 1) the definition domain and constraints over it and 2) its current value

    For instance:

    >>> from netzob.all import *
    >>> f = Field()
    >>> f.domain = Data(dataType=ASCII(), originalValue=TypeConverter.convert("zoby", ASCII, BitArray), name="pseudo")
    >>> print f.domain.varType
    Data
    >>> print TypeConverter.convert(f.domain.currentValue, BitArray, Raw)
    zoby
    >>> print f.domain.dataType
    ASCII=None ((0, None))
    >>> print f.domain.name
    pseudo

    >>> f = Field(ASCII("hello zoby"))
    >>> print f.domain.varType
    Data
    >>> print TypeConverter.convert(f.domain.currentValue, BitArray, ASCII)
    hello zoby
    """

    def __init__(self, dataType, originalValue=None, name=None, learnable=False, mutable=False):
        """The constructor of a data variable

        :param dataType: the definition domain of the data.
        :type dataType: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :keyword originalValue: the value of the data (can be None)
        :type originalValue: :class:`object`
        :keyword name: the name of the data, if None name will be generated
        :type name: :class:`str`
        :keyword learnable: a flag stating if the current value of the data can be overwritten following with parsed data
        :type learnable: :class:`bool`
        :keyword mutable: a flag stating if the current value can changes with the parsing process
        :type mutable: :class:`bool`

        :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.
        """

        super(Data, self).__init__(self.__class__.__name__, name=name)

        self.dataType = dataType
        self.currentValue = originalValue

        self.learnable = learnable
        self.mutable = mutable

    @typeCheck(AbstractVariableProcessingToken)
    def isDefined(self, processingToken):
        """If the leaf has no values, it is not defined and returns False

        >>> from netzob.all import *
        >>> data = Data(ASCII(), learnable=True, mutable=True)
        >>> print data.currentValue
        None
        >>> rToken = VariableReadingToken(value=TypeConverter.convert("hello", ASCII, BitArray))
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.isDefined(rToken)
        False
        >>> data.read(rToken)
        >>> data.isDefined(rToken)
        True
        >>> print data.currentValue
        bitarray('0001011010100110001101100011011011110110')

        :rtype: bool
        :return: True if the data has a current value or has memorized its value in the processing token
        :raises: TypeError if parameter is not Valid
        """
        if processingToken is None:
            raise TypeError("ProcessingToken cannot be None")
        result = self.getValue(processingToken) is not None
        return result

    @typeCheck(AbstractVariableProcessingToken)
    def getValue(self, processingToken):
        """Return the current or memorized value.

        >>> from netzob.all import *
        >>> data = Data(ASCII(), originalValue=TypeConverter.convert("helloworld", ASCII, BitArray))
        >>> rToken = VariableReadingToken()
        >>> print data.getValue(rToken)
        bitarray('00010110101001100011011000110110111101101110111011110110010011100011011000100110')

        :param processingToken: the token in which the memory is located
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken`
        """
        if processingToken is None:
            raise TypeError("ProcessingToken cannot be None")

        if self.currentValue is not None:
            return self.currentValue
        else:
            return processingToken.memory.recall(self)

    @typeCheck(AbstractVariableProcessingToken)
    def getDictOfValues(self, processingToken):
        """ Simply return a dict that contains the value associated to the ID of the variable.
        """
        if processingToken is None:
            raise TypeError("Processing token cannot be none")
        dictOfValues = dict()
        dictOfValues[self.id] = self.getValue(processingToken)
        return dictOfValues

    #+---------------------------------------------------------------------------+
    #| Functions inherited from AbstractLeafVariable                             |
    #+---------------------------------------------------------------------------+
    @typeCheck(AbstractVariableProcessingToken)
    def forget(self, processingToken):
        """The variable forgets its value both locally and from the memory attached to the processingToken

        >>> from netzob.all import *
        >>> d = Data(Decimal(), originalValue=TypeConverter.convert(10, Decimal, BitArray))
        >>> rToken = VariableReadingToken()
        >>> d.memorize(rToken)
        >>> d.currentValue = TypeConverter.convert(30, Decimal, BitArray)
        >>> d.currentValue
        bitarray('01111000')
        >>> d.recall(rToken)
        >>> d.currentValue
        bitarray('01010000')
        >>> d.forget(rToken)
        >>> print d.currentValue
        None

        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self._logger.debug("- {0}: value is forgotten.".format(self))
        # We remove the memorized value.
        processingToken.memory.forget(self)
        # We remove the local value
        self.currentValue = None

    @typeCheck(AbstractVariableProcessingToken)
    def recall(self, processingToken):
        """The variable recall its memorized value.

        >>> from netzob.all import *
        >>> d = Data(ASCII(), originalValue = TypeConverter.convert("zoby", ASCII, BitArray))
        >>> rToken = VariableReadingToken()
        >>> d.memorize(rToken)
        >>> d.currentValue = TypeConverter.convert("netzob", ASCII, BitArray)
        >>> print TypeConverter.convert(d.currentValue, BitArray, ASCII)
        netzob
        >>> d.recall(rToken)
        >>> print TypeConverter.convert(d.currentValue, BitArray, ASCII)
        zoby

        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self._logger.debug("- {0}: value is recalled.".format(self))

        self.currentValue = processingToken.memory.recall(self)

    @typeCheck(AbstractVariableProcessingToken)
    def memorize(self, processingToken):
        """The variable memorizes its value.


        :param processingToken: the processing token where the memory is
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise: a TypeError if parameter is not valid
        """
        if processingToken is None:
            raise TypeError("processingToken cannot be None")

        self._logger.debug("- {0}: value is memorized.".format(self))
        processingToken.memory.memorize(self)

    @typeCheck(VariableReadingToken)
    def compareFormat(self, readingToken):
        """The variable checks if its format complies with the read value's format.

        For instance, we can use it to verify the content of the variable reading token
        can be parsed with an ASCII data

        >>> from netzob.all import *
        >>> data = Data(ASCII())
        >>> rToken = VariableReadingToken(value=TypeConverter.convert("helloworld", ASCII, BitArray))
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.compareFormat(rToken)
        >>> print rToken.Ok
        True

        In the following we check if the specified data can be parsed as a Decimal (which is always the case)

        >>> data = Data(Decimal())
        >>> rToken = VariableReadingToken(value=TypeConverter.convert("This is a Field", ASCII, BitArray))
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.compareFormat(rToken)
        >>> print rToken.Ok
        True

        It also checks the requested min and max size compliance of the reading token. Below the result
        is negivative because the ASCII section in the binValue is only of 4 chars which is below
        than the 5 mandatory requested chars (5 chars * 8 bits per char) in the Data.

        >>> data = Data(ASCII(nbChars=(5,10)))
        >>> binValue = TypeConverter.convert("hey ", ASCII, BitArray)
        >>> rToken = VariableReadingToken(value=binValue)
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.compareFormat(rToken)
        >>> print rToken.Ok
        False
        >>> rToken.value = TypeConverter.convert("hello", ASCII, BitArray)
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.compareFormat(rToken)
        >>> print rToken.Ok
        True

        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: compareFormat".format(self))

        # Retrieve the value to check
        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("Cannot compareFormat because not value is linked with the current data")

        data = readingToken.getValueForVariable(self)
        minSize, maxSize = self.dataType.size
        self._logger.debug("Compare size: request={0}, data size={1}, data={2}".format(self.dataType.size, len(data), data))
        parsedLength = None
        if minSize is not None and len(data) < minSize:
            # data is too small
            result = False
        else:
            if minSize is None:
                minSize = 0
            if maxSize is None:
                maxSize = len(data)
            result = False
            for length in xrange(min(maxSize, len(data)) + 1, minSize, -1):
                tmp = TypeConverter.convert(data[:length], BitArray, Raw)
                if self.dataType.canParse(tmp):
                    parsedLength = length
                    result = True
                    break

        readingToken.Ok = result
        if readingToken.Ok:
            readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + parsedLength)
            readingToken.incrementIndex(parsedLength)

        self._logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableReadingToken)
    def learn(self, readingToken):
        """This method is used to learn the value of a field
        given the content of in the current readingToken.

        >>> from netzob.all import *
        >>> data = Data(ASCII(nbChars=(0, 6)))
        >>> print data.currentValue
        None
        >>> binValue = TypeConverter.convert("netzob, is the name of a RE tool.", ASCII, BitArray)
        >>> rToken = VariableReadingToken(value=binValue)
        >>> rToken.setValueForVariable(data, rToken.value)
        >>> data.learn(rToken)
        >>> print TypeConverter.convert(data.currentValue, BitArray, ASCII)
        netzob

        .. warning:: WIP, the delimitor case is not yet managed.

        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: learn.".format(self))
        # A format comparison had been executed before, its result must be "OK".
        if readingToken.Ok:
            # Retrieve the value to check
            if not readingToken.isValueForVariableAvailable(self):
                raise Exception("Cannot learn because not value is linked with the current data")

            tmp = readingToken.getValueForVariable(self)

            self._logger.debug("Learning : {0}".format(tmp))
            minSize, maxSize = self.dataType.size

            # If the type has a definite size.
            if maxSize is not None:
                # Length comparison. (len(tmp) >= minBits is implicit as the readingToken is OK.)
                if len(tmp) <= maxSize:
                    self.currentValue = tmp
                    readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + len(tmp))
                    readingToken.incrementIndex(len(tmp))

                else:  # len(tmp) > self.maxBits
                    # We learn as much as we can.
                    self.currentValue = tmp[:maxSize]
                    readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + maxSize)
                    readingToken.incrementIndex(maxSize)

            else:
                self.currentValue = tmp
                readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + len(tmp))
                readingToken.incrementIndex(len(tmp))

            # TODO
            # If the type is delimited from 0 to a delimiter.
            # else:
            #     endi = 0
            #     for i in range(len(tmp)):
            #         self._logger.debug("ends here : {0}".format(tmp[i:]))
            #         if self.type.endsHere(tmp[i:]):
            #             endi = i
            #             break
            #     # We learn from the beginning to the delimiter.
            #     self.currentValue = tmp[:endi + len(self.type.getDelimiter())]  # The delimiter token is a part of the variable.
            #     readingToken.incrementIndex(endi + len(self.type.getDelimiter()))

            self._logger.debug("Learning done.")
        else:
            self._logger.debug("Learning abort because the previous format comparison failed.")

        self._logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableReadingToken)
    def compare(self, readingToken):
        """The variable compares its value to the read value.

        >>> from netzob.all import *
        >>> d = Data(ASCII(), TypeConverter.convert("Zoby", ASCII, BitArray))
        >>> bin = TypeConverter.convert("Zoby has a hat", ASCII, BitArray)
        >>> rToken = VariableReadingToken(value=bin)
        >>> rToken.setValueForVariable(d, rToken.value)
        >>> d.compare(rToken)
        >>> print rToken.Ok
        True

        >>> d = Data(ASCII(), TypeConverter.convert("Zoby", ASCII, BitArray))
        >>> bin = TypeConverter.convert("Visit netzob.org for more documentation", ASCII, BitArray)
        >>> rToken = VariableReadingToken(value=bin)
        >>> rToken.setValueForVariable(d,rToken.value)
        >>> d.compare(rToken)
        >>> print rToken.Ok
        False

        :param readingToken: the processing token where the memory is
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :raise: a TypeError if parameter is not valid
        """
        if readingToken is None:
            raise TypeError("readingToken cannot be None")

        self._logger.debug("- [ {0}: compare.".format(self))
        localValue = self.getValue(readingToken)

        if not readingToken.isValueForVariableAvailable(self):
            raise Exception("Cannot compare because the reading token has no value associated with current variable.")

        tmp = readingToken.getValueForVariable(self)
        #tmp = readingToken.value#[readingToken.index:]

        self._logger.debug("Compare {0} against {1}".format(localValue, tmp))

        if len(tmp) >= len(localValue):
            if tmp[:len(localValue)] == localValue:
                self._logger.debug("Comparison successful.")
                readingToken.setValueForVariable(self, tmp[:len(localValue)])
                #readingToken.attachVariableToRange(self, readingToken.index, readingToken.index + len(localValue))
                #readingToken.incrementIndex(len(localValue))
                readingToken.Ok = True
            else:
                readingToken.removeValueForVariable(self)
                readingToken.Ok = False
                self._logger.debug("Comparison failed: wrong value.")
        else:
            readingToken.removeValueForVariable(self)
            readingToken.Ok = False
            self._logger.debug("Comparison failed: wrong size.")
        self._logger.debug("Variable {0}: {1}. ] -".format(self.name, readingToken))

    @typeCheck(VariableWritingToken)
    def mutate(self, writingToken):
        """The current value is mutated according to the given generation strategy.

        >>> from netzob.all import *
        >>> d = Data(Decimal(), TypeConverter.convert(10, Decimal, BitArray))
        >>> print TypeConverter.convert(d.currentValue, BitArray, Decimal)
        10
        >>> # Create a writing token with the default generation strategy
        >>> wToken = VariableWritingToken()
        >>> # Start the mutation
        >>> d.mutate(wToken)
        >>> # Display the mutated value
        >>> print len(d.currentValue)
        8

        :param writingToken: the processing token where the memory is
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken.VariableWritingToken`
        :raise: a TypeError if parameter is not valid
        """
        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self._logger.debug("- {0}: mutate.".format(self))

        mutations = self.dataType.mutate(writingToken.generationStrategy)
        if mutations is None or len(mutations.keys()) == 0:
            raise ValueError("No mutations computed, an error occured.")
        randomKey = random.choice(mutations.keys())
        self._logger.debug("Randomly selected mutation {0} among all the possibilities: {1}.".format(randomKey, mutations))
        self.currentValue = mutations[randomKey]

    @typeCheck(VariableWritingToken)
    def generate(self, writingToken):
        """A new current value is generated according to the variable type and the given generation strategy.

        >>> from netzob.all import *
        >>> minChar = 5
        >>> maxChar = 10
        >>> d = Data(ASCII(nbChars=(minChar,maxChar)))
        >>> # Create a writing token with the default generation strategy
        >>> wToken = VariableWritingToken()
        >>> # Start the mutation
        >>> d.generate(wToken)
        >>> # Display the generated value
        >>> print minChar * 8 <= len(d.currentValue) <= maxChar * 8
        True

        :param writingToken: the processing token where the memory is
        :type writingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableWritingToken.VariableWritingToken`
        :raise: a TypeError if parameter is not valid
        """
        if writingToken is None:
            raise TypeError("writingToken cannot be None")

        self._logger.debug("- {0}: generate.".format(self))

        self.currentValue = self.dataType.generate(writingToken.generationStrategy)

    def writeValue(self, writingToken):
        """Write the variable value if it has one, else it returns the memorized value.
        Write this value in the writingToken.

        >>> from netzob.all import *
        >>> d1 = Data(ASCII(), TypeConverter.convert("Hello", ASCII, BitArray))
        >>> wToken = VariableWritingToken()
        >>> d1.writeValue(wToken)
        >>> print TypeConverter.convert(wToken.getValueForVariable(d1), BitArray, ASCII)
        Hello

        """
        self._logger.debug("- [ {0}: writeValue.".format(self))

        # Retrieve the value of the data
        value = self.getValue(writingToken)
        tValue = TypeConverter.convert(value, BitArray, Raw)

        writingToken.setValueForVariable(self, value)

        self._logger.debug("Variable {0}: {1} ({2}). ] -".format(self.name, writingToken.value, tValue))

    @typeCheck(AbstractVariableProcessingToken)
    def restore(self, processingToken):
        """restore

        :param processingToken: the processingtoken from which it will restore the value
        :type processingToken: :class:`netzob.Common.Models.Vocabulary.Domain.VariableProcessingTokens.AbstractVariableProcessingToken.AbstractVariableProcessingToken`
        :raise Exception: if parameter is not valid
        """
        if processingToken is None:
            raise Exception("ProcessingToken cannot be None")

        self._logger.debug("- {0}: memorized value is restored.".format(self))
        processingToken.memory.restore(self)

    def buildRegex(self):
        """This method creates a regex based on the children of the Data.
        The regex is encoded in HexaString

        For instance, if the value is static :

        >>> from netzob.all import *
        >>> d1 = Data(ASCII(), TypeConverter.convert("hello", ASCII, BitArray))

        >>> d2 = Data(Decimal(), TypeConverter.convert(20, Decimal, BitArray))

        >>> d3 = Data(ASCII(nbChars=(2, 10)))

        >>> d4 = Data(ASCII())

        :return: a regex which can be used to identify the section in which the domain can be found
        :rtype: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
        """

        if self.currentValue is not None:
            return NetzobRegex.buildRegexForStaticValue(self.currentValue)
        else:
            return NetzobRegex.buildRegexForSizedValue(self.dataType.size)

    def __str__(self):
        return "{0}={1} (size={2}/{3}, learnable={4}, mutable={5})".format(self.dataType, self.currentValue, self.dataType.size[0], self.dataType.size[1], self.learnable, self.mutable)

    #+---------------------------------------------------------------------------+
    #| Properties                                                                |
    #+---------------------------------------------------------------------------+
    @property
    def dataType(self):
        """The type of the data.

        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        :raises: :class:`TypeError` or :class:`ValueError` if not valid.
        """
        return self.__dataType

    @dataType.setter
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise ValueError("dataType cannot be None")
        self.__dataType = dataType

    @property
    def currentValue(self):
        """The current value of the data.

        :type: :class:`bitarray`
        """
        if self.__currentValue is not None:
            return self.__currentValue.copy()
        else:
            return None

    @currentValue.setter
    @typeCheck(bitarray)
    def currentValue(self, currentValue):
        if currentValue is not None:
            cv = currentValue.copy()
        else:
            cv = currentValue
        self.__currentValue = cv
