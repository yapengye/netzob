# -*- coding: utf-8 -*-
from netzob.Common.Plugins.Extensions.GlobalMenuExtension import GlobalMenuExtension

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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

class ImportMenuExtension(GlobalMenuExtension):

    def __init__(self, netzob, controller, actionName, menuText, menuStock=None, 
                 menuAccel=None, menuTooltip=None):
        super(GlobalMenuExtension, self).__init__()
        self.netzob = netzob
        self.actionName = actionName
        self.menuText = menuText
        self.menuStock = menuStock 
        self.menuAccel = menuAccel
        self.menuTooltip = menuTooltip
        self.controller = controller
    
    def getUIDefinition(self):
        uiDefinition = \
        """
        <ui>
        <menubar name='MenuBar'>
            <menu action='Project'>
                <menu action='ImportTraces'>
                    <menuitem action='{0}' />
                </menu>
            </menu>
        </menubar>
        </ui>
        """.format(self.actionName)
        return uiDefinition

    def getActions(self):
        actions = [
            ("{0}".format(self.actionName), self.menuStock,
                self.menuText, self.menuAccel, self.menuTooltip, 
                self.executeAction)]
        return actions

    def executeAction(self, widget, data=None):
        self.controller(self.netzob)