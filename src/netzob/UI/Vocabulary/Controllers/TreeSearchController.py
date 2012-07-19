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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
import logging
from gi.repository import Gtk, Gdk
import uuid

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.UI.Vocabulary.Views.TreeSearchView import TreeSearchView
from netzob.Common.Field import Field
from netzob.Common.Filters.Visualization.TextColorFilter import TextColorFilter
from netzob.Common.ProjectConfiguration import ProjectConfiguration


#+----------------------------------------------
#| TreeSearchController:
#|     update and generates the treeview and its
#|     treestore dedicated to the search process
#+----------------------------------------------
class TreeSearchController(object):

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self, netzob, vocabularyController):
        self.netzob = netzob
        self.vocabularyController = vocabularyController
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.UI.Vocabulary.Controllers.TreeSearchController.py')
        self.searchTasks = []
        self.view = TreeSearchView(self.netzob)
        self.initCallbacks()

    def initCallbacks(self):
        self.getTreeview().connect('button-press-event', self.buttonPressOnSearchResults_cb)

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self, searchTasks=[]):
        if self.netzob.getCurrentProject() != None:
            isActive = self.netzob.getCurrentProject().getConfiguration().getVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DISPLAY_SEARCH)
            if isActive:
                self.view.show()
                return
            else:
                self.view.hide()

        if len(searchTasks) == 0:
            self.decolorizeAnySearchResult()
            self.view.treestore.clear()
            return

        foundSymbols = dict()
        foundMessages = dict()

        for task in searchTasks:
            if len(task.getResults()) > 0:
                treeItemTask = self.view.treestore.append(None, [_("Task"), None, task.getDescription()])
            for result in task.getResults():
                # retrieve the symbol associated with the message
                symbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(result.getMessage())

                # Display the tree item for the symbol
                treeItemSymbol = None
                if str(symbol.getID()) in foundSymbols.keys():
                    treeItemSymbol = foundSymbols[str(symbol.getID())]
                else:
                    treeItemSymbol = self.view.treestore.append(treeItemTask, [_("Symbol"), symbol.getID(), symbol.getName()])
                    foundSymbols[str(symbol.getID())] = treeItemSymbol

                # Display the tree item for the message
                treeItemMessage = None
                if str(result.getMessage().getID()) in foundMessages.keys():
                    treeItemMessage = foundMessages[str(result.getMessage().getID())]
                else:
                    treeItemMessage = self.view.treestore.append(treeItemSymbol, [_("Message"), str(result.getMessage().getID()), str(result.getMessage().getID())])
                    foundMessages[str(result.getMessage().getID())] = treeItemMessage

                # Add the result
                self.view.treestore.append(treeItemMessage, [_("Segment"), str(result.getMessage().getID()), str(result.getSegments()) + " : " + str(result.getVariationDescription()) + " - " + str(result.getDescription())])

        self.colorizeResults(searchTasks)

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.taks = []
        self.view.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning(_("The treeview for the symbol is in error mode"))
        pass

    def colorizeResults(self, searchTasks):
        colorizedSymbols = []
        for task in searchTasks:
            for result in task.getResults():
                for (start, length) in result.getSegments():
                    filter = TextColorFilter(_("Search"), "green")
                    message = result.getMessage()
                    message.addVisualizationFilter(filter, start, start + length)
                    # colorize the associated symbol
#                    symbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(message)
#                    if not symbol in colorizedSymbols:
#                        symbol.addVisualizationFilter(TextColorFilter(uuid.uuid4(), "Search", None, None, "#DD0000"))
#                        colorizedSymbols.append(symbol)

    def decolorizeAnySearchResult(self):
        if self.netzob.getCurrentProject() == None:
            return

        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        for symbol in vocabulary.getSymbols():
            filterToRemoveFromSymbol = []
            for filter in symbol.getVisualizationFilters():
                if filter.getName() == self.view.treeName:
                    filterToRemoveFromSymbol.append(filter)

            for filter in filterToRemoveFromSymbol:
                symbol.removeVisualizationFilter(filter)

            filterToRemoveFromMessage = []
            for message in symbol.getMessages():
                for (filter, start, end) in message.getVisualizationFilters():
                    if filter.getName() == "Search":
                        filterToRemoveFromMessage.append(filter)

                for f in filterToRemoveFromMessage:
                    message.removeVisualizationFilter(f)

    #+----------------------------------------------
    #| button_press_on_search_results:
    #|   operation when the user click on the treeview of the search results.
    #+----------------------------------------------
    def buttonPressOnSearchResults_cb(self, treeview, event):
        if self.netzob.getCurrentProject() == None:
            return

        elementType = None
        elementValue = None

        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        # Retrieve informations on the clicked element
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No element selected
                pass
            else:
                # An element is selected
                aIter = treeview.get_model().get_iter(path)
                if aIter:
                    if treeview.get_model().iter_is_valid(aIter):
                        elementType = treeview.get_model().get_value(aIter, 0)
                        elementID = treeview.get_model().get_value(aIter, 1)
                        elementValue = treeview.get_model().get_value(aIter, 2)

        # Depending of its type, we select it
        if elementType != None and elementValue != None:
            if elementType == "Symbol":
                clickedSymbol = self.netzob.getCurrentProject().getVocabulary().getSymbolByID(elementID)
                self.selectedSymbol = clickedSymbol
                self.vocabularyController.treeSymbolController.update()
                self.vocabularyController.treeMessageController.update()
            elif elementType == "Message":
                clickedMessage = self.netzob.getCurrentProject().getVocabulary().getMessageByID(elementID)
                clickedSymbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(clickedMessage)
                self.selectedSymbol = clickedSymbol
                self.selectedMessage = clickedMessage
                self.vocabularyController.treeMessageController.update()

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.view.treeview

    def getScrollLib(self):
        return self.view.scroll

    def getWidget(self):
        return self.view.scroll

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.view.treeview = treeview

    def setScrollLib(self, scroll):
        self.view.scroll = scroll
