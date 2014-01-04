#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
import unittest
import doctest

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.all import *
from netzob.Common.Utils import NetzobRegex
from netzob.Common.Utils.DataAlignment import ParallelDataAlignment
from netzob.Common.Utils.DataAlignment import DataAlignment
from netzob.Common.Models.Vocabulary import AbstractField
from netzob.Common.Models.Vocabulary.Domain.Variables import AbstractVariable
from netzob.Common.Models.Vocabulary.Messages import AbstractMessage

from netzob.Inference.Vocabulary.FormatOperations import FieldReseter
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitStatic import FieldSplitStatic
from netzob.Inference.Vocabulary.FormatOperations import ClusterByKeyField
from netzob.Inference.Vocabulary.FormatOperations import ClusterByApplicativeData
from netzob.Inference.Vocabulary.FormatOperations import ClusterByAlignment
from netzob.Inference.Vocabulary.FormatOperations import ClusterBySize
from netzob.Inference.Vocabulary.FormatOperations import FindKeyFields
from netzob.Common.Utils import SortedTypedList

from netzob.Inference.Vocabulary.Search import SearchTask
from netzob.Inference.Vocabulary.Search import SearchResult
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitAligned import FieldSplitAligned
from netzob.Inference.Vocabulary.FormatOperations import FieldSplitDelimiter

from netzob.Inference.Vocabulary.FormatOperations import FieldOperations


def getSuite():
    # List of modules to include in the list of tests
    modules = [
        Protocol.__module__,
        Field.__module__,
        DataAlignment,
        AbstractField,
        Symbol.__module__,
        DomainFactory.__module__,
        Alt.__module__,
        Agg.__module__,
        Data.__module__,
        ASCII.__module__,
        Decimal.__module__,
        BitArray.__module__,
        Raw.__module__,
        HexaString.__module__,
        AbstractType.__module__,
        Memory.__module__,
        TypeConverter.__module__,
        AbstractVariable,
        VariableReadingToken.__module__,
        # # JSONSerializator.__module__,
        # # TCPServer.__module__,
        Actor.__module__,
        TCPServer.__module__,
        TCPClient.__module__,
        UDPServer.__module__,
        UDPClient.__module__,
        # # Angluin.__module__,
        State.__module__,
        Transition.__module__,
        AbstractionLayer.__module__,
        NetzobRegex,
        ParallelDataAlignment,

        Format.__module__,
        FieldSplitStatic,
        FieldSplitAligned,
        FieldSplitDelimiter,
        FindKeyFields,
        FieldReseter,
        AbstractMessage,
        ClusterByKeyField,
        Session.__module__,
        SortedTypedList,
        ApplicativeData.__module__,
        DomainEncodingFunction.__module__,
        TypeEncodingFunction.__module__,
        SearchEngine.__module__,
        SearchTask,
        SearchResult,
        IPv4.__module__,
        ClusterByApplicativeData,
        ClusterByAlignment,
        ClusterBySize,
        
        # Size.__module__,
        RawMessage.__module__,
        L2NetworkMessage.__module__,
        L3NetworkMessage.__module__,
        L4NetworkMessage.__module__,

        FieldOperations,
        CorrelationFinder.__module__,
        RelationFinder.__module__,
        Automata.__module__,
    ]

    suite = unittest.TestSuite()
    for mod in modules:
        suite.addTest(doctest.DocTestSuite(mod))
    return suite
