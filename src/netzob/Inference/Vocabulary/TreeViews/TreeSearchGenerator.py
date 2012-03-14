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
import logging
import gtk
from netzob.Common.Field import Field

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.VisualizationFilters.TextColorFilter import TextColorFilter
import uuid


#+----------------------------------------------
#| TreeSearchGenerator:
#|     update and generates the treeview and its
#|     treestore dedicated to the search process
#+----------------------------------------------
class TreeSearchGenerator():

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Vocabulary.TreeViews.TreeSearchGenerator.py')
        self.tree = None
        self.searchTasks = []

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        
        self.tree = gtk.TreeView()
        colResult = gtk.TreeViewColumn()
        colResult.set_title("Search results")

        cell = gtk.CellRendererText()
        colResult.pack_start(cell, True)
        colResult.add_attribute(cell, "text", 0)

        self.treestore = gtk.TreeStore(str)
        
        

        self.tree.append_column(colResult)
        self.tree.set_model(self.treestore)
        self.tree.show()
        
        
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 250)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.tree)
        self.scroll.show()
        
     

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.taks = []
        self.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning("The treeview for the symbol is in error mode")
        pass

    #+----------------------------------------------
    #| show:
    #|   Display the panel
    #+----------------------------------------------
    def show(self):
        self.scroll.show_all()

    #+----------------------------------------------
    #| hide:
    #|   Hide the panel
    #+----------------------------------------------
    def hide(self):
        self.scroll.hide_all()

    #+----------------------------------------------
    #| default:
    #|         Update the treestore in normal mode
    #+----------------------------------------------
    def update(self, searchTasks=[]):
        
        if len(searchTasks) == 0 :
            self.decolorizeAnySearchResult()
            self.treestore.clear()
            return
        
        
        foundSymbols = dict()
        foundMessages = dict()
                
        for task in searchTasks:
            for result in task.getResults():
                # retrieve the symbol associated with the message
                symbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(result.getMessage())
                
                # Display the tree item for the symbol
                treeItemSymbol = None
                if str(symbol.getID()) in foundSymbols.keys() :
                    treeItemSymbol = foundSymbols[str(symbol.getID())]
                else :
                    treeItemSymbol = self.treestore.append(None, [symbol.getName()])
                    foundSymbols[str(symbol.getID())] = treeItemSymbol
                    
                # Display the tree item for the message
                treeItemMessage = None
                if str(result.getMessage().getID()) in foundMessages.keys() :
                    treeItemMessage = foundMessages[str(result.getMessage().getID())]
                else :
                    treeItemMessage = self.treestore.append(treeItemSymbol, [result.getMessage().getID()])
                    foundMessages[str(result.getMessage().getID())] = treeItemMessage
                
                # Add the result
                self.treestore.append(treeItemMessage, [str(result.getSegments())])
                
        self.colorizeResults(searchTasks)
    
       
        
    def colorizeResults(self, searchTasks):
        colorizedSymbols = []
        for task in searchTasks:
            for result in task.getResults():
                for (start, end) in result.getSegments() :
                    filter = TextColorFilter(uuid.uuid4(), "Search", start, start + end + 1, "#DD0000")
                    message = result.getMessage()
                    message.addVisualizationFilter(filter) 
                    # colorize the associated symbol
                    symbol = self.netzob.getCurrentProject().getVocabulary().getSymbolWhichContainsMessage(message)
                    if not symbol in colorizedSymbols :
                        symbol.addVisualizationFilter(TextColorFilter(uuid.uuid4(), "Search", None, None, "#DD0000")) 
                        colorizedSymbols.append(symbol)
        
    def decolorizeAnySearchResult(self):
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        for symbol in vocabulary.getSymbols() :
            filterToRemoveFromSymbol = []
            for filter in symbol.getVisualizationFilters() :
                if filter.getName() == "Search" :
                    filterToRemoveFromSymbol.append(filter)
                    
            for filter in filterToRemoveFromSymbol :
                symbol.removeVisualizationFilter(filter)
                
            filterToRemoveFromMessage = []
            for message in symbol.getMessages() :
                for filter in message.getVisualizationFilters() :
                    if filter.getName() == "Search" :
                        filterToRemoveFromMessage.append(filter)
                        
                for f in filterToRemoveFromMessage :
                    message.removeVisualizationFilter(f)
        
        
        
    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.tree

    def getScrollLib(self):
        return self.scroll

    #+----------------------------------------------
    #| SETTERS:
    #+----------------------------------------------
    def setTreeview(self, tree):
        self.tree = tree

    def setScrollLib(self, scroll):
        self.scroll = scroll
