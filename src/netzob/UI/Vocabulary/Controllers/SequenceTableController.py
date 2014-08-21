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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gi.repository import Gdk
import logging

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.SequenceTableView import SequenceTableView
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnFieldController import ContextualMenuOnFieldController
from netzob.Common.SignalsManager import SignalsManager


class SequenceTableController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = SequenceTableView(self)
        self.selectedMessages = []

    @property
    def view(self):
        return self._view

    def getSignalsManager(self):
        return self.vocabularyController.netzob.getSignalsManager()

    def getSelectedMessages(self):
        return self.selectedMessages

    def sequenceTableTreeView_changed_event_cb(self, selection):
        """Callback executed when the user
        clicks on a message in the SequenceTable"""
        if self.vocabularyController.selectedMessagesToMove is not None:
            self.vocabularyController.removePendingMessagesToMove()

        self.selectedMessages = []
        if selection is not None:
            (model, rows) = selection.get_selected_rows()
            for row in rows:
                iter = model.get_iter(row)
                msgID = model[iter][0]
                if msgID is not None:
                    message = self.vocabularyController.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    if message is None:
                        logging.warn("Impossible to retrieve the requested message ({0})".format(msgID))
                    else:
                        self.selectedMessages.append(message)
        self.vocabularyController.sequenceController.updateMessageProperties()

        # Send signals to update toolbar
        nbSelectedMessage = len(self.selectedMessages)
        if nbSelectedMessage == 0:
            self.getSignalsManager().emitSignal(SignalsManager.SIG_MESSAGES_NO_SELECTION)
        elif nbSelectedMessage == 1:
            self.getSignalsManager().emitSignal(SignalsManager.SIG_MESSAGES_SINGLE_SELECTION)
        elif nbSelectedMessage > 1:
            self.getSignalsManager().emitSignal(SignalsManager.SIG_MESSAGES_MULTIPLE_SELECTION)

    def messageListBox_button_press_event_cb(self, box, eventButton):
        self.vocabularyController.setSelectedMessageTable(self.view)

    def closeButton_clicked_cb(self, button):
        self.vocabularyController.removeMessageTable(self.view)

    def sequenceTableTreeView_button_press_event_cb(self, treeview, eventButton):
        # Popup a contextual menu if right click
        self.vocabularyController.setSelectedMessageTable(self.view)
        if eventButton.type == Gdk.EventType.BUTTON_PRESS and eventButton.button == 3:
            x = int(eventButton.x)
            y = int(eventButton.y)
            try:
                (path, treeviewColumn, x, y) = treeview.get_path_at_pos(x, y)
            except:
                # No message selected
                return

            # Retrieve the selected messages
            messages = []
            layer = self._view.getDisplayedObject()
            if layer is None:
                logging.warn("No layer selected, please choose one.")
                return

            (model, paths) = treeview.get_selection().get_selected_rows()
            for path in paths:
                message_id = model[path][0]
                if message_id is not None:
                    message = layer.getMessageByID(message_id)
                    messages.append(message)
                else:
                    return

            # Retrieve the selected field number
            iField = self.view.displayedObject.getExtendedFields()[0].getGlobalIndex()  # Starting displayed field
            for col in treeview.get_columns():
                if col == treeviewColumn:
                    break
                iField += 1
            field = layer.getFieldByIndex(iField)
            if field is None:
                logging.warn("Impossible to retrieve the clicked field!")
                return

            # Popup a contextual menu
            menuController = ContextualMenuOnFieldController(self.vocabularyController, layer, messages, field)
            menuController.run(eventButton)
            return True  # Needed to block remainin signals (especially the 'changed_cb' signal)

    def sequenceTableTreeView_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def sequenceTableTreeView_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)

    def sequenceTableBox_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def sequenceTableBox_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)
