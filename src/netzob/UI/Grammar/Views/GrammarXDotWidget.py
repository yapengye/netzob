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
#| Standard library imports
#+----------------------------------------------
from gettext import gettext as _


#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------
from netzob.Simulator.XDotWidget import XDotWidget

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------


#+----------------------------------------------
#| Configuration of the logger
#+----------------------------------------------


#+----------------------------------------------
#| XDotWidget:
#|    Integrates an XDot graph in a PyGtk window
#+----------------------------------------------
class GrammarXDotWidget(XDotWidget):

    def __init__(self):
        XDotWidget.__init__(self)
        self.connect('clicked', self.on_click_action)

    def on_click_action(self, object, url, event):
        if event.button == 3:
            print url

    def drawAutomata(self, automata):
        self.set_dotcode(automata.getDotCode())
        self.zoom_to_fit()