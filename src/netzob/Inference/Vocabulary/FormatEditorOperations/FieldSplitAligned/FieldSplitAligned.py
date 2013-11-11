
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
#| Standard library imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.C_Extensions.WrapperArgsFactory import WrapperArgsFactory
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Inference.Vocabulary.Search.SearchEngine import SearchEngine
from netzob import _libNeedleman


@NetzobLogger
class FieldSplitAligned(object):
    """This class align the data attached to a specified field
    and build a field definition based on the result of the alignment.

    The alignement is based on Needleman & Wunsch sequence alignement.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = ["01ff00ff", "0222ff0000ff", "03ff000000ff", "0444ff00000000ff", "05ff0000000000ff", "06ff000000000000ff"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print symbol
    01ff00ff
    0222ff0000ff
    03ff000000ff
    0444ff00000000ff
    05ff0000000000ff
    06ff000000000000ff
    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol)
    >>> print symbol
    01   | ff00 |            | ff
    0222 | ff00 | 00         | ff
    03   | ff00 | 0000       | ff
    0444 | ff00 | 000000     | ff
    05   | ff00 | 00000000   | ff
    06   | ff00 | 0000000000 | ff

    >>> samples = ["hello toto, what's up in France ?", "hello netzob, what's up in UK ?", "hello sygus, what's up in Germany ?"]
    >>> messages = [RawMessage(data=sample) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> print symbol
    hello toto, what's up in France ?
    hello netzob, what's up in UK ?
    hello sygus, what's up in Germany ?

    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol, useSemantic = False)
    >>> print symbol
    hello  | toto   | , what's up in  | France  |  ?
    hello  | netzob | , what's up in  | UK      |  ?
    hello  | sygus  | , what's up in  | Germany |  ?

    Let's illustrate the use of semantic constrained sequence alignment with a simple example

    >>> samples = ["John-0108030405--john.doe@gmail.com", "Mathieu-0908070605-31 rue de Paris, 75000 Paris, France-mat@yahoo.fr", "Olivia-0348234556-7 allee des peupliers, 13000 Marseille, France-olivia.tortue@hotmail.fr"]
    >>> messages = [RawMessage(data=sample) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> print symbol
    John-0108030405--john.doe@gmail.com
    Mathieu-0908070605-31 rue de Paris, 75000 Paris, France-mat@yahoo.fr
    Olivia-0348234556-7 allee des peupliers, 13000 Marseille, France-olivia.tortue@hotmail.fr

    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol, useSemantic = False)
    >>> print symbol
    John    | -0 | 10 | 8 | 03040 | 5 | - | - | john.    | d | o | e | @gm                  | a |     | i | l.        | c |           | o | m
    Mathieu | -0 | 90 | 8 | 07060 | 5 |   | - | 31 rue   | d |   | e |  Paris, 75000 P      | a | r   | i | s, Fran   | c | e-mat@yah | o | o.fr
    Olivia  | -0 | 34 | 8 | 2345  | 5 | 6 | - | 7 allee  | d |   | e | s peupliers, 13000 M | a | rse | i | lle, Fran | c | e-        | o | livia.tortue@hotmail.fr

    >>> applicativeDatas = []
    >>> applicativeDatas.append(ApplicativeData("Firstname", ASCII("John")))
    >>> applicativeDatas.append(ApplicativeData("Firstname", ASCII("Mathieu")))
    >>> applicativeDatas.append(ApplicativeData("Firstname", ASCII("Olivia")))
    >>> applicativeDatas.append(ApplicativeData("PhoneNumber", ASCII("0108030405")))
    >>> applicativeDatas.append(ApplicativeData("PhoneNumber", ASCII("0348234556")))
    >>> applicativeDatas.append(ApplicativeData("PhoneNumber", ASCII("0908070605")))
    >>> applicativeDatas.append(ApplicativeData("StreetAddress", ASCII("31 rue de Paris")))
    >>> applicativeDatas.append(ApplicativeData("StreetAddress", ASCII("7 allee des peupliers")))
    >>> applicativeDatas.append(ApplicativeData("CityAddress", ASCII("Paris")))
    >>> applicativeDatas.append(ApplicativeData("CityAddress", ASCII("marseille")))
    >>> applicativeDatas.append(ApplicativeData("Email", ASCII("john.doe@gmail.com")))
    >>> applicativeDatas.append(ApplicativeData("Email", ASCII("mat@yahoo.fr")))
    >>> applicativeDatas.append(ApplicativeData("Email", ASCII("olivia.tortue@hotmail.fr")))
    >>> session = Session(messages, applicativeData=applicativeDatas)
    >>> symbol = Symbol(messages=messages)

    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol, useSemantic=True)
    >>> print symbol

    """

    def __init__(self, unitSize=AbstractType.UNITSIZE_8, doInternalSlick=False):
        """Constructor.

        """
        self.doInternalSlick = doInternalSlick
        self.unitSize = unitSize

    @typeCheck(AbstractField, bool)
    def execute(self, field, useSemantic=True):
        """Execute the alignement on the specified field.

        :parameter field: the field that will be aligned
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        """
        if field is None:
            raise TypeError("Field cannot be None")

        if useSemantic is None:
            raise TypeError("useSemantic cannot be None")

        # First step: we clean and reset the field
        from netzob.Inference.Vocabulary.FormatEditor import FormatEditor
        FormatEditor.resetFormat(field)

        # Retrieve all the segment of messages to align
        messageValues = field.getMessageValues(encoded=False, styled=False)

        # Semantic tags (a.k.a applicative data)
        semanticTags = None
        if useSemantic:
            semanticTags = [self.__searchApplicativeDataInMessage(message) for message, values in messageValues.iteritems()]

        if len(messageValues.values()) == 0:
            return

        # Execute the alignement
        (alignment, semanticTags, score) = self._alignData(messageValues.values(), semanticTags)

        # Check the results
        if alignment is None:
            raise ValueError("Impossible to compute an alignment for the specifed data")

        # Build Fields based on computed alignement and semantic tags
        self._updateFieldsFromAlignment(field, alignment, semanticTags)

        # if useSemantic:
        #     self._createSubFieldsFollowingSemanticTags(field, alignment, semanticTags)

    @typeCheck(AbstractField, str, dict)
    def _updateFieldsFromAlignment(self, field, alignment, semanticTags):
        """This methods creates a regex based on the computed alignment
        by the Needleman&Wunsch algorithm and the attached semantic tags.

        @param field : the field for which it creates the regex (and the sub fields)
        @param align : the string representing the common alignment between messages of the symbol.
        @param semanticTags : the list of tags attached to each half-bytes of the provided alignment."""

        if field is None:
            raise TypeError("Field cannot be None")
        if alignment is None:
            raise TypeError("Alignment cannot be None")
        if semanticTags is None:
            raise TypeError("SemanticTags cannot be None")


        self._logger.debug("Semantic Tags : {0}".format(semanticTags))
        self._logger.debug("Alignment: {0}".format(alignment))

        # Create fields following the alignment
        self._splitFieldFollowingAlignment(field, alignment)

    def _splitFieldFollowingAlignment(self, field, align):
        """Update the field definition with new fields following the
        specified align."""

        # STEP 1 : Create a field separation based on static and dynamic fields
        leftAlign, rightAlign = self._splitAlignment(align)
        splited = self._mergeAlign(leftAlign, rightAlign)
        step1Fields = []

        for (entryVal, entryDyn) in splited:
            if entryDyn:
                newField = Field(Raw(nbBytes=(0, len(entryVal) / 2)))
            else:
                newField = Field(Raw(TypeConverter.convert(entryVal, HexaString, Raw)))
            step1Fields.append(newField)

        field.children = step1Fields

    def _splitAlignment(self, align):
        """Splits the specified alignment which is composed of hexastring and of dynamic sections ("-")
        The idea is to separate in two (left and right) and then to merge the splitted left and the splitted right.

        >>> import random
        >>> fs = FieldSplitAligned()
        >>> data = "-----01987640988765--876--678987--67898-------6789789-87987978----"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['-----', True], ['01987640988765', False], ['--', True], ['876', False], ['--', True], ['678987', False], ['--', True], ['67898', False], ['-------', True], ['6789789', False], ['-', True], ['87987978', False], ['----', True]]
        >>> data = "-------------------------------"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['-------------------------------', True]]
        >>> data = "98754678998765467890875645"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['98754678998765467890875645', False]]
        >>> data = "---------------987-----6789765--568767---568776897689---567876------------------5678657865-9876579867789-9876879-9876787678657865467876546"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['---------------', True], ['987', False], ['-----', True], ['6789765', False], ['--', True], ['568767', False], ['---', True], ['568776897689', False], ['---', True], ['567876', False], ['------------------', True], ['5678657865', False], ['-', True], ['9876579867789', False], ['-', True], ['9876879', False], ['-', True], ['9876787678657865467876546', False]]
        >>> nbField = random.randint(50000, 200000)
        >>> tab = []
        >>> for i in range(nbField):
        ...     if i%2 == 0:
        ...         tab.append("-"*random.randint(1, 20))
        ...     else:
        ...         tab.append("".join([random.choice('0123456789abcdef') for x in range(random.randint(1, 20))]))
        >>> data = "".join(tab)
        >>> nbField == len(fs._mergeAlign(*fs._splitAlignment(data)))
        True

        """
        if len(align) == 1:
            return ([[align[0], align[0] == "-"]], [])
        elif len(align) == 2:
            return ([[align[0], align[0] == "-"]], [[align[1], align[1] == "-"]])

        indexHalf = len(align) / 2
        leftAlign = align[0:indexHalf]
        rightAlign = align[indexHalf:]

        leftLeftAlign, rightLeftAlign = self._splitAlignment(leftAlign)
        mergedLeftAlign = self._mergeAlign(leftLeftAlign, rightLeftAlign)

        leftRightAlign, rightRightAlign = self._splitAlignment(rightAlign)
        mergedRightAlign = self._mergeAlign(leftRightAlign, rightRightAlign)

        return (mergedLeftAlign, mergedRightAlign)

    def _mergeAlign(self, leftAlign, rightAlign):
        if len(leftAlign) == 0:
            return rightAlign
        if len(rightAlign) == 0:
            return leftAlign
        if leftAlign[-1][1] == rightAlign[0][1]:
            leftAlign[-1][0] = leftAlign[-1][0] + rightAlign[0][0]
            align = leftAlign + rightAlign[1:]
        else:
            align = leftAlign + rightAlign
        return align

    # def _temp(self, align):
    #     self._logger.debug("Align = {0}".format(align))
    #     for i, val in enumerate(align):

    #         if (val == "-"):
    #             if (found is False):
    #                 start = i
    #                 found = True
    #         else:
    #             if (found is True):
    #                 found = False
    #                 nbTiret = i - start
    #                 self._logger.debug("Add dyn raw : {0}".format(nbTiret / 2))
    #                 domains.append(Raw(nbBytes=(0, nbTiret / 2)))
    #                 self._logger.debug("Converting : {0}".format(val))
    #                 domains.append(Raw(TypeConverter.convert(val, HexaString, Raw)))
    #             else:
    #                 if len(domains) == 0:
    #                     domains.append(Raw(TypeConverter.convert(val, HexaString, Raw)))
    #                 else:
    #                     prevVal = TypeConverter.convert(domains[-1].value, BitArray, Raw)
    #                     domains[-1] += Raw(prevVal + TypeConverter.convert(val, HexaString, Raw))
    #     if (found is True):
    #         nbTiret = i - start + 1
    #         domains.append(Raw(nbBytes=(0, nbTiret)))

    #     # We have a computed the 'simple' regex,
    #     # and represent it using the field representation
    #     step1Fields = []
    #     for domainElt in domains:
    #         if domainElt is None:
    #             pass
    #         innerField = Field(domain=domainElt)
    #         step1Fields.append(innerField)
    #         field.children.append(innerField)

    @typeCheck(list, list)
    def _alignData(self, values, semanticTags=None):
        """Align the specified data with respect to the semantic tags
        identified over the data.

        :parameter values: values to align
        :type values: a list of hexastring.
        :keyword semanticTags: semantic tags to consider when aligning
        :type semanticTags: a dict of :class:`netzob.Common.Models.Vocabulary.SemanticTag.SemanticTag`
        :return: the alignment, its score and the semantic tags
        :rtype: a tupple (alignement, semanticTags, score)
        """
        if values is None or len(values) == 0:
            raise TypeError("At least one value must be provided.")

        for val in values:
            if val is None or not isinstance(val, str):
                raise TypeError("At least one value is None or not an str which is not authorized.")

        if semanticTags is None:
            semanticTags = [dict() for v in values]

        if len(semanticTags) != len(values):
            raise TypeError("There should be a list of semantic tags for each value")

        # Prepare the argument to send to the C wrapper
        toSend = [(''.join(values[iValue]), semanticTags[iValue]) for iValue in xrange(len(values))]

        wrapper = WrapperArgsFactory("_libNeedleman.alignMessages")
        wrapper.typeList[wrapper.function](toSend)

        debug = False
        (score1, score2, score3, regex, mask, semanticTags) = _libNeedleman.alignMessages(self.doInternalSlick, self._cb_executionStatus, debug, wrapper)
        scores = (score1, score2, score3)

        # Deserialize returned info
        alignment = self._deserializeAlignment(regex, mask, self.unitSize)
        semanticTags = self._deserializeSemanticTags(semanticTags, self.unitSize)

        return (alignment, semanticTags, scores)

    @typeCheck(AbstractMessage)
    def __searchApplicativeDataInMessage(self, message):
        """This internal method search any applicative data that could be identified
        in the specified message and returns results in a dict that shows the position
        of the applicative data identified.

        :parameter message: the message in which we search any applicative data
        :type message: :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :return: a dict that describes the position of identified applicative data
        :rtype: :class:`dict`
        """
        if message is None:
            raise TypeError("Message cannot be None")

        self._logger.debug("Search app data in {0}".format(message.data))

        results = dict()

        appValues = dict()
        if message.session is not None:
            for applicativeD in message.session.applicativeData:
                appValues[applicativeD.value] = applicativeD.name
        else:
            self._logger.info("Message is not attached to a session, so no applicative data will be considered while computing the alignment.")

        if len(appValues) > 0:
            searchResults = SearchEngine.searchInMessage(appValues.keys(), message, addTags=False)
            for searchResult in searchResults:
                for (startResultRange, endResultRange) in searchResult.ranges:
                    appDataName = appValues[searchResult.searchTask.properties["data"]]
                    for pos in range(startResultRange/4, endResultRange/4):
                        results[pos] = appDataName

        return results

    @typeCheck(AbstractField, str, dict)
    def _createSubFieldsFollowingSemanticTags(self, rootField, align, semanticTags):
        """Searches for subfields which should be created because of identified semantic boundaries.
        """
        if rootField is None:
            raise TypeError("RootField cannot be None")
        if align is None:
            raise TypeError("Align cannot be None")
        if semanticTags is None:
            raise TypeError("SemanticTags cannot be None")

        self._logger.debug("original semantic tags: ")
        self._logger.debug(semanticTags)

        originalFields = rootField._getLeafFields()

        if len(originalFields) == 1 and rootField == originalFields[0]:
            # We are dealing with a specific field
            self._logger.debug("Analyze sub fields for {0}".format(rootField.regex))

            if len(set(rootField.getValues())) == 1:
                self._createSubFieldsForAStaticField(rootField, align, semanticTags)
            else:
                self._createSubFieldsForADynamicField(rootField, align, semanticTags)

            for f in rootField.children:
                self._logger.debug("\t {0} : {1}".format(f.name, f.regex))
        else:
            # We are dealing with multiple fields, lets split them
            currentIndex = 0

            for field in originalFields:
                self._logger.debug("field regex = {0} (maxSize={1})".format(field.regex, field.domain.maxSize()))

                # Retrieve the size of the current field
                lengthField = ( field.domain.maxSize() / 4)

                # Find semantic tags related to the current section
                sectionSemanticTags = dict((k, semanticTags[k]) for k in xrange(currentIndex, currentIndex + lengthField))

                # reccursive call
                self._logger.debug("Working on field : {0}".format(field.name))
                self._createSubFieldsFollowingSemanticTags(field, align[currentIndex:currentIndex + lengthField], sectionSemanticTags)

                currentIndex += lengthField

    def createSubFieldsForAStaticField(self, field, align, semanticTags):
        """createSubFieldsForAStaticField:
        Analyzes the static field provided and create sub fields following
        the provided semantic tags."""
        logging.debug("Create subfields for static field {0} : {1}".format(field.getName(), align))

        if len(field.getLocalFields()) > 0:
            logging.warning("Impossible to create sub fields for this field since its not cleaned")
            return

        subFields = []

        currentTag = None
        currentTagLength = 0

        for index, tag in semanticTags.iteritems():
            if tag != currentTag:
                # Create a sub field
                subFieldValue = align[index - currentTagLength:index]
                if len(subFieldValue) > 0:
                    subFields.append(subFieldValue)
                currentTagLength = 0
            currentTag = tag
            currentTagLength += 1
        if currentTagLength > 0:
            subFieldValue = align[-currentTagLength:]
            if len(subFieldValue) > 0:
                subFields.append(subFieldValue)

        if len(subFields) > 1:
            for iSubField, subFieldValue in enumerate(subFields):
                subField = Field("{0}_{1}".format(field.getName(), iSubField), "({0})".format(subFieldValue), field.getSymbol())
                field.addLocalField(subField)

    def _createSubFieldsForADynamicField(self, field, align, semanticTags):
        """Analyzes the dynamic field provided and create sub fields following
        the provided semantic tags."""

        if field is None:
            raise TypeError("Field cannot be None")
        if align is None:
            raise TypeError("Align cannot be None")
        if semanticTags is None:
            raise TypeError("SemanticTags cannot be None")

        self._logger.debug("Create subfields for dynamic field {0} : {1}".format(field.name, field.regex))

        subFields = []

        currentTag = None
        currentTagLength = 0

        semanticTagsForEachMessage = field.getSemanticTagsByMessage()

        for index, tag in semanticTags.iteritems():
            if tag != currentTag:
                # Create a sub field
                if currentTagLength > 0:
                    values = self._getFieldValuesWithTag(field, semanticTagsForEachMessage, currentTag)
                    subFields.append((currentTag, values))
                currentTagLength = 0
            currentTag = tag
            currentTagLength += 1
        if currentTagLength > 0:
            values = self._getFieldValuesWithTag(field, semanticTagsForEachMessage, currentTag)
            subFields.append((currentTag, values))

        self._logger.debug("Identified subFields : {0}".format(subFields))

        for iSubField, (tag, values) in enumerate(subFields):
            if len(values) > 0:
                if tag == "None":
                    minValue = None
                    maxValue = None
                    for v in values:
                        if minValue is None or len(v) < minValue:
                            minValue = len(v)
                        if maxValue is None or len(v) > maxValue:
                            maxValue = len(v)
                    subField = Field("{0}_{1}".format(field.getName(), iSubField), "(.{" + str(minValue) + "," + str(maxValue) + "})", field.getSymbol())

                    field.addLocalField(subField)
                else:
                    # create regex based on unique values
                    newRegex = '|'.join(list(set(values)))
                    newRegex = "({0})".format(newRegex)
                    subField = Field("{0}_{1}".format(field.getName(), iSubField), newRegex, field.getSymbol())
                    field.addLocalField(subField)

    @typeCheck(AbstractField, dict, str)
    def _getFieldValuesWithTag(self, field, semanticTagsForEachMessage, tag):
        if field is None:
            raise TypeError("Field cannot be None")
        if semanticTagsForEachMessage is None:
            raise TypeError("SemanticTagsForEachMessage cannot be None")
        if tag is None:
            raise TypeError("Tag cannot be None")

        values = []

        # Retrieve value of each message in current field tagged with requested tag
        for message, tagsInMessage in semanticTagsForEachMessage.iteritems():
            initial = None
            end = None

            for tagIndex in sorted(tagsInMessage.keys()):
                tagName = tagsInMessage[tagIndex]
                if initial is None and tagName == tag:
                    initial = tagIndex
                elif initial is not None and tagName != tag:
                    end = tagIndex
                    break

            if initial is not None and end is None:
                end = sorted(tagsInMessage.keys())[-1] + 1
            if initial is not None and end is not None:
                values.append(message.getStringData()[initial:end])

                for i in range(initial, end):
                    del tagsInMessage[i]

        if "" not in values and len(semanticTagsForEachMessage.keys()) > len(values):
            values.append("")

        return values


    def _cb_executionStatus(self, stage, donePercent, currentMessage):
        """Callback function called by the C extension to provide
        info on the current status.
        """
        pass

    def _deserializeSemanticTags(self, tags, unitSize=AbstractType.UNITSIZE_8):
        """Deserialize the information returned from the C library
        and build the semantic tags definitions from it.
        """
        result = dict()
        arTags = tags.split(';')
        j = 0
        for iTag, tag in enumerate(arTags):
            if tag != "None":
                result[j]=tag[2:-2]
            else:
                result[j]=tag

            if unitSize == AbstractType.UNITSIZE_8:
                j = j + 1
                result[j] = result[j-1]
            else:
                raise ValueError("Unsupported unitsize.")

            j += 1

        return result

    def _deserializeAlignment(self, regex, mask, unitSize=AbstractType.UNITSIZE_8):
        """
        deserializeAlignment: Transforms the C extension results
        in a python readable way
        @param regex the C returned regex
        @param mask the C returned mask
        @param unitSize the unitSize
        @returns the python alignment
        """
        if not (unitSize == AbstractType.UNITSIZE_8 or unitSize == AbstractType.UNITSIZE_4):
            raise ValueError("Deserializing with unitSize {0} not yet implemented, only 4 and 8 supported.".format(unitSize))

        align = ""
        for i, c in enumerate(mask):
            if c != '\x02':
                if c == '\x01':
                    if unitSize == AbstractType.UNITSIZE_8:
                        align += "--"
                    elif unitSize == AbstractType.UNITSIZE_4:
                        align += "-"
                else:
                    if unitSize == AbstractType.UNITSIZE_8:
                        align += TypeConverter.convert(regex[i:i + 1], Raw, HexaString)
                    elif unitSize == AbstractType.UNITSIZE_4:
                        align += TypeConverter.convert(regex[i:i + 1], Raw, HexaString)[1:]
        return align

    @property
    def doInternalSlick(self):
        return self.__doInternalSlick

    @doInternalSlick.setter
    @typeCheck(bool)
    def doInternalSlick(self, doInternalSlick):
        if doInternalSlick is None:
            raise TypeError("doInternalSlick cannot be None")
        self.__doInternalSlick = doInternalSlick

    @property
    def unitSize(self):
        return self.__unitSize

    @unitSize.setter
    @typeCheck(str)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("Unitsize cannot be None")
        if unitSize not in AbstractType.supportedUnitSizes():
            raise TypeError("Specified unitsize is not supported, refers to AbstractType.supportedUnitSizes() for the list.")
        self.__unitSize = unitSize
