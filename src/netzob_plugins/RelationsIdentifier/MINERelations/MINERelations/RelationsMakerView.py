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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
import logging

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class RelationsMakerView(object):
    """RelationsMakeView:
            GUI for creating relations based on results of MINE.
    """

    GLADE_FILENAME = "RelationsMakerDialog.glade"

    def __init__(self, controller, netzob, relations):
        """Constructor of RelationsMakeView"""
        self.relations = relations
        self.controller = controller

        # Import and add configuration widget
        self.builderConfWidget = Gtk.Builder()

        gladePath = os.path.join(netzob.getPluginStaticResourcesPath(), "ui", RelationsMakerView.GLADE_FILENAME)
        self.builderConfWidget.add_from_file(gladePath)

        self._getObjects(self.builderConfWidget, ["dialog", "relationsListStore", "relationsTreeView"])
        self.builderConfWidget.connect_signals(self.controller)

        # Fullfill the relations liststore with computed relations
        for (symbolName, rels) in relations.items():
            for rel in rels:
                line = self.relationsListStore.append()

                strStartType = "Value of"
                if rel['x_attribute'] == "s":
                    strStartType = "Size of"

                strEndType = "Value of"
                if rel['y_attribute'] == "s":
                    strEndType = "Size of"
                self.relationsListStore.set(line, 0, str(rel['id']))
                self.relationsListStore.set(line, 1, rel['relation_type'])
                self.relationsListStore.set(line, 2, strStartType + " " + rel['x_field'].getName() + "@" + rel['x_field'].getSymbol().getName())
                self.relationsListStore.set(line, 3, strEndType + " " + rel['y_field'].getName() + "@" + rel['y_field'].getSymbol().getName())
                self.relationsListStore.set(line, 4, float(rel['mic']))
                self.relationsListStore.set(line, 5, float(rel['pearson']))

    def show(self):
        self.dialog.show()

    def destroy(self):
        self.dialog.destroy()

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def getSelectedRelation(self):
        model, iter = self.relationsTreeView.get_selection().get_selected()
        idRelation = None
        if iter is not None:
            idRelation = model[iter][0]

        if idRelation == None:
            logging.info("No relation selected")
            return None

        for (symbolName, rels) in self.relations.items():
            for rel in rels:
                if str(rel['id']) == str(idRelation):
                    return rel
        logging.warning("Impossible to retrieve the requested relation")
        return None
