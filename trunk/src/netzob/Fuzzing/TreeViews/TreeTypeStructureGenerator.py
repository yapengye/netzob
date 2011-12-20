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

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

#+---------------------------------------------- 
#| TreeTypeStructureGenerator :
#|     update and generates the treeview and its 
#|     treestore dedicated to the type structure
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TreeTypeStructureGenerator():
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param vbox : where the treeview will be hold
    #+---------------------------------------------- 
    def __init__(self):
        self.group = None
        self.message = None
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.TreeViews.TreeTypeStructureGenerator.py')
   
    #+---------------------------------------------- 
    #| initialization :
    #| builds and configures the treeview
    #+----------------------------------------------     
    def initialization(self):
        # creation of the treestore
        self.treestore = gtk.TreeStore(int, str, str, str) # iCol, Name, Data, Description
        # creation of the treeview   
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.set_reorderable(True)
        # Creation of a cell rendered and of a column
        cell = gtk.CellRendererText()
        columns = ["iCol", "Name", "Value", "Description"]
        for i in range(1, len(columns)):
            column = gtk.TreeViewColumn(columns[i])
            column.pack_start(cell, True)
            column.set_attributes(cell, markup=i)
            self.treeview.append_column(column)
        self.treeview.show()
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scroll.add(self.treeview)
        self.scroll.show()

    #+---------------------------------------------- 
    #| clear :
    #|         Clear the class
    #+---------------------------------------------- 
    def clear(self):
        self.group = None
        self.message = None
        self.treestore.clear()
        
    #+---------------------------------------------- 
    #| error :
    #|         Update the treestore in error mode
    #+---------------------------------------------- 
    def error(self):
        self.log.warning("The treeview for the messages is in error mode")      
        pass
    
    #+---------------------------------------------- 
    #| update :
    #|   Update the treestore
    #+---------------------------------------------- 
    def update(self):
        if self.getGroup() == None or self.getMessage() == None:
            self.clear()
            return

        splittedMessage = self.getMessage().applyRegex(styled=True, encoded=True)

        if str(self.message.getID).find("HEADER") != -1:
            self.clear()
            return

        self.treestore.clear()
        iCol = 0
        for col in self.getGroup().getColumns():
            tab = ""
            for k in range(int(col['tabulation'])):
                tab += " "
            messageElt = splittedMessage[iCol]
            if not self.getGroup().isRegexStatic(col['regex']):
                iter = self.treestore.append(None, [iCol, tab + col['name'] + ":", col['regex'] , col['description']])
            else:
                iter = self.treestore.append(None, [iCol, tab + col['name'] + ":", messageElt, col['description']])
            iCol += 1

    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getTreeview(self):
        return self.treeview
    def getScrollLib(self):
        return self.scroll
    def getGroup(self):
        return self.group
    def getMessage(self):
        return self.message

    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setTreeview(self, treeview):
        self.treeview = treeview
    def setScrollLib(self, scroll):
        self.scroll = scroll
    def setGroup(self, group):
        self.group = group
    def setMessage(self, message):
        self.message = message
    def setMessageByID(self, message_id):
        self.message = self.group.getMessageByID(message_id)

