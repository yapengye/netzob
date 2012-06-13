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
import gtk
import pygtk
import tempfile
pygtk.require('2.0')
import logging
import os
import time
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ExecutionContext import ExecutionContext
from netzob.Import.GOTPoisoning.PrototypesRepositoryParser import PrototypesRepositoryParser
from netzob.Import.GOTPoisoning.ParasiteGenerator import ParasiteGenerator
from netzob.Import.GOTPoisoning.InjectorGenerator import InjectorGenerator
from netzob.Import.GOTPoisoning.GOTPoisoner import GOTPoisoner


#+---------------------------------------------------------------------------+
#| Api:
#|     GUI for capturing messages from api hooking
#+---------------------------------------------------------------------------+
class ApiImport:

    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #+-----------------------------------------------------------------------+
    def __init__(self, netzob):
        self.netzob = netzob
        self.listOfProcess = []

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.ApiImport.py')
        self.packets = []

        # First we parse the repository
        repositoryFile = self.netzob.getCurrentWorkspace().getPathOfPrototypes() + os.sep + "repository.xml"
        if repositoryFile == "" or not os.path.isfile(repositoryFile):
            self.log.warn(_("Unable to find a repository file for API injector."))
        else:
            self.repositoryOfSharedLib = PrototypesRepositoryParser.loadFromXML(repositoryFile)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = gtk.Table(rows=6, columns=5, homogeneous=False)
        self.panel.show()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of processes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        but = gtk.Button(_("Update processes list"))
        but.show()
        but.connect("clicked", self.updateProcessList_cb)
        self.processStore = gtk.combo_box_entry_new_text()
        self.processStore.show()
        self.processStore.set_size_request(500, -1)
        self.processStore.set_model(gtk.ListStore(str))
        self.panel.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.processStore, 1, 5, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.handlerID = self.processStore.connect("changed", self.processSelected_cb)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of DLL
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = gtk.ScrolledWindow()
        self.dllTreeview = gtk.TreeView(gtk.TreeStore(str, str, str))  # file descriptor, type, name
        self.dllTreeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn(_("Name"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.dllTreeview.append_column(column)
        # Col type
        column = gtk.TreeViewColumn(_("Version"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.dllTreeview.append_column(column)
        # Col name
        column = gtk.TreeViewColumn(_("Path"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.dllTreeview.append_column(column)
        self.dllTreeview.show()

        self.dllTreeview.connect("cursor-changed", self.dllSelected_cb)
#        self.dllHandlerID = self.dllTreeview.connect("changed", self.dllSelected_cb)

        scroll.add(self.dllTreeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 5, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of prototypes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.dllStore = gtk.combo_box_entry_new_text()
        self.dllStore.show()
        self.dllStore.set_size_request(300, -1)
        self.dllStore.set_model(gtk.ListStore(str))

        self.dllStore.connect("changed", self.prototypeSelected_cb)

        self.panel.attach(self.dllStore, 0, 3, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.butAddPrototype = gtk.Button(_("Create prototype"))
        self.butAddPrototype.show()
        self.butAddPrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butAddPrototype, 3, 4, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.butRemovePrototype = gtk.Button(_("Delete prototype"))
        self.butRemovePrototype.show()
        self.butRemovePrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butRemovePrototype, 4, 5, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of buttons (start and stop capture)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.startCapture = gtk.Button(_("Start capture"))
        self.startCapture.show()
        self.startCapture.connect("clicked", self.startCaptureFunction)
        self.panel.attach(self.startCapture, 3, 4, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.stopCapture = gtk.Button(_("Stop capture"))
        self.stopCapture.show()
        self.stopCapture.connect("clicked", self.stopCaptureFunction)
        self.panel.attach(self.stopCapture, 4, 5, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.pktTreestore = gtk.TreeStore(int, str, str, str, int)  # pktID, Function, Parameter, data, timestamp
        treeview = gtk.TreeView(self.pktTreestore)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        cell = gtk.CellRendererText()
        # Col fd
        column = gtk.TreeViewColumn(_("Function"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col direction
        column = gtk.TreeViewColumn(_("Parameter"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col Data
        column = gtk.TreeViewColumn(_("Data"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 6, 7, 0, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

    #+----------------------------------------------
    #| Called when user wants to update the process list
    #+----------------------------------------------
    def updateProcessList_cb(self, button):
        self.processStore.handler_block(self.handlerID)
        # clear the list of process
        self.processStore.get_model().clear()

        # retrieves the list of process
        self.listOfProcess = ExecutionContext.getCurrentProcesses()

        # add in the list all the process
        for process in self.listOfProcess:
            self.processStore.append_text(str(process.getPid()) + "\t" + process.getName())
        self.processStore.handler_unblock(self.handlerID)

    #+----------------------------------------------
    #| Called when user select a process
    #+----------------------------------------------
    def processSelected_cb(self, widget):
        # Updates the list of shared lib
        strProcessSelected = self.processStore.get_active_text()
        pid = int(strProcessSelected.split()[0])
        self.selectedProcess = None

        for process in self.listOfProcess:
            if process.getPid() == pid:
                self.selectedProcess = process

        if self.selectedProcess != None:
            libs = self.selectedProcess.getSharedLibs()
            self.dllTreeview.get_model().clear()
            for lib in libs:
                self.dllTreeview.get_model().append(None, [lib.getName(), lib.getVersion(), lib.getPath()])

        else:
            self.log.error(_("A selected process cannot be found !"))

    #+----------------------------------------------
    #| Called when user select a a DLL
    #+----------------------------------------------
    def dllSelected_cb(self, treeview):
        # Retrieve the dll selected
        treeselection = treeview.get_selection()
        (model, pathlist) = treeselection.get_selected_rows()
        iter = model.get_iter(pathlist[0])

        found = False

        self.selectedDLL = None

        if(model.iter_is_valid(iter)):
            libName = model.get_value(iter, 0)
            libVersion = model.get_value(iter, 1)
            libPath = model.get_value(iter, 2)
            found = True

        if found == False:
            self.log.error(_("The selected process cannot be find !"))
            return

        self.dllStore.get_model().clear()

        # search for available prototypes given lib in repository
        for lib in self.repositoryOfSharedLib:
            if lib.getName() == libName:
                self.selectedDLL = lib
                for func in lib.getFunctions():
                    self.dllStore.append_text(func.getPrototype())

    #+----------------------------------------------
    #| Called when user select a prototype
    #+----------------------------------------------
    def prototypeSelected_cb(self, widget):
        if self.selectedProcess == None:
            self.log.warning(_("You have to select a process if you want to capture it"))
            return
        if self.selectedDLL == None:
            self.log.warning(_("You have to select a DLL if you want to capture it"))
            return

        # Updates the list of shared lib
        prototype = self.dllStore.get_active_text()
        self.selectedFunction = None

        for function in self.selectedDLL.getFunctions():
            if function.getPrototype() == prototype:
                self.selectedFunction = function

        if self.selectedFunction == None:
            self.log.error(_("Impossible to retrieve the selected function"))
        else:
            self.log.info(_("Selected function done!"))

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def startCaptureFunction(self, button):
        if self.selectedProcess == None:
            self.log.warning(_("You have to select a process if you want to capture it"))
            return
        if self.selectedDLL == None:
            self.log.warning(_("You have to select a DLL if you want to capture it"))
            return
        if self.selectedFunction == None:
            self.log.warning(_("You have to select a function if you want to capture it"))
            return

        # Create a temporary folder (secure way) <- hihihihi
        tmpFolder = tempfile.mkdtemp()
        self.log.info(_("Temporary folder: {0}").format(tmpFolder))

        parasiteGenerator = ParasiteGenerator(tmpFolder)
        parasiteGenerator.addAnHijackedFunctions(self.selectedFunction)

        parasiteGenerator.writeParasiteToFile()
        parasiteGenerator.compileParasite()
        parasiteGenerator.linkParasite()

        injectorGenerator = InjectorGenerator(tmpFolder, parasiteGenerator)
        injectorGenerator.writeInjectorToFile()
        injectorGenerator.compileInjector()

        poisoner = GOTPoisoner(parasiteGenerator, injectorGenerator)
        poisoner.injectProcess(self.selectedProcess.getPid())

        self.fifoFile = parasiteGenerator.getFifoFile()

        self.aSniffThread = threading.Thread(None, self.sniffThread, None, (), {})
        self.aSniffThread.start()

        self.log.info(_("Starting the capture of [{0}]").format(self.selectedProcess.getPid()))
        self.log.info(_("DLL [{0}]").format(self.selectedDLL.getName()))
        self.log.info(_("Function [{0}]").format(self.selectedFunction.getPrototype()))

    def readFromFifo(self):
        self.fifo = open(self.fifoFile, 'r')
        receivedMessage = self.readline(self.fifo)
        self.log.info(_("FIFO: {0}").format(receivedMessage))
        while (receivedMessage != "STOP\n"):
            self.pktTreestore.append(None, [len(self.packets), "NONE", "NC", receivedMessage, int(time.time())])
            receivedMessage = self.readline(self.fifo)
            self.log.info("FIFO : " + receivedMessage)

    def createFifo(self):
        self.log.info(_("Creating the FIFO file: {0}").format(self.fifoFile))
        # Create the fifo
        try:
            os.mkfifo(self.fifoFile)
        except OSError, e:
            self.log.error(_("Failed to create FIFO: %s") % e)
            return False
        else:
            self.log.info(_("The fifo has been created..."))
            return True

    def readline(self, f):
        s = f.readline()
        while s == "":
            time.sleep(0.0001)
            s = f.readline()
        return s

    def sniffThread(self):
        # Create the receptor (FIFO creation)
        if not self.createFifo():
            self.log.error(_("Cannot execute GOT Poisoning since FIFO file was not created !"))
            return

        # Read from the fifo
        self.readFromFifo()

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def stopCaptureFunction(self, button):
        self.log.debug(_("Stoping the capture..."))

        # We first stop the thread
        if self.aSniffThread != None and self.aSniffThread.isAlive():
            self.aSniffThread._Thread__stop()
        self.aSniffThread = None

        # now we clean everything
        self.log.debug(_("Reading finish, we close the FIFO."))

        # Close and remove fifo
        self.fifo.close()
        os.remove(self.fifoFile)

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
