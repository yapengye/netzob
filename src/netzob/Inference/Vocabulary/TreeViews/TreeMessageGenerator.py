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
import pango
import gobject
import gtk

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Field import Field
from netzob.Common.NetzobException import NetzobException
import uuid
import time


#+----------------------------------------------
#| TreeMessageGenerator:
#|     update and generates the treeview and its
#|     treestore dedicated to the messages
#+----------------------------------------------
class TreeMessageGenerator():

    #+----------------------------------------------
    #| Constructor:
    #| @param vbox : where the treeview will be hold
    #+----------------------------------------------
    def __init__(self):
        self.symbol = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TreeStores.TreeMessageGenerator.py')
        self.currentColumns = []

    #+----------------------------------------------
    #| initialization:
    #| builds and configures the treeview
    #+----------------------------------------------
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(str, str, str)
        # creation of the treeview
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        
        # maximum number of columns = 200
        for i_col in range(4, 204) :
            # Define cellRenderer object
            textCellRenderer = gtk.CellRendererText()
            textCellRenderer.set_property("size-points", 8)
            textCellRenderer.set_property('background-set', True)

            # Column Messages
            lvcolumn = gtk.TreeViewColumn(str("#" + str(i_col - 4)))
            lvcolumn.set_resizable(True)
            lvcolumn.set_sort_column_id(i_col)
            lvcolumn.set_clickable(True)
            lvcolumn.pack_start(textCellRenderer, True)
            lvcolumn.set_attributes(textCellRenderer, markup=i_col, background=1, weight=2, editable=3)
            
#            self.treeview.append_column(lvcolumn)
            self.currentColumns.append(lvcolumn)
        

        self.treeview.show()
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_size_request(-1, 200)
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+----------------------------------------------
    #| clear:
    #|         Clear the class
    #+----------------------------------------------
    def clear(self):
        self.symbol = None
        self.treestore.clear()

    #+----------------------------------------------
    #| error:
    #|         Update the treestore in error mode
    #+----------------------------------------------
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")
        self.treestore.clear()

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
    def default(self, symbol):
        self.treestore.clear()            
        
        if symbol == None:
            return

        self.symbol = symbol
        self.log.debug("Updating the treestore of the messages in default mode with the messages from the symbol " + self.symbol.getName())

        # Verifies we have everything needed for the creation of the treeview
        if (self.symbol == None):
            self.log.warn("Error while trying to update the list of messages")
            return

        if (len(self.symbol.getMessages()) < 1 or len(self.symbol.getFields()) == 0):
            self.log.debug("It's an empty symbol so nothing to display")
            return
#        
#        # Remove all the columns of the current treeview
#        for col in self.currentColumns:
#            self.treeview.remove_column(col)
#            
#       
#        
#        iField = 4
#        for field in self.symbol.getFields():
#            # Define cellRenderer object
#            textCellRenderer = gtk.CellRendererText()
#            textCellRenderer.set_property("size-points", 8)
#            textCellRenderer.set_property('background-set', True)
#
#            # Column Messages
#            lvcolumn = gtk.TreeViewColumn(str(uuid.uuid4()))
#            lvcolumn.set_resizable(True)
#            lvcolumn.set_sort_column_id(iField)
#            lvcolumn.set_clickable(True)
#            lvcolumn.pack_start(textCellRenderer, True)
#            lvcolumn.set_attributes(textCellRenderer, markup=iField, background=1, weight=2, editable=3)
#            
#            self.treeview.append_column(lvcolumn)
#            self.currentColumns.append(lvcolumn)
#            iField = iField + 1
        
        

        # Create a TreeStore with N cols, with N := len(self.symbol.getFields())
        # str : Name of the row
        # str : Color of the row
        # int : pango type (weight bold)
        # bool : is row editable
        # [str...str] : value of cols
        
        treeStoreTypes = [str, str, int, gobject.TYPE_BOOLEAN]
        for field in self.symbol.getFields():
            treeStoreTypes.append(str)
        self.log.debug("Treestore will be composed of followings : " + str(treeStoreTypes))
        self.treestore = gtk.TreeStore(*treeStoreTypes)

        # Build the regex row
        regex_row = []
        regex_row.append("HEADER REGEX")
        regex_row.append("#c8c8c8")
        regex_row.append(pango.WEIGHT_BOLD)
        regex_row.append(True)
        for field in self.symbol.getFields():
            regex_row.append(field.getEncodedVersionOfTheRegex())
        self.log.debug("Regex row : " + str(regex_row))
        
        self.treestore.append(None, regex_row)
        
        # Build the types row
        types_line = []
        types_line.append("HEADER TYPE")
        types_line.append("#dedede")
        types_line.append(pango.WEIGHT_BOLD)
        types_line.append(True)
        for field in self.symbol.getFields():
            types_line.append(field.getFormat())
        self.log.debug("Type row : " + str(types_line))
        self.treestore.append(None, types_line)

        # Build the next rows from messages after applying the regex
        for message in self.symbol.getMessages():
            # For each message we create a line and computes its cols
            try:
                messageTable = message.applyAlignment(styled=True, encoded=True)
                self.log.debug("Computed alignment of message : " + str(messageTable))
            except NetzobException:
                self.log.warn("Impossible to display one of messages since it cannot be cut according to the computed regex.")
                self.log.warn("Message : " + str(message.getStringData()))
                
                continue  # We don't display the message in error
            line = []
            line.append(message.getID())
            line.append("#ffffff")
            line.append(pango.WEIGHT_NORMAL)
            line.append(False)
            line.extend(messageTable)
            self.treestore.append(None, line)
            self.log.debug("Content row : " + str(line))

        
        # activate or deactiave the perfect number of columns = nb Field
        for i in range(0, min(200, len(self.symbol.getFields()))) :
            self.treeview.append_column(self.currentColumns[i])
        for j in range(len(self.symbol.getFields()), 200) :
            self.treeview.remove_column(self.currentColumns[j])

        self.treeview.set_model(self.treestore)

    def updateDefault(self):
        self.default(self.symbol)
        

    #+----------------------------------------------
    #| GETTERS:
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview

    def getScrollLib(self):
        return self.scroll

    def getSymbol(self):
        return self.symbol
