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
from gi.repository import Gtk, Gdk
import gi
from netzob.NetzobMainView import NetzobMainView
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
import sys
import logging
import locale
import gettext

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.DepCheck import DepCheck
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Workspace import Workspace
from netzob.Common.CommandLine import CommandLine
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.LoggingConfiguration import LoggingConfiguration


class NetzobMainController(object):
    """"Netzob main window controller"""

    def __init__(self):
        # Parse command line arguments
        cmdLine = CommandLine()
        cmdLine.parse()
        opts = cmdLine.getOptions()

        # Initialize everything
        self._loadWorkspace(opts)
        self._initLogging()
        self._initResourcesAndLocales()

        # Check dependencies
        if not DepCheck.checkRequiredDependency():
            self.log.fatal("Netzob could not start because some of its" +
                     "required dependencies were not found.")
            sys.exit()

        ### TEST CODE
        # Load thrid project of workspace
        self.currentProject = self.getCurrentWorkspace().getProjects()[2]
        #### TEST CODE

        # Initialize main view
        self.view = NetzobMainView(self)

        # Load all available plugins
        NetzobPlugin.loadPlugins(self)

    def _loadWorkspace(self, opts):
        if opts.workspace == None:
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
        else:
            workspace = opts.workspace

        logging.debug("The workspace: {0}".format(str(workspace)))

        # Load workspace
        self.currentWorkspace = (Workspace.loadWorkspace(workspace))

        # the semi-automatic loading of the workspace has failed (second attempt)
        if self.currentWorkspace == None:
            # we force the creation (or specification) of the workspace
            if not ResourcesConfiguration.initializeResources(True):
                logging.fatal("Error while configuring the resources of Netzob")
                sys.exit()
            workspace = str(ResourcesConfiguration.getWorkspaceFile())
            logging.debug("The workspace: {0}".format(str(workspace)))
            # loading the workspace
            self.currentWorkspace = (Workspace.loadWorkspace(workspace))
            if self.currentWorkspace == None:
                logging.fatal("Stopping the execution (no workspace computed)!")
                sys.exit()

        self.currentProject = self.currentWorkspace.getLastProject()

    def _initResourcesAndLocales(self):
        # Initialiaze gettext
        gettext.bindtextdomain("netzob", ResourcesConfiguration.getLocaleLocation())
        gettext.textdomain("netzob")
        try:
            locale.getlocale()
        except:
            logging.exception("setlocale failed, resetting to C")
            locale.setlocale(locale.LC_ALL, "C")

        # Initialize and verify all resources
        if not ResourcesConfiguration.initializeResources():
            logging.fatal("Error while configuring the resources of Netzob")
            sys.exit()

    def _initLogging(self):
        # Create the logging infrastructure
        LoggingConfiguration().initializeLogging(self.currentWorkspace)
        self.log = logging.getLogger(__name__)
        self.log.info(_("Starting netzob"))

    def run(self):
        self.view.run()
        Gtk.main()

    def getCurrentProject(self):
        return self.currentProject

    def getCurrentWorkspace(self):
        return self.currentWorkspace

    def perspectiveComboBox_changed_cb(self, comboBox):
        iter = comboBox.get_active_iter()
        if iter is not None:
            model = comboBox.get_model()
            newPerspectiveCode = model[iter][0]
        self.view.switchPerspective(newPerspectiveCode)

    def mainWindow_destroy_cb(self, window):
        Gtk.main_quit()
