# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pango
import pygtk
from netzob.Common.TypeConvertor import TypeConvertor
from netzob.Common.Symbol import Symbol
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.Models.RawMessage import RawMessage
pygtk.require('2.0')
import logging
import threading
import copy
import os
import time
import random
import uuid
#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common import StateParser

from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Inference.Vocabulary.SearchView import SearchView
from netzob.Inference.Vocabulary.Entropy import Entropy
from netzob.Inference.Vocabulary.TreeViews.TreeGroupGenerator import TreeGroupGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeMessageGenerator import TreeMessageGenerator
from netzob.Inference.Vocabulary.TreeViews.TreeTypeStructureGenerator import TreeTypeStructureGenerator

#+---------------------------------------------- 
#| UImodelization :
#|     GUI for message modelization
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UImodelization:
    TARGET_TYPE_TEXT = 80
    TARGETS = [('text/plain', 0, TARGET_TYPE_TEXT)]
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
#        self.netzob.groups.initGroupsWithTraces()
        pass

    def update(self):
        self.updateTreeStoreGroup()
        self.updateTreeStoreMessage()
        self.updateTreeStoreTypeStructure()

    def clear(self):
        self.selectedSymbol = None

    def kill(self):
        pass
    
    def save(self, file):
        self.log = logging.getLogger('netzob.Modelization.UImodelization.py')
        self.log.info("Saving the modelization")
        
        stateParser = StateParser.StateParser(file)
        stateParser.saveInConfiguration(self.netzob.groups.getGroups())
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main class
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.UImodelization.py')
        self.netzob = netzob
        self.selectedSymbol = None
        self.selectedMessage = ""
        self.treeMessageGenerator = TreeMessageGenerator()
        self.treeMessageGenerator.initialization()
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeGroupGenerator = TreeGroupGenerator(self.netzob)
        self.treeGroupGenerator.initialization()
        
        # Definition of the Sequence Onglet
        # First we create an VBox which hosts the two main children
        self.panel = gtk.VBox(False, spacing=0)
        self.panel.show()
        self.defer_select = False

        configParser = ConfigurationParser()
        
        #+---------------------------------------------- 
        #| TOP PART OF THE GUI : BUTTONS
        #+----------------------------------------------
        topPanel = gtk.HBox(False, spacing=5)
        topPanel.show()
        self.panel.pack_start(topPanel, False, False, 0)

        ## Classification by similarity
        frame = gtk.Frame()
        frame.set_label("1 - Classification by similarity")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=3, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget entry for chosing the alignment score sub-limit
        label = gtk.Label("Similarity threshold:")
        label.show()
        combo = gtk.combo_box_entry_new_text()
#        combo.set_size_request(60, -1)
        combo.set_model(gtk.ListStore(str))
        combo.connect("changed", self.updateScoreLimit)
        possible_choices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
        min_equivalence = configParser.getFloat("clustering", "equivalence_threshold")
        for i in range(len(possible_choices)):
            combo.append_text(str(possible_choices[i]))
            if str(possible_choices[i]) == str(int(min_equivalence)):
                combo.set_active(i)
        combo.show()
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button activate orphan reduction
        butOrphanReduction = gtk.CheckButton("Orphan reduction")
        doOrphanReduction = configParser.getInt("clustering", "orphan_reduction")
        if doOrphanReduction == 1:
            butOrphanReduction.set_active(True)
        else:
            butOrphanReduction.set_active(False)
        butOrphanReduction.connect("toggled", self.activeOrphanReduction)
        butOrphanReduction.show()
        table.attach(butOrphanReduction, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button merge common regexes
        but = gtk.Button("Merge common regexes")
        but.connect("clicked", self.netzob.groups.mergeCommonRegexes, self)
        ## TODO: merge common regexes (if it is really usefull)
        but.show()
        but.set_sensitive(False)
        table.attach(but, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Message format inferrence
        frame = gtk.Frame()
        frame.set_label("2 - Message format inferrence")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=5, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button slick regexes
        but = gtk.Button("Slick regexes")
        but.connect("clicked", self.netzob.groups.slickRegexes, self)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget checkbox for selecting the slickery during alignement process
        but = gtk.CheckButton("Slick regexes")
        doInternalSlick = configParser.getInt("clustering", "do_internal_slick")
        if doInternalSlick == 1:
            but.set_active(True)
        else:
            but.set_active(False)
        but.connect("toggled", self.activeInternalSlickRegexes)
        but.show()
        table.attach(but, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget for launching the analysis
        but = gtk.Button(gtk.STOCK_OK)
        but.set_label("Discover alignment")
        but.connect("clicked", self.startAnalysis_cb)
        but.show()
        table.attach(but, 0, 2, 2, 3, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=5, ypadding=5)

        # Widget entry for chosing the alignment delimiter
        label = gtk.Label("Set the delimiter : ")
        label.show()
        entry = gtk.Entry(4)
        entry.show()
        table.attach(label, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget for forcing alignment delimiter
        but = gtk.Button(gtk.STOCK_OK)
        but.set_label("Force alignment")
        but.connect("clicked", self.forceAlignment_cb, entry)
        but.show()
        table.attach(but, 0, 2, 4, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL, xpadding=5, ypadding=5)
       
        ## Field type inferrence
        frame = gtk.Frame()
        frame.set_label("3 - Field type inferrence")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=2, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button refine regex
        but = gtk.Button("Refine regexes")
        but.connect("clicked", self.refineRegexes_cb)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Widget button to show fields entropy
        but = gtk.Button("Messages distribution")
        but.connect("clicked", self.messagesDistribution_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Widget for choosing the analysed protocole type
        label = gtk.Label("Protocol type : ")
        label.show()
        combo = gtk.combo_box_entry_new_text()
#        combo.set_size_request(300, -1)
        combo.set_model(gtk.ListStore(str))
        combo.append_text("Text based (HTTP, FTP)")
        combo.append_text("Fixed fields binary based (IP, TCP)")
        combo.append_text("Variable fields binary based (ASN.1)")
        combo.connect("changed", self.updateProtocolType)
        protocol_type_ID = configParser.getInt("clustering", "protocol_type")
        combo.set_active(protocol_type_ID)
        combo.show()
        table.attach(label, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        table.attach(combo, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Dependencies inferrence
        frame = gtk.Frame()
        frame.set_label("4 - Dependencies inferrence")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button find size fields
        but = gtk.Button("Find size fields")
        # TODO: just try to use an ASN.1 parser to find the simple TLV protocols
        but.connect("clicked", self.findSizeFields)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button for environment dependencies
        but = gtk.Button("Environment dependencies")
        but.connect("clicked", self.env_dependencies_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        ## Semantic inferrence
        frame = gtk.Frame()
        frame.set_label("5 - Semantic inferrence")
        frame.show()
        topPanel.pack_start(frame, False, False, 0)
        table = gtk.Table(rows=4, columns=4, homogeneous=False)
        table.show()
        frame.add(table)

        # Widget button data carving
        but = gtk.Button("Data carving")
        but.connect("clicked", self.dataCarving_cb)
        but.show()
        table.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Widget button for search
        but = gtk.Button("Search")
        but.connect("clicked", self.search_cb)
        but.show()
        table.attach(but, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : GROUP TREEVIEW
        #+----------------------------------------------           
        bottomPanel = gtk.HPaned()
        bottomPanel.show()
        self.panel.pack_start(bottomPanel, True, True, 0)
        leftPanel = gtk.VBox(False, spacing=0)
#        leftPanel.set_size_request(-1, -1)
        leftPanel.show()
        bottomPanel.add(leftPanel)
        # Initialize the treeview generator for the groups
        leftPanel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeGroupGenerator.getTreeview().enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeGroupGenerator.getTreeview().connect("drag_data_received", self.drop_fromDND)
#        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupChanged)
        self.treeGroupGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_groups)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : MESSAGE TREEVIEW MESSAGE
        #+----------------------------------------------
        rightPanel = gtk.VPaned()
        rightPanel.show()
        bottomPanel.add(rightPanel)
        rightPanel.add(self.treeMessageGenerator.getScrollLib())
        
        # Attach to the treeview few actions (DnD, cursor and buttons handlers...)
        self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        self.treeMessageGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect('button-release-event', self.button_release_on_treeview_messages)
        self.treeMessageGenerator.getTreeview().connect("row-activated", self.dbClickToChangeType)

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        rightPanel.add(self.treeTypeStructureGenerator.getScrollLib())        
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_treeview_typeStructure)
        self.log.debug("GUI for sequential part is created")

    #+---------------------------------------------- 
    #| startAnalysis :
    #|   Parse the traces and store the results
    #+----------------------------------------------
    def startAnalysis_cb(self, widget):
        if self.netzob.getCurrentProject() == None:
            self.log.info("A project must be loaded to start an analysis")
            return
        self.selectedSymbol = None
        self.treeMessageGenerator.clear()
        self.treeGroupGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        
        self.alignThread = threading.Thread(None, vocabulary.alignWithNeedlemanWunsh, None, ([self.netzob.getCurrentProject().getConfiguration(), self.update]), {})
        self.alignThread.start()
        
    #+---------------------------------------------- 
    #| forceAlignment :
    #|   Force the delimiter for sequence alignment
    #+----------------------------------------------
    def forceAlignment_cb(self, widget, delimiter):
        if self.netzob.getCurrentProject() == None:
            self.log.info("A project must be loaded to start an analysis")
            return
        self.selectedGroup = ""
        self.treeMessageGenerator.clear()
        self.treeGroupGenerator.clear()
        self.treeTypeStructureGenerator.clear()
        self.update()
        vocabulary = self.netzob.getCurrentProject().getVocabulary()
        vocabulary.alignWithDelimiter(self.netzob.getCurrentProject().getConfiguration(), delimiter.get_text())
        self.update()
    
    #+---------------------------------------------- 
    #| button_press_on_treeview_groups :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_groups(self, treeview, event):
        self.log.debug("User requested a contextual menu (treeview group)")
        
        project = self.netzob.getCurrentProject()
        if project == None :
            self.log.warn("No current project loaded")
            return 
        if project.getVocabulary() == None :
            self.log.warn("The current project doesn't have any referenced vocabulary")
            return
        
        clickedSymbol = None
        
        x = int(event.x)
        y = int(event.y)
        clickedSymbol = self.treeGroupGenerator.getSymbolAtPosition(x, y)
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1 and clickedSymbol != None :
            self.selectedSymbol = clickedSymbol
            self.update()
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu_for_groups(event, clickedSymbol)

    def button_release_on_treeview_messages(self, treeview, event):
        # re-enable selection
        treeview.get_selection().set_select_function(lambda * ignore: True)
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and self.defer_select == target[0] and not (event.x == 0 and event.y == 0)): # certain drag and drop
            treeview.set_cursor(target[0], target[1], False)
            self.defer_select = False

    #+---------------------------------------------- 
    #| button_press_on_treeview_messages :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_messages(self, treeview, event):
        target = treeview.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == gtk.gdk.BUTTON_PRESS and not (event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)) and treeview.get_selection().path_is_selected(target[0])):
            # disable selection
            treeview.get_selection().set_select_function(lambda * ignore: False)
            self.defer_select = target[0]

        # Display the details of a packet
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)
                    symbol = self.treeMessageGenerator.getSymbol()
                    self.treeTypeStructureGenerator.setSymbol(symbol)
                    self.treeTypeStructureGenerator.setMessageByID(message_id)
                    self.updateTreeStoreTypeStructure()

        # Popup a menu
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (treeview messages)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            
            # Retrieve the selected message
            message_id = None
            aIter = treeview.get_model().get_iter(path)
            if aIter:
                if treeview.get_model().iter_is_valid(aIter):
                    message_id = treeview.get_model().get_value(aIter, 0)
            

            # Retrieve the selected column number
            iField = 0
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1
                
            selectedField = None
            print "iField = " + str(iField)
            for field in self.treeMessageGenerator.getSymbol().getFields() :
                if field.getIndex() == iField :
                    selectedField = field
            if selectedField == None :
                self.log.warn("Impossible to retrieve the clicked field !")
                return
                
            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific column
            typesList = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, selectedField, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate column
            concatMenu = gtk.Menu()
            if selectedField.getIndex() > 0 :
                item = gtk.MenuItem("with precedent field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
                concatMenu.append(item)
                
            if selectedField.getIndex() < len(self.treeMessageGenerator.getSymbol().getFields()) - 1:
                item = gtk.MenuItem("with next field")
                item.show()
                item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
                concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the column
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add entry to retrieve the field domain of definition
            item = gtk.MenuItem("Domain of definition")
            item.show()
            item.connect("activate", self.rightClickDomainOfDefinition, selectedField)
            menu.append(item)
            
            # Add entry to show properties of the message
            item = gtk.MenuItem("Properties")
            item.show()
            item.connect("activate", self.rightClickShowPropertiesOfMessage, message_id)
            menu.append(item)
            
            # Add entry to delete the message
            item = gtk.MenuItem("Delete message")
            item.show()
            item.connect("activate", self.rightClickDeleteMessage, message_id)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| button_press_on_treeview_typeStructure :
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_typeStructure(self, treeview, event):
        if self.treeTypeStructureGenerator.getMessage() == None:
            return

        # Popup a menu
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.log.debug("User requested a contextual menu (on treeview typeStructure)")
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            (iField,) = path
            
            
            selectedField = None
            for field in self.treeMessageGenerator.getSymbol().getFields() :
                if field.getIndex() == iField :
                    selectedField = field
            if selectedField == None :
                self.log.warn("Impossible to retrieve the clicked field !")
                return
            
            menu = gtk.Menu()
            # Add sub-entries to change the type of a specific field
            typesList = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
            typeMenu = gtk.Menu()
            for aType in typesList:
                item = gtk.MenuItem("Render in : " + str(aType))
                item.show()
                item.connect("activate", self.rightClickToChangeType, selectedField, aType)   
                typeMenu.append(item)
            item = gtk.MenuItem("Change Type")
            item.set_submenu(typeMenu)
            item.show()
            menu.append(item)

            # Add entries to concatenate fields
            concatMenu = gtk.Menu()
            item = gtk.MenuItem("with precedent field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "left")
            concatMenu.append(item)
            item = gtk.MenuItem("with next field")
            item.show()
            item.connect("activate", self.rightClickToConcatColumns, selectedField, "right")
            concatMenu.append(item)
            item = gtk.MenuItem("Concatenate")
            item.set_submenu(concatMenu)
            item.show()
            menu.append(item)

            # Add entry to split the field
            item = gtk.MenuItem("Split column")
            item.show()
            item.connect("activate", self.rightClickToSplitColumn, selectedField)
            menu.append(item)

            # Add entry to export fields
            item = gtk.MenuItem("Export selected fields")
            item.show()
            item.connect("activate", self.exportSelectedFields_cb)
            menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

    #+---------------------------------------------- 
    #| exportSelectedFields_cb :
    #|   Callback to export the selected fields
    #|   as a new trace
    #+----------------------------------------------
    def exportSelectedFields_cb(self, event):
        # Retrieve associated messages of selected fields
        aggregatedCells = {}
        (model, paths) = self.treeTypeStructureGenerator.getTreeview().get_selection().get_selected_rows()
        for path in paths:
            aIter = model.get_iter(path)
            if(model.iter_is_valid(aIter)):
                iField = model.get_value(aIter, 0)
                
                selectedField = None
                for field in self.treeMessageGenerator.getSymbol().getFields() :
                    if field.getIndex() == iField :
                        selectedField = field
                if selectedField == None :
                    self.log.warn("Impossible to retrieve the clicked field !")
                    return
                
                cells = self.treeTypeStructureGenerator.getSymbol().getMessagesValuesByField(selectedField)
                for i in range(len(cells)):
                    if not i in aggregatedCells:
                        aggregatedCells[i] = ""
                    aggregatedCells[i] += str(cells[i])

        # Popup a menu to save the data
        dialog = gtk.Dialog(title="Save selected data", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()

        # Add to an existing trace
        label = gtk.Label("Add to an existing trace")
        label.show()
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = gtk.Button("Save")
        but.connect("clicked", self.add_packets_to_existing_trace, entry, aggregatedCells, dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = gtk.Label("Create a new trace")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Save")
        but.connect("clicked", self.create_new_trace, entry, aggregatedCells, dialog)
        but.show()
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, messages, dialog):
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        existingTraceDir = projectsDirectoryPath + os.sep + entry.get_active_text()
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages:
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, messages, dialog):
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            if entry.get_text() == tmpDir:
                dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
                dialogBis.set_size_request(250, 50)
                dialogBis.show()
                return

        # Create the dest Dir
        newTraceDir = projectsDirectoryPath + os.sep + entry.get_text()
        os.mkdir(newTraceDir)
        # Create the new XML structure
        res = "<datas>\n"
        for message in messages.values():
            res += "<data proto=\"ipc\" sourceIp=\"local\" sourcePort=\"local\" targetIp=\"local\" targetPort=\"local\" timestamp=\"" + str(time.time()) + "\">\n"
            res += message + "\n"
            res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir + os.sep + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.netzob.updateListOfAvailableProjects()

    #+---------------------------------------------- 
    #| rightClickDomainOfDefinition :
    #|   Retrieve the domain of definition of the selected column
    #+----------------------------------------------
    def rightClickDomainOfDefinition(self, event, field):
        cells = self.treeMessageGenerator.getSymbol().getMessagesValuesByField(field)
        tmpDomain = set()
        for cell in cells:
            tmpDomain.add(TypeConvertor.encodeNetzobRawToGivenType(cell, field.getSelectedType()))
        domain = sorted(tmpDomain)

        dialog = gtk.Dialog(title="Domain of definition for the column " + field.getName(), flags=0, buttons=None)
         
        # Text view containing domain of definition 
        ## ListStore format :
        # str: symbol.id
        treeview = gtk.TreeView(gtk.ListStore(str)) 
        treeview.set_size_request(500, 300)
        treeview.show()
        
        cell = gtk.CellRendererText()
        cell.set_sensitive(True)
        cell.set_property('editable', True)
        
        column = gtk.TreeViewColumn("Column " + str(field.getIndex()))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)        
        
        treeview.append_column(column)

        # Just to force the calculation of each group with its associated messages
        currentProject = self.netzob.getCurrentProject()
        if currentProject == None :
            self.log.warn("No current project found")
            return
        if currentProject.getVocabulary() == None :
            self.log.warn("The project has no vocbaulary to work with.")
            return
        
        for symbol in currentProject.getVocabulary().getSymbols():
            self.selectedSymbol = symbol
            self.treeMessageGenerator.default(symbol)

        for elt in domain:
            treeview.get_model().append([elt])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| rightClickShowPropertiesOfMessage :
    #|   Show a popup to present the properties of the selected message
    #+----------------------------------------------
    def rightClickShowPropertiesOfMessage(self, event, id_message):
        self.log.debug("The user wants to see the properties of message " + str(id_message))
        
        # Retrieve the selected message
        message = self.selectedSymbol.getMessageByID(id_message)
        if message == None :
            self.log.warning("Impossible to retrieve the message based on its ID [{0}]".format(id_message))
            return
        
        # Create the dialog
        dialog = gtk.Dialog(title="Properties of message " + str(message.getID()), flags=0, buttons=None)
        ## ListStore format : (str=key, str=value)
        treeview = gtk.TreeView(gtk.ListStore(str, str)) 
        treeview.set_size_request(500, 300)
        treeview.show()
        
        cell = gtk.CellRendererText()
        
        columnProperty = gtk.TreeViewColumn("Property")
        columnProperty.pack_start(cell, True)
        columnProperty.set_attributes(cell, text=0)
        
        columnValue = gtk.TreeViewColumn("Value")
        columnValue.pack_start(cell, True)
        columnValue.set_attributes(cell, text=1)        
        
        treeview.append_column(columnProperty)
        treeview.append_column(columnValue)
         
        # Retrieves all the properties of current message and 
        # insert them in the treeview
        for property in message.getProperties():
            treeview.get_model().append(property)
                
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()
            
        
    #+---------------------------------------------- 
    #| rightClickDeleteMessage :
    #|   Delete the requested message
    #+----------------------------------------------
    def rightClickDeleteMessage(self, event, id_message):
        self.log.debug("The user wants to delete the message " + str(id_message))
        
        message_symbol = self.selectedSymbol
        message = self.selectedSymbol.getMessageByID(id_message)
        
        # Break if the message to move was not found
        if message == None :
            self.log.warning("Impossible to retrieve the message to remove based on its ID [{0}]".format(id_message))
            return
        
        questionMsg = "Click yes to confirm the deletion of message {0}".format(id_message)
        md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == gtk.RESPONSE_YES:
            self.log.debug("The user has confirmed !")
            message_symbol.removeMessage(message)
            self.update()
            

    #+---------------------------------------------- 
    #| rightClickToChangeType :
    #|   Callback to change the column type
    #|   by doing a right click
    #+----------------------------------------------
    def rightClickToChangeType(self, event, field, aType):
        field.setSelectedType(aType)
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToConcatColumns:
    #|   Callback to concatenate two columns
    #+----------------------------------------------
    def rightClickToConcatColumns(self, event, field, strOtherCol):
        self.log.debug("Concatenate the column " + str(field.getIndex()) + " with the " + str(strOtherCol) + " column")

        if field.getIndex() == 0 and strOtherCol == "left":
            self.log.debug("Can't concatenate the first column with its left column")
            return

        if field.getIndex() + 1 == len(self.selectedSymbol.getFields()) and strOtherCol == "right":
            self.log.debug("Can't concatenate the last column with its right column")
            return

        if strOtherCol == "left":
            self.selectedSymbol.concatFields(field.getIndex() - 1)
        else:
            self.selectedSymbol.concatFields(field.getIndex())
        self.treeMessageGenerator.updateDefault()
        self.update()

    #+---------------------------------------------- 
    #|  rightClickToSplitColumn:
    #|   Callback to split a column
    #+----------------------------------------------
    def rightClickToSplitColumn(self, event, field):
        dialog = gtk.Dialog(title="Split column " + str(field.getIndex()), flags=0, buttons=None)
        textview = gtk.TextView()
        textview.set_editable(False)
        textview.get_buffer().create_tag("redTag", weight=pango.WEIGHT_BOLD, foreground="red", family="Courier")
        textview.get_buffer().create_tag("greenTag", weight=pango.WEIGHT_BOLD, foreground="#006400", family="Courier")
        self.split_position = 2
        self.split_max_len = 0

        # Find the size of the longest message
        cells = self.selectedSymbol.getMessagesValuesByField(field)
        for m in cells:
            if len(m) > self.split_max_len:
                self.split_max_len = len(m)

        # Left arrow
        arrow = gtk.Arrow(gtk.ARROW_LEFT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "left", field)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Right arrow
        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        arrow.show()
        but = gtk.Button()
        but.add(arrow)
        but.connect("clicked", self.adjustSplitColumn, textview, "right", field)
        but.show()
        dialog.action_area.pack_start(but, True, True, 0)

        # Split button
        but = gtk.Button(label="Split column")
        but.show()
        but.connect("clicked", self.doSplitColumn, textview, field, dialog)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing selected column messages
        frame = gtk.Frame()
        frame.set_label("Content of the column to split")
        frame.show()
        textview.set_size_request(400, 300)
#        cells = self.treeMessageGenerator.getGroup().getCellsByCol(iCol)

        for m in cells:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getSelectedType()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getSelectedType()) + "\n", "greenTag")
        textview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(textview)
        frame.add(scroll)
        dialog.vbox.pack_start(frame, True, True, 0)
        dialog.show()

    def doSplitColumn(self, widget, textview, field, dialog):
        if self.split_max_len <= 2:
            dialog.destroy()
            return

        self.selectedSymbol.splitField(field, self.split_position)
        self.treeMessageGenerator.updateDefault()            
        dialog.destroy()
        self.update()

    def adjustSplitColumn(self, widget, textview, direction, field):
        if self.split_max_len <= 2:
            return
        messages = self.selectedSymbol.getMessagesValuesByField(field)

        # Bounds checking
        if direction == "left":
            self.split_position -= 2
            if self.split_position < 2:
                self.split_position = 2
        else:
            self.split_position += 2
            if self.split_position > self.split_max_len - 2:
                self.split_position = self.split_max_len - 2

        # Colorize text according to position
        textview.get_buffer().set_text("")
        for m in messages:
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[:self.split_position], field.getSelectedType()) + "  ", "redTag")
            textview.get_buffer().insert_with_tags_by_name(textview.get_buffer().get_end_iter(), TypeConvertor.encodeNetzobRawToGivenType(m[self.split_position:], field.getSelectedType()) + "\n", "greenTag")

    #+---------------------------------------------- 
    #| dbClickToChangeType :
    #|   Called when user double click on a row
    #|    in order to change the column type
    #+----------------------------------------------
    def dbClickToChangeType(self, treeview, path, treeviewColumn):
        # Retrieve the selected column number
        iField = 0
        for col in treeview.get_columns():
            if col == treeviewColumn:
                break
            iField += 1
                
        selectedField = None
        for field in self.treeMessageGenerator.getSymbol().getFields() :
            if field.getIndex() == iField :
                selectedField = field
        
        if selectedField == None :
            self.log.warn("Impossible to retrieve the clicked field !")
            return
        
        # Find the next possible type for this column
        possibleTypes = self.treeMessageGenerator.getSymbol().getPossibleTypesForAField(selectedField)
        i = 0
        chosedType = selectedField.getSelectedType()
        for aType in possibleTypes:
            if aType == chosedType:
                chosedType = possibleTypes[(i + 1) % len(possibleTypes)]
                break
            i += 1

        # Apply the new choosen type for this column
        selectedField.setSelectedType(chosedType)
        self.treeMessageGenerator.updateDefault()
        
    #+---------------------------------------------- 
    #| build_context_menu_for_groups :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def build_context_menu_for_groups(self, event, symbol):
        # Retrieves the group on which the user has clicked on
        
        entries = [        
                  (gtk.STOCK_EDIT, self.displayPopupToEditGroup, (symbol != None)),
                  (gtk.STOCK_ADD, self.displayPopupToCreateGroup, (symbol == None)),
                  (gtk.STOCK_REMOVE, self.displayPopupToRemoveGroup, (symbol != None))
        ]

        menu = gtk.Menu()
        for stock_id, callback, sensitive in entries:
            item = gtk.ImageMenuItem(stock_id)
            item.connect("activate", callback, symbol)  
            item.set_sensitive(sensitive)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)


    #+---------------------------------------------- 
    #| displayPopupToCreateGroup_ResponseToDialog :
    #|   pygtk is so good ! arf :( <-- clap clap :D
    #+----------------------------------------------
    def displayPopupToCreateGroup_ResponseToDialog(self, entry, dialog, response):
        dialog.response(response)

    def displayPopupToEditGroup(self, event, group):
        dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
        dialog.set_markup("<b>Please enter the name of the symbol :</b>")
        #create the text input field
        entry = gtk.Entry()
        entry.set_text(group.getName())
        #allow the user to press enter to do ok
        entry.connect("activate", self.responseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name : "), False, 5, 5)
        hbox.pack_end(entry)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        text = entry.get_text()
        if (len(text) > 0) :
            self.selectedSymbol.setName(text)
        dialog.destroy()
        
        self.update()

    def responseToDialog(self, entry, dialog, response):
        dialog.response(response)
    
    
    #+---------------------------------------------- 
    #| displayPopupToCreateGroup :
    #|   Display a form to create a new group.
    #|   Based on the famous dialogs
    #+----------------------------------------------
    def displayPopupToCreateGroup(self, event, group):
        
        #base this on a message dialog
        dialog = gtk.MessageDialog(
                                   None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_OK,
                                   None)
        dialog.set_markup("<b>Please enter symbol's name</b> :")
        #create the text input field
        entry = gtk.Entry()
        #allow the user to press enter to do ok
        entry.connect("activate", self.displayPopupToCreateGroup_ResponseToDialog, dialog, gtk.RESPONSE_OK)
        #create a horizontal box to pack the entry and a label
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Name :"), False, 5, 5)
        hbox.pack_end(entry)
        #add it and show it
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        #go go go
        dialog.run()
        newSymbolName = entry.get_text()
        dialog.destroy()
        
        if (len(newSymbolName) > 0) :
            newSymbolId = str(uuid.uuid4())
            self.log.debug("a new symbol will be created with the given name : {0}".format(newSymbolName))
            newSymbol = Symbol(newSymbolId, newSymbolName)
            
            self.netzob.getCurrentProject().getVocabulary().addSymbol(newSymbol)
            
            #Update Left and Right
            self.update()
        
    #+---------------------------------------------- 
    #| displayPopupToRemoveGroup :
    #|   Display a popup to remove a group
    #|   the removal of a group can only occurs
    #|   if its an empty group
    #+----------------------------------------------    
    def displayPopupToRemoveGroup(self, event, symbol):
        
        if (len(symbol.getMessages()) == 0) :
            self.log.debug("Can remove the group {0} since it's an empty one.".format(symbol.getName()))
            questionMsg = "Click yes to confirm the removal of the symbol {0}".format(symbol.getName())
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, questionMsg)
            result = md.run()
            md.destroy()
            if result == gtk.RESPONSE_YES:
                self.netzob.getCurrentProject().getVocabulary().removeSymbol(symbol)
                #Update Left and Right
                self.update()
            else :
                self.log.debug("The user didn't confirm the deletion of the group " + symbol.getName())                
            
        else :
            self.log.debug("Can't remove the symbol {0} since its not an empty one.".format(symbol.getName()))
            errorMsg = "The selected symbol cannot be removed since it contains messages."
            md = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, errorMsg)
            md.run()
            md.destroy()
        
    #+---------------------------------------------- 
    #| drop_fromDND :
    #|   defines the operation executed when a message is
    #|   is dropped out current group to the selected group 
    #+----------------------------------------------
    def drop_fromDND(self, treeview, context, x, y, selection, info, etime):
        ids = selection.data
        for msg_id in ids.split(";") :
            
            modele = treeview.get_model()
            info_depot = treeview.get_dest_row_at_pos(x, y)
            
            # First we search for the message to move
            message = None
            message_symbol = self.selectedSymbol
            for msg in message_symbol.getMessages() :
                if str(msg.getID()) == msg_id :
                    message = msg
            
            # Break if the message to move was not found
            if message == None :
                self.log.warning("Impossible to retrieve the message to move based on its ID [{0}]".format(msg_id))
                return
            
            self.log.debug("The message having the ID [{0}] has been found !".format(msg_id))
            
            # Now we search for the new group of the message
            if info_depot :
                chemin, position = info_depot
                iter = modele.get_iter(chemin)
                new_symbol_id = str(modele.get_value(iter, 0))
                
                new_message_symbol = self.netzob.getCurrentProject().getVocabulary().getSymbol(new_symbol_id)
                    
            if new_message_symbol == None :
                self.log.warning("Impossible to retrieve the symbol in which the selected message must be moved out.")
                return
            
            self.log.debug("The new symbol of the message is {0}".format(str(new_message_symbol.getID())))
            #Removing from its old group
            message_symbol.removeMessage(message)
            
            #Adding to its new group
            new_message_symbol.addMessage(message)            
        
        message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
        new_message_symbol.buildRegexAndAlignment(self.netzob.getCurrentProject().getConfiguration())
        #Update Left and Right
        self.update()
        return
   
    #+---------------------------------------------- 
    #| drag_fromDND :
    #|   defines the operation executed when a message is
    #|   is dragged out current group 
    #+----------------------------------------------
    def drag_fromDND(self, treeview, contexte, selection, info, dateur):   
        ids = []             
        treeview.get_selection().selected_foreach(self.foreach_drag_fromDND, ids)
        selection.set(selection.target, 8, ";".join(ids))
    
    def foreach_drag_fromDND(self, model, path, iter, ids):
        texte = str(model.get_value(iter, 0))
        ids.append(texte)
        return
    
    #+---------------------------------------------- 
    #| Update the content of the tree store for groups
    #+----------------------------------------------
    def updateTreeStoreGroup(self):        
        # Updates the treestore with a selected message
        if (self.selectedMessage != "") :
            self.treeGroupGenerator.messageSelected(self.selectedMessage)
            self.selectedMessage = ""
        else :
            # Default display of the groups
            self.treeGroupGenerator.default()
 
    #+---------------------------------------------- 
    #| Update the content of the tree store for messages
    #+----------------------------------------------
    def updateTreeStoreMessage(self):     
        # If we found it we can update the content of the treestore        
        if self.selectedSymbol != None :
            self.treeMessageGenerator.default(self.selectedSymbol)
            # enable dragging message out of current group
            self.treeMessageGenerator.getTreeview().enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
            self.treeMessageGenerator.getTreeview().connect("drag-data-get", self.drag_fromDND)      
        # Else, quite weird so throw a warning
        else :
            self.treeMessageGenerator.default(None)
            
            

    #+---------------------------------------------- 
    #| Update the content of the tree store for type structure
    #+----------------------------------------------
    def updateTreeStoreTypeStructure(self):
        self.treeTypeStructureGenerator.update()
       
    
    #+---------------------------------------------- 
    #| Called when user select a new score limit
    #+----------------------------------------------
    def updateScoreLimit(self, combo):
        val = combo.get_active_text()
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_EQUIVALENCE_THRESHOLD, int(val))

    #+---------------------------------------------- 
    #| Called when user wants to slick internally in libNeedleman
    #+----------------------------------------------
    def activeInternalSlickRegexes(self, checkButton):
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_DO_INTERNAL_SLICK, checkButton.get_active())
        
    #+---------------------------------------------- 
    #| Called when user wants to activate orphan reduction
    #+----------------------------------------------
    def activeOrphanReduction(self, checkButton):
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ORPHAN_REDUCTION, checkButton.get_active())

    #+---------------------------------------------- 
    #| Called when user wants to modify the expected protocol type
    #+----------------------------------------------
    def updateProtocolType(self, combo):
        valID = combo.get_active()
        if valID == 0:
            display = "ascii"
        else:
            display = "binary"
        
        if self.netzob.getCurrentProject() != None :
            self.netzob.getCurrentProject().getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_GLOBAL_DISPLAY, display)
        
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                for field in symbol.getFields() :
                    field.setSelectedType(display)
            self.update()

    #+---------------------------------------------- 
    #| Called when user wants to refine regexes
    #+----------------------------------------------
    def refineRegexes_cb(self, button):
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            symbol.refineRegexes()
        dialog = gtk.Dialog(title="Refinement done", flags=0, buttons=None)
        dialog.set_size_request(250, 50)
        dialog.show()
        self.update()

    #+---------------------------------------------- 
    #| Called when user wants to execute data carving
    #+----------------------------------------------
    def dataCarving_cb(self, button):
        dialog = gtk.Dialog(title="Data carving results", flags=0, buttons=None)
        
        if self.netzob.getCurrentProject() == None :
            return  

        # Just to force the calculation of the splitted messages by regex
        ## TODO: put this at the end of the alignement process
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            self.treeMessageGenerator.default(symbol)
        
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_TOP)
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            scroll = symbol.dataCarving()
            if scroll != None:
                notebook.append_page(scroll, gtk.Label(symbol.getName()))
        

        dialog.vbox.pack_start(notebook, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to search data in messages
    #+----------------------------------------------
    def search_cb(self, button):
        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)

        # Just to force the calculation of the splitted messages by regex 
        ## TODO: put this at the end of the alignement process
        if self.netzob.getCurrentProject() != None :
        
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                self.treeMessageGenerator.default(symbol)
        
            searchPanel = SearchView(self.netzob.getCurrentProject())
            dialog.vbox.pack_start(searchPanel.getPanel(), True, True, 0)
            dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to identifies environment dependencies
    #+----------------------------------------------
    def env_dependencies_cb(self, button):
        dialog = gtk.Dialog(title="Search", flags=0, buttons=None)

        # Just to force the calculation of the splitted messages by regex 
        ## TODO: put this at the end of the alignement process
        if self.netzob.getCurrentProject() != None :
            
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                self.treeMessageGenerator.default(symbol)
                
            notebook = gtk.Notebook()
            notebook.show()
            notebook.set_tab_pos(gtk.POS_TOP)
            for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
                scroll = symbol.envDependencies(self.netzob.getCurrentProject())
                if scroll != None:
                    notebook.append_page(scroll, gtk.Label(symbol.getName())) 
            
            dialog.vbox.pack_start(notebook, True, True, 0)
            dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to see the distribution of a group of messages
    #+----------------------------------------------
    def messagesDistribution_cb(self, but):
        if self.selectedSymbol == None:
            self.log.info("No group selected")
            return
        entropy = Entropy(self.selectedSymbol)
        entropy.buildDistributionView()

    #+---------------------------------------------- 
    #| Called when user wants to find the potential size fields
    #+----------------------------------------------
    def findSizeFields(self, button):
        # Create a temporary symbol for testing size fields
        tmp_symbol = Symbol("tmp_symbol", "tmp_group")
        
        if self.netzob.getCurrentProject() == None :
            return  

        # Just to force the calculation of the splitted messages by regex
        ## TODO: put this at the end of the alignement process
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            self.treeMessageGenerator.default(symbol)
        

        dialog = gtk.Dialog(title="Potential size fields and related payload", flags=0, buttons=None)
        ## ListStore format :
        # str: group.id
        # int: size field column
        # int: size field size
        # int: start column
        # int: substart column
        # int: end column
        # int: subend column
        # str: message rendered in cell
        treeview = gtk.TreeView(gtk.ListStore(str, int, int, int, int, int, int, str)) 
        cell = gtk.CellRendererText()
        treeview.connect("cursor-changed", self.sizeField_selected, tmp_symbol)
        column = gtk.TreeViewColumn('Size field and related payload')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=7)
        treeview.append_column(column)

        # Chose button
        but = gtk.Button(label="Apply size field")
        but.show()
        but.connect("clicked", self.applySizeField, dialog, tmp_symbol)
        dialog.action_area.pack_start(but, True, True, 0)

        # Text view containing potential size fields
        treeview.set_size_request(800, 300)
        
        self.netzob.getCurrentProject().getVocabulary().findSizeFields(treeview.get_model())
        
        treeview.show()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        dialog.vbox.pack_start(scroll, True, True, 0)
        dialog.show()

    #+---------------------------------------------- 
    #| Called when user wants to try to apply a size field on a group
    #+----------------------------------------------
    def sizeField_selected(self, treeview, symbol):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                group_id = model.get_value(iter, 0)
                size_field = model.get_value(iter, 1)
                size_field_len = model.get_value(iter, 2)
                start_field = model.get_value(iter, 3)
                start_field_len = model.get_value(iter, 4)
                end_field = model.get_value(iter, 5)
                end_field_len = model.get_value(iter, 6)
                
                ## Select the related group
                self.selectedSymbol = symbol
                self.update()

                ## Select the first message for details (after the 3 header rows)
                it = self.treeMessageGenerator.treestore.get_iter_first()
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return
                it = self.treeMessageGenerator.treestore.iter_next(it)
                if it == None:
                    return

                # Build a temporary group
                symbol.clear()
                for message in self.treeMessageGenerator.getSymbol().getMessages():
                    tmp_message = RawMessage("tmp", 329832, message.getData())
                    symbol.addMessage(tmp_message)
                symbol.setAlignment(copy.deepcopy(self.treeMessageGenerator.getSymbol().getAlignment()))
                symbol.setFields(copy.deepcopy(list(self.treeMessageGenerator.getSymbol().getFields())))

                self.treeTypeStructureGenerator.setSymbol(symbol)
                self.treeTypeStructureGenerator.setMessageByID(symbol.getMessages()[-1].getID())

                # Optionaly splits the columns if needed, and handles columns propagation
#                if symbol.splitColumn(size_field, size_field_len) == True:
#                    if size_field < start_field:
#                        start_field += 1
#                    if end_field != -1:
#                        end_field += 1
#                symbol.setDescriptionByCol(size_field, "Size field")
#                group.setColorByCol(size_field, "red")
#                if group.splitColumn(start_field, start_field_len) == True:
#                    start_field += 1
#                    if end_field != -1:
#                        end_field += 1
#                group.setDescriptionByCol(start_field, "Start of payload")
#                group.splitColumn(end_field, end_field_len)
#
#                # Adapt tabulation for encapsulated payloads
#                if end_field != -1:
#                    for iCol in range(start_field, end_field + 1):
#                        group.setTabulationByCol(iCol, group.getTabulationByCol(iCol) + 10)
#                else:
#                    group.setTabulationByCol(start_field, group.getTabulationByCol(start_field) + 10)

                # View the proposed protocol structuration
                self.update()

    #+---------------------------------------------- 
    #| Called when user wants to apply a size field on a group
    #+----------------------------------------------
    def applySizeField(self, button, dialog, group):
#        self.treeMessageGenerator.getGroup().setColumns(copy.deepcopy(list(group.getColumns())))
        dialog.destroy()
