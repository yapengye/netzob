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
import logging
import time
from gi.repository import GObject
import os

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Inference.Grammar.Oracles.NetworkOracle import NetworkOracle
from netzob.Common.MMSTD.Dictionary.Memory import Memory


#+----------------------------------------------
#| LearningAlgorithm:
#|    Abstract class which provides to his children
#| the necessary functions to learn
#+----------------------------------------------
class LearningAlgorithm(object):

    def __init__(self, dictionary, inputDictionary, communicationChannel, resetScript, callbackFunction, cb_hypotheticalAutomaton, cache):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.LearningAlgorithm.py')
        self.dictionary = dictionary
        self.inputDictionary = inputDictionary
        self.communicationChannel = communicationChannel
        self.inferedAutomata = None
        self.resetScript = resetScript
        self.submitedQueries = []
        self.cache = cache

        self.callbackFunction = callbackFunction
        self.cb_hypotheticalAutomaton = cb_hypotheticalAutomaton

    def getInputDictionary(self):
        return self.inputDictionary

    def attachStatusCallBack(self, callbackFunction):
        self.callbackFunction = callbackFunction

    def learn(self):
        self.log.error("The LearningAlgorithm class doesn't support 'learn'.")
        raise NotImplementedError("The LearningAlgorithm class doesn't support 'learn'.")

    def getSubmitedQueries(self):
        return self.submitedQueries

    def submitQuery(self, query):
        # Verify the request is not in the cache
        cachedValue = self.cache.getCachedResult(query)
        if cachedValue != None:
            self.log.info("The MQ is cached, result obtained : " + str(query) + " = " + str(cachedValue) + ".")
            return cachedValue[len(cachedValue) - 1]

        # TODO : must be UPGRADED
        # WARNING
        if self.resetScript != "":
            self.log.info("Reseting the oracle by executing script : " + self.resetScript)
            os.system("sh " + self.resetScript)

        self.log.info("Submit the following query : " + str(query))

        isMaster = not self.communicationChannel.isServer()

        # transform the query into a MMSTD
        mmstd = query.toMMSTD(self.dictionary, isMaster)

        self.cb_hypotheticalAutomaton(mmstd)
        time.sleep(10)
        self.log.info("The current experimentation has generated the following MMSTD :")
        self.log.debug(mmstd.getDotCode())

        # create an oracle for this MMSTD
        oracle = NetworkOracle(self.communicationChannel, isMaster)

        # start the oracle with the MMSTD
        oracle.setMMSTD(mmstd)
        oracle.start()

        # wait it has finished
        self.log.info("Waiting for the oracle to finish")
        while oracle.isAlive():
            time.sleep(0.01)
        self.log.info("The oracle has finished !")

        # stop the oracle and retrieve the query
        oracle.stop()

        self.log.info("Close (again) the server")
        self.communicationChannel.close()

        if isMaster:
            resultQuery = oracle.getResults()
            tmpResultQuery = oracle.getGeneratedOutputSymbols()
        else:
            resultQuery = oracle.getGeneratedInputSymbols()
            tmpResultQuery = oracle.getGeneratedInputSymbols()

        self.log.info("---------------------------------------------")
        self.log.info("RESUMONS UN PETIT PEU TOUT CA :")
        self.log.info("---------------------------------------------")
        self.log.info("SUBMITED : ")
        self.log.info(str(query))
        self.log.info("---------------------------------------------")
        self.log.info("RESULT :")
        self.log.info("---------------------------------------------")
        self.log.info("+ getResults :")
        self.log.info(str(resultQuery))
        self.log.info("---------------------------------------------")
        self.log.info("+ getGeneratedInputSymbols :")
        self.log.info(str(oracle.getGeneratedInputSymbols()))
        self.log.info("---------------------------------------------")
        self.log.info("+ getGeneratedOutputSymbols :")
        self.log.info(str(oracle.getGeneratedOutputSymbols()))
        self.log.info("---------------------------------------------")
        self.log.info("The following query has been computed : " + str(resultQuery))

        # Register this query and the associated response
        self.submitedQueries.append([query, resultQuery])

        # return only the last result
        if len(resultQuery) > 0:
            # Execute the call back function
            GObject.idle_add(self.callbackFunction, query, tmpResultQuery)
            result = resultQuery[len(resultQuery) - 1]
            self.cache.cacheResult(query, resultQuery)

            self.cache.dumpCache()

            return result
        else:
            # Execute the call back function
            GObject.idle_add(self.callbackFunction, query, "OUPS")
            self.cache.cacheResult(query, resultQuery)
            return resultQuery

    def getInferedAutomata(self):
        return self.inferedAutomata
