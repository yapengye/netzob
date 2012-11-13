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
from locale import gettext as _
from gi.repository import Gtk
import gi
import logging
gi.require_version('Gtk', '3.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.UI.Export.Views.TextExportView import TextExportView
from netzob.Export.TextExport import TextExport


#+----------------------------------------------
#| TextExport:
#|     GUI for exporting results in text mode
#+----------------------------------------------
class TextExportController(object):

    #+----------------------------------------------
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.view.symbolTreeview.get_model().clear()
        for symbol in self.netzob.getCurrentProject().getVocabulary().getSymbols():
            iter = self.view.symbolTreeview.get_model().append(None, ["{0}".format(symbol.getID()), "{0} [{1}]".format(symbol.getName(), str(len(symbol.getMessages()))), "{0}".format(symbol.getScore()), '#000000', '#DEEEF0'])

    def clear(self):
        pass

    def kill(self):
        pass

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the main netzob object
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.UI.Export.Controllers.TextExport.py')
        self.model = TextExport(netzob)
        self.view = TextExportView()
        self.initCallbacks()
        self.update()

    def initCallbacks(self):
        self.view.symbolTreeview.connect("changed", self.symbolSelected_cb)

    def symbolSelected_cb(self, selection):
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                symbolID = model.get_value(iter, 0)
                self.showTextDefinition(symbolID)

    def showTextDefinition(self, symbolID):
        if symbolID is None:
            self.log.debug("No selected symbol")
            self.view.textarea.get_buffer().set_text(_("Select a symbol to see its text definition"))
        else:
            textDefinition = self.model.getTextDefinition(symbolID)
            if textDefinition is not None:
                self.view.textarea.get_buffer().set_text("")
                self.view.textarea.get_buffer().insert_with_tags_by_name(self.view.textarea.get_buffer().get_start_iter(), textDefinition, "normalTag")
            else:
                self.view.textarea.get_buffer().set_text(_("No text definition found"))

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.view
