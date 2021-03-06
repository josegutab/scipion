# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This modules handles the Project management
"""

import os
import re
import json
import traceback
import time
from collections import OrderedDict
import datetime as dt

import pyworkflow.em as em
import pyworkflow.config as pwconfig
import pyworkflow.protocol as pwprot
import pyworkflow.object as pwobj
import pyworkflow.utils as pwutils
from pyworkflow.mapper import SqliteMapper
from pyworkflow.utils.graph import Graph
from pyworkflow.utils import getFreePort

PROJECT_DBNAME = 'project.sqlite'
PROJECT_LOGS = 'Logs'
PROJECT_RUNS = 'Runs'
PROJECT_TMP = 'Tmp'
PROJECT_UPLOAD = 'Uploads'
PROJECT_SETTINGS = 'settings.sqlite'
PROJECT_CONFIG = '.config'
PROJECT_CONFIG_HOSTS = 'hosts.conf'
PROJECT_CONFIG_PROTOCOLS = 'protocols.conf'

# Regex to get numbering suffix and automatically propose runName
REGEX_NUMBER_ENDING = re.compile('(?P<prefix>.+\D)(?P<number>\d*)\s*$')


        
class Project(object):
    """This class will handle all information 
    related with a Project"""


    def __init__(self, path):
        """Create a project associated with a given path"""
        # To create a Project, a path is required
        self.name = path
        self.shortName = os.path.basename(path)
        self.path = os.path.abspath(path)
        self.pathList = [] # Store all related paths
        self.dbPath = self.__addPath(PROJECT_DBNAME)
        self.logsPath = self.__addPath(PROJECT_LOGS)
        self.runsPath = self.__addPath(PROJECT_RUNS)
        self.tmpPath = self.__addPath(PROJECT_TMP)
        self.uploadPath = self.__addPath(PROJECT_UPLOAD)
        self.settingsPath = self.__addPath(PROJECT_SETTINGS)
        self.configPath = self.__addPath(PROJECT_CONFIG)
        self.runs = None
        self._runsGraph = None
        self._transformGraph = None
        self._sourceGraph = None
        self.address = ''
        self.port = getFreePort()
        # Host configuration
        self._hosts = None
        self._protocolViews = None

    def getObjId(self):
        """ Return the unique id assigned to this project. """
        return os.path.basename(self.path)
    
    def __addPath(self, *paths):
        """Store a path needed for the project"""
        p = self.getPath(*paths)
        self.pathList.append(p)
        return p
        
    def getPath(self, *paths):
        """Return path from the project root"""
        if paths:
            return os.path.join(*paths)
        else:
            return self.path
    
    def getDbPath(self):
        """ Return the path to the sqlite db. """
        return self.dbPath
    
    def getCreationTime(self):
        """ Return the time when the project was created. """
        # In project.create method, the first object inserted
        # in the mapper should be the creation time
        return self.settings.getCreationTime()
    
    def getElapsedTime(self):
        """ Return the time since the project was created. """
        return dt.datetime.now() - self.getCreationTime()
    
    def getLeftTime(self):
        lifeTime = self.settings.getLifeTime()
        
        if lifeTime:
            td = dt.timedelta(days=lifeTime)
            return td - self.getElapsedTime()
        else:
            return None
    
    def setDbPath(self, dbPath):
        """ Set the project db path.
        This function is used when running a protocol where
        a project is loaded but using the protocol own sqlite file.
        """
        # First remove from pathList the old dbPath
        self.pathList.remove(self.dbPath)
        self.dbPath = os.path.abspath(dbPath)
        self.pathList.append(self.dbPath)
    
    def getName(self):
        return self.name
    
    #TODO: maybe it has more sense to use this behaviour
    # for just getName function...
    def getShortName(self):
        return self.shortName
    
    def getTmpPath(self, *paths):
        return self.getPath(PROJECT_TMP, *paths)
    
    def getSettings(self):
        return self.settings
    
    def saveSettings(self):
        # Read only mode
        if not self.isReadOnly():
            self.settings.write()
            
    def createMapper(self, sqliteFn):
        """ Create a new SqliteMapper object and pass as classes dict
        all globas and update with data and protocols from em.
        """
        #TODO: REMOVE THE USE OF globals() here
        classesDict = dict(pwobj.__dict__)
        classesDict.update(em.getProtocols())
        classesDict.update(em.getObjects())
        return SqliteMapper(sqliteFn, classesDict)
    
    def load(self, dbPath=None, hostsConf=None, protocolsConf=None, chdir=True):
        """ Load project data, configuration and settings.
        Params:
            dbPath: the path to the project database.
                If None, use the project.sqlite in the project folder.
            hosts: where to read the host configuration. 
                If None, check if exists in .config/hosts.conf
                or read from ~/.config/scipion/hosts.conf
            settings: where to read the settings.
                If None, use the settings.sqlite in project folder.
        """
        if not os.path.exists(self.path):
            raise Exception("Cannot load project, path doesn't exist: %s" % self.path)
        
        if chdir:
            os.chdir(self.path) #Before doing nothing go to project dir
        
        self._loadDb(dbPath)
        
        self._loadHosts(hostsConf)
        
        self._loadProtocols(protocolsConf)
        
        #FIXME: Handle settings argument here
        
        # It is possible that settings does not exists if 
        # we are loading a project after a Project.setDbName,
        # used when running protocols
        settingsPath = os.path.join(self.path, self.settingsPath) 
        if os.path.exists(settingsPath):
            self.settings = pwconfig.loadSettings(settingsPath)
        else:
            self.settings = None
            
    #---- Helper functions to load different pieces of a project
    def _loadDb(self, dbPath):
        """ Load the mapper from the sqlite file in dbPath. """
        if dbPath is not None:
            self.setDbPath(dbPath)
        
        absDbPath = os.path.join(self.path, self.dbPath)
        if not os.path.exists(absDbPath):
            raise Exception("Project database not found in '%s'" % absDbPath)
        self.mapper = self.createMapper(absDbPath)
        
    def _loadHosts(self, hosts):
        """ Loads hosts configuration from hosts file. """
        # If the host file is not passed as argument...
        projHosts = self.getPath(PROJECT_CONFIG, PROJECT_CONFIG_HOSTS)        
        
        if hosts is None:
            # Try first to read it from the project file .config./hosts.conf
            if os.path.exists(projHosts):
                hostsFile = projHosts
            else:
                localDir = os.path.dirname(os.environ['SCIPION_LOCAL_CONFIG'])
                hostsFile = [os.environ['SCIPION_HOSTS'],
                             os.path.join(localDir, 'hosts.conf')]
        else:
            pwutils.copyFile(hosts, projHosts)
            hostsFile = hosts
            
        self._hosts = pwconfig.loadHostsConf(hostsFile)
        
    def _loadProtocols(self, protocolsConf):
        """ Load protocol configuration from a .conf file. """
        # If the host file is not passed as argument...
        projProtConf = self.getPath(PROJECT_CONFIG, PROJECT_CONFIG_PROTOCOLS)
        
        if protocolsConf is None:
            # Try first to read it from the project file .config/hosts.conf
            if os.path.exists(projProtConf):
                protConf = projProtConf
            else:
                localDir = os.path.dirname(os.environ['SCIPION_LOCAL_CONFIG'])
                protConf = [os.environ['SCIPION_PROTOCOLS'],
                            os.path.join(localDir, 'protocols.conf')]
        else:
            pwutils.copyFile(protocolsConf, projProtConf)
            protConf = protocolsConf
          
        self._protocolViews = pwconfig.loadProtocolsConf(protConf)
        
        
    def getHostNames(self):
        """ Return the list of host name in the project. """
        return self._hosts.keys()
    
    def getHostConfig(self, hostName):
        if hostName in self._hosts:
            hostKey = hostName
        else:
            hostKey = self._hosts.keys()[0]
            print "PROJECT: Warning, protocol host '%s' not found." % hostName
            print "         Using '%s' instead." % hostKey
            
        return self._hosts[hostKey]
    
    def getProtocolViews(self):
        return self._protocolViews.keys()
    
    def getCurrentProtocolView(self):
        """ Select the view that is currently selected.
        Read from the settings the last selected view
        and get the information from the self._protocolViews dict.
        """
        currentView = self.settings.getProtocolView()
        if currentView in self._protocolViews:
            viewKey = currentView
        else:
            viewKey = self._protocolViews.keys()[0]
            self.settings.setProtocolView(viewKey)
            print "PROJECT: Warning, protocol view '%s' not found." % currentView
            print "         Using '%s' instead."  % viewKey
        
        return self._protocolViews[viewKey]          
        
    def create(self, runsView=1, readOnly=False, hostsConf=None, protocolsConf=None):
        """Prepare all required paths and files to create a new project.
        Params:
         hosts: a list of configuration hosts associated to this projects (class ExecutionHostConfig)
        """
        # Create project path if not exists
        pwutils.path.makePath(self.path)
        os.chdir(self.path) #Before doing nothing go to project dir
        self._cleanData()
        print "Creating project at: ", os.path.abspath(self.dbPath)
        # Create db throught the mapper
        self.mapper = self.createMapper(self.dbPath)
        creation = pwobj.String(objName='CreationTime') # Store creation time
        creation.set(dt.datetime.now())
        self.mapper.insert(creation)
        self.mapper.commit()
        # Load settings from .conf files and write .sqlite
        self.settings = pwconfig.ProjectSettings()
        self.settings.setRunsView(runsView)
        self.settings.setReadOnly(readOnly)
        self.settings.write(self.settingsPath)
        # Create other paths inside project
        for p in self.pathList:
            pwutils.path.makePath(p)
                
        self._loadHosts(hostsConf)
        
        self._loadProtocols(protocolsConf)
        
    def _cleanData(self):
        """Clean all project data"""
        pwutils.path.cleanPath(*self.pathList)      
                
    def launchProtocol(self, protocol, wait=False):
        """ In this function the action of launching a protocol
        will be initiated. Actions done here are:
        1. Store the protocol and assign name and working dir
        2. Create the working dir and also the protocol independent db
        3. Call the launch method in protocol.job to handle submition: mpi, thread, queue,
        and also take care if the execution is remotely."""

        if not protocol.isInteractive():
            self._checkModificationAllowed([protocol], 'Cannot RE-LAUNCH protocol')
        protocol.setStatus(pwprot.STATUS_LAUNCHED)
        self._setupProtocol(protocol)
        #protocol.setMapper(self.mapper) # mapper is used in makePathAndClean
        protocol.makePathsAndClean() # Create working dir if necessary
        self.mapper.commit()
        
        # Prepare a separate db for this run
        # NOTE: now we are simply copying the entire project db, this can be changed later
        # to only create a subset of the db need for the run
        pwutils.path.copyFile(self.dbPath, protocol.getDbPath())
        
        # Launch the protocol, the jobId should be set after this call
        pwprot.launch(protocol, wait)
        
        # Commit changes
        if wait: # This is only useful for launching tests...
            self._updateProtocol(protocol)
        else:
            self.mapper.store(protocol)
        self.mapper.commit()
        
    def _updateProtocol(self, protocol, tries=0):
        if not self.isReadOnly():
            try:
                # Backup the values of 'jobId', 'label' and 'comment'
                # to be restored after the .copy
                jobId = protocol.getJobId() 
                label = protocol.getObjLabel()
                comment = protocol.getObjComment()
                
                #TODO: when launching remote protocols, the db should be retrieved 
                # in a different way.

                #join(protocol.getHostConfig().getHostPath(), protocol.getDbPath())
                prot2 = pwprot.getProtocolFromDb(self.path, protocol.getDbPath(), 
                                          protocol.getObjId())

                # Copy is only working for db restored objects
                protocol.setMapper(self.mapper)
                protocol.copy(prot2, copyId=False)
                # Restore backup values
                protocol.setJobId(jobId)
                protocol.setObjLabel(label)
                protocol.setObjComment(comment)
                
                self.mapper.store(protocol)
            
            except Exception, ex:
                print "Error trying to update protocol: %s(jobId=%s)\n ERROR: %s, tries=%d" % (protocol.getObjName(), jobId, ex, tries)
                if tries == 3: # 3 tries have been failed
                    traceback.print_exc()
                    # If any problem happens, the protocol will be marked wih a status fail
                    protocol.setFailed(str(ex))
                    self.mapper.store(protocol)
                else:
                    time.sleep(0.5)
                    self._updateProtocol(protocol, tries+1)
        
    def stopProtocol(self, protocol):
        """ Stop a running protocol """
        try:
            pwprot.stop(protocol)
        except Exception:
            raise
        finally:
            protocol.setAborted()
            self._storeProtocol(protocol)
        
    def continueProtocol(self, protocol):
        """ This function should be called 
        to mark a protocol that have an interactive step
        waiting for approval that can continue
        """
        protocol.continueFromInteractive()
        self.launchProtocol(protocol)
        
    def __protocolInList(self, prot, protocols):
        """ Check if a protocol is in a list comparing the ids. """
        for p in protocols:
            if p.getObjId() == prot.getObjId():
                return True
        return False
    
    def __validDependency(self, prot, child, protocols):
        """ Check if the given child is a true dependency of the protocol
        in order to avoid any modification.
        """
        return (not self.__protocolInList(child, protocols) and
                not child.isSaved()) 
        
    
    def _getProtocolsDependencies(self, protocols):
        error = ''
        for prot in protocols:
            node = self.getRunsGraph().getNode(prot.strId())
            if node:
                childs = [node.run for node in node.getChilds() if self.__validDependency(prot, node.run, protocols)]
                if childs:
                    deps = [' ' + c.getRunName() for c in childs]
                    error += '\n *%s* is referenced from:\n   - ' % prot.getRunName()
                    error += '\n   - '.join(deps) 
        return error
        
    
    def _checkProtocolsDependencies(self, protocols, msg):
        """ Check if the protocols have depencies.
        This method is used before delete or save protocols to be sure
        it is not referenced from other runs. (an Exception is raised)
        Params:
             protocols: protocol list to be analyzed.
             msg: String message to be prefixed to Exception error.
        """
        # Check if the protocol have any dependencies
        error = self._getProtocolsDependencies(protocols)
        if error:
            raise Exception(msg + error)
        
    def _checkModificationAllowed(self, protocols, msg):
        """ Check if any modification operation is allowed for
        this group of protocols. 
        """
        if self.isReadOnly():
            raise Exception(msg + " Running in READ-ONLY mode.")
        
        self._checkProtocolsDependencies(protocols, msg)
        
    def deleteProtocol(self, *protocols):
        self._checkModificationAllowed(protocols, 'Cannot DELETE protocols')
        
        for prot in protocols:
            self.mapper.delete(prot) # Delete from database
            wd = prot.workingDir.get()
            
            if wd.startswith(PROJECT_RUNS):
                pwutils.path.cleanPath(wd)
            else:
                print "Error path: ", wd 
      
        self.mapper.commit()     
        
    def __setProtocolLabel(self, newProt):
        """ Set a readable label to a newly created protocol.
        We will try to find another existing protocol of the 
        same class and set the label from it.
        """
        prevLabel = None # protocol with same class as newProt
        newProtClass = newProt.getClass()
        
        for prot in self.getRuns(iterate=True, refresh=False):
            if newProtClass == prot.getClass():
                prevLabel = prot.getObjLabel().strip()
                
        if prevLabel: 
            numberSuffix = 2
            m = REGEX_NUMBER_ENDING.match(prevLabel)
            if m and m.groupdict()['number']:
                numberSuffix = int(m.groupdict()['number']) + 1
                prevLabel = m.groupdict()['prefix'].strip()
            protLabel =  prevLabel + ' %s' % numberSuffix
        else:
            protLabel = newProt.getClassLabel()
            
        newProt.setObjLabel(protLabel)
        
    def newProtocol(self, protocolClass, **kwargs):
        """ Create a new protocol from a given class. """
        newProt = protocolClass(project=self, **kwargs)
        # Only set a default label to the protocol if is was not
        # set throught the kwargs
        if not newProt.getObjLabel():
            self.__setProtocolLabel(newProt)
        
        newProt.setMapper(self.mapper)
        newProt.setProject(self)
        
        return newProt
                      
    def __getIOMatches(self, node, childNode):
        """ Check if some output of node is used as input in childNode.
        Return the list of attribute names that matches.
        Used from self.copyProtocol
        """
        matches = []
        for iKey, iAttr in childNode.run.iterInputAttributes():
            value = iAttr.get()
            if value is None:
                if iAttr.getObjValue() is node.run:
                    oKey = iAttr.getExtendedValue()
                    matches.append((oKey, iKey))
            else:
                for oKey, oAttr in node.run.iterOutputAttributes(em.EMObject):
                    if oAttr is iAttr.get():
                        matches.append((oKey, iKey))
                
        
        return matches                    
        
    def copyProtocol(self, protocol):
        """ Make a copy of the protocol, return a new one with copied values. """
        result = None
        
        if isinstance(protocol, pwprot.Protocol):
            newProt = self.newProtocol(protocol.getClass())
            newProt.copyDefinitionAttributes(protocol)
            result = newProt
    
        elif isinstance(protocol, list):
            # Handle the copy of a list of protocols
            # for this case we need to update the references of input/outputs
            newDict = {}
                        
            for prot in protocol:
                newProt = self.newProtocol(prot.getClass())
                newProt.copyDefinitionAttributes(prot)
                newDict[prot.getObjId()] = newProt
                self.saveProtocol(newProt)
                         
            g = self.getRunsGraph(refresh=False)
            
            for prot in protocol:
                node = g.getNode(prot.strId())
                newProt = newDict[prot.getObjId()]
                
                for childNode in node.getChilds():
                    newChildProt = newDict.get(childNode.run.getObjId(), None)
                    
                    if newChildProt:
                        # Get the matches between outputs/inputs of node and childNode
                        matches = self.__getIOMatches(node, childNode)
                        # For each match, set the pointer and the extend attribute
                        # to reproduce the dependencies in the new workflow
                        for oKey, iKey in matches:
                            childPointer = getattr(newChildProt, iKey)
                            childPointer.set(newProt)
                            childPointer.setExtendedAttribute(oKey)
                        self.mapper.store(newChildProt)  

            self.mapper.commit()
        else:
            raise Exception("Project.copyProtocol: invalid input protocol type '%s'." % type(protocol))
    
        return result
    
    def exportProtocols(self, protocols, filename):
        """ Create a text json file with the info
        to import the workflow into another project.
        This methods is very similar to copyProtocol
        Params:
            protocols: a list of protocols to export.
            filename: the filename where to write the workflow.
        
        """
        # Handle the copy of a list of protocols
        # for this case we need to update the references of input/outputs
        newDict = OrderedDict()
                    
        for prot in protocols:
            newDict[prot.getObjId()] = prot.getDefinitionDict()
                     
        g = self.getRunsGraph(refresh=False)
        
        for prot in protocols:
            protId = prot.getObjId()
            node = g.getNode(prot.strId())
            
            for childNode in node.getChilds():
                childId = childNode.run.getObjId()
                if childId in newDict:
                    childDict = newDict[childId]
                    # Get the matches between outputs/inputs of node and childNode
                    matches = self.__getIOMatches(node, childNode)
                    for oKey, iKey in matches:
                        childDict[iKey] = '%s.%s%s' % (protId, pwobj.Pointer.EXTENDED_ATTR, oKey)
                      
        f = open(filename, 'w')  
        
        f.write(json.dumps(list(newDict.values()), 
                           indent=4, separators=(',', ': ')) + '\n')
        f.close()
        
    def loadProtocols(self, filename=None, jsonStr=None):
        """ Load protocols generated in the same format as self.exportProtocols.
        Params:
            filename: the path of the file where to read the workflow.
            jsonStr: read the protocols from a string instead of file.
        Note: either filename or jsonStr should be not None.
        """
        f = open(filename)
        protocolsList = json.load(f)
        
        emProtocols = em.getProtocols()
        newDict = {}
        
        # First iteration: create all protocols and setup parameters
        for protDict in protocolsList:
            protClassName = protDict['object.className']
            protId = protDict['object.id']
            protClass = emProtocols.get(protClassName, None)
            
            if protClass is None:
                print "ERROR: protocol class name '%s' not found" % protClassName
            else:
                prot = self.newProtocol(protClass, 
                                        objLabel=protDict.get('object.label', None),
                                        objComment=protDict.get('object.comment', None))
                newDict[protId] = prot
                for paramName, attr in prot.iterDefinitionAttributes():
                    if not attr.isPointer():
                        if paramName in protDict:
                            attr.set(protDict[paramName])
                self.saveProtocol(prot)
        # Second iteration: update pointers values
        for protDict in protocolsList:
            protId = protDict['object.id']
            
            if protId in newDict:
                prot = newDict[protId]
                for paramName, attr in prot.iterDefinitionAttributes():
                        if attr.isPointer() and paramName in protDict:
                            parts = protDict[paramName].split('.')
                            if parts[0] in newDict:
                                attr.set(newDict[parts[0]]) # set pointer to correct created protocol
                                if len(parts) > 1: # set extended attribute part
                                    attr._extended.set(parts[1])
                            else:
                                attr.set(None)
                self.mapper.store(prot)
            
        f.close()
        self.mapper.commit()
            
    
    def saveProtocol(self, protocol):
        self._checkModificationAllowed([protocol], 'Cannot SAVE protocol')

        if protocol.isRunning() or protocol.isFinished() or protocol.isLaunched():
            raise Exception('Cannot SAVE a protocol that is %s. Copy it instead.' % protocol.getStatus())

        
        protocol.setStatus(pwprot.STATUS_SAVED)
        if protocol.hasObjId():
            self._storeProtocol(protocol)
        else:
            self._setupProtocol(protocol)
                
    def getProtocol(self, protId):
        protocol = self.mapper.selectById(protId)
        
        if not isinstance(protocol, pwprot.Protocol):
            raise Exception('>>> ERROR: Invalid protocol id: %d' % protId)
        
        self._setProtocolMapper(protocol)
        
        return protocol
    
    def getProtocolsByClass(self, className):
        return self.mapper.selectByClass(className)
            
    def getObject(self, objId):
        """ Retrieve an object from the db given its id. """
        return self.mapper.selectById(objId)
        
    def _setHostConfig(self, protocol):
        """ Set the appropiate host config to the protocol
        give its value of 'hostname'
        """
        hostName = protocol.getHostName()
        hostConfig = self.getHostConfig(hostName)
        protocol.setHostConfig(hostConfig)
    
    def _storeProtocol(self, protocol):
        # Read only mode
        if not self.isReadOnly():
            self.mapper.store(protocol)
            self.mapper.commit()
    
    def _setProtocolMapper(self, protocol):
        """ Set the project and mapper to the protocol. """
        protocol.setProject(self)
        protocol.setMapper(self.mapper)
        self._setHostConfig(protocol)
        
    def _setupProtocol(self, protocol):
        """Insert a new protocol instance in the database"""
        
        # Read only mode
        if not self.isReadOnly():
        
            self._storeProtocol(protocol) # Store first to get a proper id
            # Set important properties of the protocol
            workingDir = "%06d_%s" % (protocol.getObjId(), protocol.getClassName())
            self._setProtocolMapper(protocol)
            #print protocol.strId(), protocol.getProject().getName()
            #protocol.setName(name)
            protocol.setWorkingDir(self.getPath(PROJECT_RUNS, workingDir))
            # Update with changes
            self._storeProtocol(protocol)
            
    def getRuns(self, iterate=False, refresh=True):
        """ Return the existing protocol runs in the project. 
        """
        if self.runs is None or refresh:
            # Close db open connections to db files
            self.runs = self.mapper.selectByClass("Protocol", iterate=False)
            for r in self.runs:
                self._setProtocolMapper(r)
                # Update nodes that are running and are not invoked by other protocols
                if r.isActive():
                    if not r.isChild():
                        self._updateProtocol(r)
            self.mapper.commit()
        
        return self.runs
    
    def iterSubclasses(self, classesName, objectFilter=None):
        """ Retrieve all objects from the project that are instances
            of any of the classes in classesName list.
        Params: 
            classesName: String with commas separated values of classes name. 
            objectFilter: a filter function to discard some of the retrieved objects."""
        for objClass in classesName.split(","):
            for obj in self.mapper.selectByClass(objClass.strip(), iterate=True, objectFilter=objectFilter):
                yield obj
    
    def getRunsGraph(self, refresh=True):
        """ Build a graph taking into account the dependencies between
        different runs, ie. which outputs serves as inputs of other protocols. 
        """
        if refresh or self._runsGraph is None:
            outputDict = {} # Store the output dict
            runs = [r for r in self.getRuns(refresh=refresh) if not r.isChild()]
            g = pwutils.graph.Graph(rootName='PROJECT')
            
            for r in runs:
                n = g.createNode(r.strId())
                n.run = r
                n.setLabel(r.getRunName())
                outputDict[r.getObjId()] = n
                for _, attr in r.iterOutputAttributes(em.EMObject):
                    outputDict[attr.getObjId()] = n # mark this output as produced by r
                
            def _checkInputAttr(node, pointed):
                """ Check if an attr is registered as output"""
                if pointed is not None:
                    pointedId = pointed.getObjId()
                    
                    if pointedId in outputDict:
                        parentNode = outputDict[pointedId]
                        if parentNode is node:
                            print "WARNING: Found a cyclic dependence from node %s to itself, problably a bug. " % pointedId
                        else:
                            parentNode.addChild(node)
                            return True
                return False
                
            for r in runs:
                node = g.getNode(r.strId())
                for _, attr in r.iterInputAttributes():
                    if attr.hasValue():
                        pointed = attr.getObjValue()
                        # Only checking pointed object and its parent, if more levels
                        # we need to go up to get the correct dependencies
                        if not _checkInputAttr(node, pointed):
                            parent = self.mapper.getParent(pointed)
                            _checkInputAttr(node, parent)
            rootNode = g.getRoot()
            rootNode.run = None
            rootNode.label = "PROJECT"
            
            for n in g.getNodes():
                if n.isRoot() and not n is rootNode:
                    rootNode.addChild(n)
            self._runsGraph = g
            
        return self._runsGraph
    
    def _getRelationGraph(self, relation=em.RELATION_SOURCE, refresh=False):
        """ Retrieve objects produced as outputs and
        make a graph taking into account the SOURCE relation. """
        relations = self.mapper.getRelationsByName(relation)
        g = pwutils.graph.Graph(rootName='PROJECT')
        root = g.getRoot()
        root.object = None
        runs = self.getRuns(refresh=refresh)
        
        for r in runs:
            for _, attr in r.iterOutputAttributes(em.EMObject):
                node = g.createNode(attr.strId(), attr.getNameId())
                node.object = attr                
        
        for rel in relations:
            pid = str(rel['object_parent_id'])
            parent = g.getNode(pid)
            if not parent:
                print "error, parent none: ", pid
            else:
                cid = str(rel['object_child_id'])
                child = g.getNode(cid)
                if not child:
                    print "error, child none: ", cid, " label: ", 
                    print "   parent: ", pid 
                else:
                    parent.addChild(child)
            
        for n in g.getNodes():
            if n.isRoot() and not n is root:
                root.addChild(n)
            
        return g
    
    def getSourceChilds(self, obj):
        """ Return all the objects have used obj
        as a source.
        """
        return self.mapper.getRelationChilds(em.RELATION_SOURCE, obj)
    
    def getSourceParents(self, obj):
        """ Return all the objects that are SOURCE of this object.
        """
        return self.mapper.getRelationParents(em.RELATION_SOURCE, obj)
    
    def getTransformGraph(self, refresh=False):
        """ Get the graph from the TRASNFORM relation. """
        if refresh or not self._transformGraph:
            self._transformGraph = self._getRelationGraph(em.RELATION_TRANSFORM, refresh)
            
        return self._transformGraph
            
    def getSourceGraph(self, refresh=False):
        """ Get the graph from the SOURCE relation. """
        if refresh or not self._sourceGraph:
            self._sourceGraph = self._getRelationGraph(em.RELATION_SOURCE, refresh)
            
        return self._sourceGraph
                
    def getRelatedObjects(self, relation, obj, direction=em.RELATION_CHILDS):
        """ Get all objects related to obj by a give relation.
        Params:
            relation: the relation name to search for.
            obj: object from which the relation will be search,
                actually not only this, but all other objects connected
                to this one by the RELATION_TRANSFORM.
            direction: this say if search for childs or parents in the relation.
        """
        graph = self.getTransformGraph()
        relations = self.mapper.getRelationsByName(relation)
        connection = self._getConnectedObjects(obj, graph)
        objects = []
        
        for rel in relations:
            pid = str(rel['object_parent_id'])
            parent = connection.get(pid, None)
            if parent:
                cid = str(rel['object_child_id'])
                child = graph.getNode(cid).object
                objects.append(child)
                
        return objects
    
    def _getConnectedObjects(self, obj, graph):
        """ Given a TRANSFORM graph, return the elements that
        are connected to an object, either childs, ancestors or siblings. 
        """
        n = graph.getNode(obj.strId())
        # Get the oldest ancestor of a node, before 
        # reaching the root node
        while not n.getParent().isRoot():
            n = n.getParent()
            
        connection = {}
        for node in n.iterChilds():
            connection[node.object.strId()] = node.object
        
        return connection
    
    def isReadOnly(self):
        return self.settings.getReadOnly()
    
    def setReadOnly(self, value):
        self.settings.setReadOnly(value)

        
