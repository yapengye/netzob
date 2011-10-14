#!/usr/bin/python
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

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging.config
from threading import Thread

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractActor :
#|     Definition of an actor
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractActor(Thread):
    
    def __init__(self, name, model, isMaster):
        Thread.__init__(self)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.AbstractActor.py')
        self.name = name
        self.model = model
        self.isMaster = isMaster

    

        
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name
    def getModel(self):
        return self.model
    def isMaster(self):
        return self.isMaster
    
    def setModel(self, model):
        self.model = model
    def setName(self, name):
        self.name = name
    
    
