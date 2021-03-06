#!/usr/bin/env python
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
Data-oriented view of the project objects.
"""

import Tkinter as tk
import ttk
import tkFont

import pyworkflow.protocol.protocol as prot
from pyworkflow.em import findViewers, DESKTOP_TKINTER
from pyworkflow.utils.graph import Graph
from pyworkflow.utils.properties import Message, Icon, Color

import pyworkflow.gui as gui
from pyworkflow.gui.tree import Tree
from pyworkflow.gui.dialog import EditObjectDialog
from pyworkflow.gui.text import TaggedText
from pyworkflow.gui import Canvas, RoundedTextBox
from pyworkflow.gui.graph import LevelTree
from pyworkflow.gui.form import getObjectLabel


ACTION_EDIT = Message.LABEL_EDIT
ACTION_COPY = Message.LABEL_COPY
ACTION_DELETE = Message.LABEL_DELETE
ACTION_REFRESH = Message.LABEL_REFRESH
ACTION_STEPS = Message.LABEL_BROWSE
ACTION_TREE = Message.LABEL_TREE
ACTION_LIST = Message.LABEL_LIST
ACTION_STOP = Message.LABEL_STOP
ACTION_DEFAULT = Message.LABEL_DEFAULT
ACTION_CONTINUE = Message.LABEL_CONTINUE
ACTION_RESULTS = Message.LABEL_ANALYZE

RUNS_TREE = Icon.RUNS_TREE
RUNS_LIST = Icon.RUNS_LIST
 
ActionIcons = {
    ACTION_EDIT: Icon.ACTION_EDIT , 
    ACTION_COPY: Icon.ACTION_COPY ,
    ACTION_DELETE:  Icon.ACTION_DELETE,
    ACTION_REFRESH:  Icon.ACTION_REFRESH,
    ACTION_STEPS:  Icon.ACTION_STEPS,
    ACTION_TREE:  None, # should be set
    ACTION_LIST:  Icon.ACTION_LIST,
    ACTION_STOP: Icon.ACTION_STOP,
    ACTION_CONTINUE: Icon.ACTION_CONTINUE,
    ACTION_RESULTS: Icon.ACTION_RESULTS,
               }

STATUS_COLORS = {
               prot.STATUS_SAVED: '#D9F1FA',
               prot.STATUS_LAUNCHED: '#D9F1FA',
               prot.STATUS_RUNNING: '#FCCE62',
               prot.STATUS_FINISHED: '#D2F5CB',
               prot.STATUS_FAILED: '#F5CCCB',
               prot.STATUS_INTERACTIVE: '#F3F5CB',
               prot.STATUS_ABORTED: '#F5CCCB',
               #prot.STATUS_SAVED: '#124EB0',
               }

def populateTree(tree, elements, parentId=''):
    for node in elements:
        if hasattr(node, 'count'):
            t = node.getName()
            if node.count:
                t += ' (%d)' % node.count
            node.nodeId = tree.insert(parentId, 'end', node.getName(), text=t)
            populateTree(tree, node.getChilds(), node.nodeId)
            if node.count:
                tree.see(node.nodeId)
                tree.item(node.nodeId, tags='non-empty')

    
class ProjectDataView(tk.Frame):
    def __init__(self, parent, windows, **args):
        tk.Frame.__init__(self, parent, **args)
        # Load global configuration
        self.windows = windows
        self.project = windows.project
        self.root = windows.root
        self.getImage = windows.getImage
        self.protCfg = windows.protCfg
        self.icon = windows.icon
        self.settings = windows.getSettings()
        self.showGraph = self.settings.getRunsView()
        self.style = ttk.Style()
        
        self.root.bind("<F5>", self.refreshData)
        self.__autoRefresh = None
        self.__autoRefreshCounter = 3 # start by 3 secs  

        self._dataGraph = windows.project.getSourceGraph(True)

        c = self._createContent()
        
        gui.configureWeigths(self)
        c.grid(row=0, column=0, sticky='news')
        
    def _createContent(self):
        """ Create the Protocols View for the Project.
        It has two panes:
            Left: containing the Protocol classes tree
            Right: containing the Runs list
        """
        p = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg='white')
        
        # Left pane, contains Data tree
        leftFrame = tk.Frame(p, bg='white')
        bgColor = '#eaebec'
        self._createDataTree(leftFrame, bgColor)
        gui.configureWeigths(leftFrame)
        
        # Right pane
        rightFrame = tk.Frame(p, bg='white')
        rightFrame.columnconfigure(0, weight=1)
        rightFrame.rowconfigure(1, weight=1)
        #rightFrame.rowconfigure(0, minsize=label.winfo_reqheight())
        self._fillRightPane(rightFrame)

        # Add sub-windows to PanedWindows
        p.add(leftFrame, padx=5, pady=5)
        p.add(rightFrame, padx=5, pady=5)
        p.paneconfig(leftFrame, minsize=300)
        p.paneconfig(rightFrame, minsize=400)        
        
        return p
    
    def _createDataTree(self, parent, bgColor):
        """Create a tree on the left panel to store how 
        many object are from each type and the hierarchy.
        """
        self.style.configure("W.Treeview", background=Color.LIGHT_GREY_COLOR, borderwidth=0)
        self.dataTree = Tree(parent, show='tree', style='W.Treeview')
        self.dataTree.column('#0', minwidth=300)
        self.dataTree.tag_configure('protocol', image=self.getImage('python_file.gif'))
        self.dataTree.tag_configure('protocol_base', image=self.getImage('class_obj.gif'))
        f = tkFont.Font(family='helvetica', size='10', weight='bold')
        self.dataTree.tag_configure('non-empty', font=f)
        self.dataTree.grid(row=0, column=0, sticky='news')
                        
        # Program automatic refresh
        self.dataTree.after(3000, self._automaticRefreshData)
        
        self._updateDataTree()
        
        
    def _updateDataTree(self):
            
        def createClassNode(classObj):
            """ Add the object class to hierarchy and 
            any needed subclass. """
            className = classObj.__name__
            classNode = classesGraph.getNode(className)
            
            if not classNode:
                classNode = classesGraph.createNode(className)
                if className != 'EMObject' and classObj.__bases__:
                    baseClass = classObj.__bases__[0]
                    for b in classObj.__bases__:
                        if b.__name__ == 'EMObject':
                            baseClass = b
                            break
                    parent = createClassNode(baseClass)
                    parent.addChild(classNode)
                classNode.count = 0
                
            return classNode
            
        classesGraph = Graph()
        
        self.dataTree.clear()
        for node in self._dataGraph.getNodes():
            if node.object:
                classNode = createClassNode(node.object.getClass())
                classNode.count += 1
        
        populateTree(self.dataTree, classesGraph.getRootNodes())

    
    def _fillRightPane(self, parent):
        """
        # Create the right Pane that will be composed by:
        # a Action Buttons TOOLBAR in the top
        # and another vertical Pane with:
        # Runs History (at Top)
        # Sectected run info (at Bottom)
        """
        # Create the Action Buttons TOOLBAR
        toolbar = tk.Frame(parent, bg='white')
        toolbar.grid(row=0, column=0, sticky='news')
        gui.configureWeigths(toolbar)
        #toolbar.columnconfigure(0, weight=1)
        toolbar.columnconfigure(1, weight=1)
        
        self.runsToolbar = tk.Frame(toolbar, bg='white')
        self.runsToolbar.grid(row=0, column=0, sticky='sw')
        # On the left of the toolbar will be other
        # actions that can be applied to all runs (refresh, graph view...)
        self.allToolbar = tk.Frame(toolbar, bg='white')
        self.allToolbar.grid(row=0, column=10, sticky='se')
        #self.createActionToolbar()

        # Create the Run History tree
        v = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        #runsFrame = ttk.Labelframe(v, text=' History ', width=500, height=500)
        runsFrame = tk.Frame(v, bg='white')
        self._createDataGraph(runsFrame)
        gui.configureWeigths(runsFrame)
        
        # Create the Selected Run Info
        infoFrame = tk.Frame(v)
        gui.configureWeigths(infoFrame)
        self._infoText = TaggedText(infoFrame, bg='white')
        self._infoText.grid(row=0, column=0, sticky='news')
        
        v.add(runsFrame, weight=3)
        v.add(infoFrame, weight=1)
        v.grid(row=1, column=0, sticky='news')

    # TODO(josemi): check that the call to RoundedTextBox is correct
    # It looks suspicious because RoundedTextBox() needs 5 arguments, not 3
    def _createNode(self, canvas, node, y):
        """ Create Data node to be painted in the graph. """
        node.selected = False
        node.box = RoundedTextBox(canvas, node, y)
        return node.box

    def _createDataItem(self, canvas, node, y):
        if node.object is None:
            nodeText = "Project"
        else:
            label = getObjectLabel(node.object, self.project.mapper)
            nodeText = (label[:25]+'...') if len(label) > 25 else label
                
        textColor = 'black'
        color = '#ADD8E6' #Lightblue
        item = self._dataCanvas.createTextbox(nodeText, 100, y, bgColor=color, textColor=textColor)

        return item
    
    def _createDataGraph(self, parent):
        """ This will be the upper part of the right panel.
        It will contains the Data Graph with their relations. 
        """
        self._dataCanvas = Canvas(parent, width=600, height=500)
        self._dataCanvas.grid(row=0, column=0, sticky='nsew')
        self._dataCanvas.onClickCallback = self._onClick
        self._dataCanvas.onDoubleClickCallback = self._onDoubleClick
        self._dataCanvas.onRightClickCallback = self._onRightClick
       
        self._updateDataGraph()
        
    def _updateDataGraph(self): 
        lt = LevelTree(self._dataGraph)
        self._dataCanvas.clear()
        lt.setCanvas(self._dataCanvas)
        lt.paint(self._createDataItem)
        self._dataCanvas.updateScrollRegion()
        
    def _selectObject(self, obj):
        self._selected = obj
        self._infoText.setReadOnly(False)
        self._infoText.setText('*Label:* ' + getObjectLabel(obj, self.project.mapper))
        self._infoText.addText('*Info:* ' + str(obj))
        self._infoText.addText('*Created:* ' + '2014-11-22')
        if obj.getObjComment():
            self._infoText.addText('*Comments:* ' + obj.getObjComment())
        self._infoText.setReadOnly(True)
        
    def _onClick(self, e=None):
        if e.node.object:
            self._selectObject(e.node.object)
    
    def _onDoubleClick(self, e=None):
        if e.node.object:
            self._selectObject(e.node.object)
            # Graph the first viewer available for this type of object
            ViewerClass = findViewers(self._selected.getClassName(), DESKTOP_TKINTER)[0] #
            viewer = ViewerClass(project=self.project)
            viewer.visualize(self._selected)
        
    def _onRightClick(self, e=None):
        return [(Message.LABEL_EDIT, self._editObject, Icon.ACTION_EDIT)]
    
    def _editObject(self):
        """Open the Edit GUI Form given an instance"""
        EditObjectDialog(self, Message.TITLE_EDIT_OBJECT, self._selected, self.project.mapper)

    def refreshData(self, e=None, initRefreshCounter=True):
        """ Refresh the status of displayed data.
         Params:
            e: Tk event input
            initRefreshCounter: if True the refresh counter will be set to 3 secs
             then only case when False is from _automaticRefreshData where the
             refresh time is doubled each time to avoid refreshing too often.
        """        
        self._dataGraph = self.windows.project.getSourceGraph(True)
        self._updateDataTree()
        self._updateDataGraph()
 
        if initRefreshCounter:
            self.__autoRefreshCounter = 3 # start by 3 secs
            if self.__autoRefresh:
                self.dataTree.after_cancel(self.__autoRefresh)
                self.__autoRefresh = self.dataTree.after(self.__autoRefreshCounter*1000, self._automaticRefreshData)
         
    def _automaticRefreshData(self, e=None):
        """ Schedule automatic refresh increasing the time between refreshes. """
        self.refreshData(initRefreshCounter=False)
        secs = self.__autoRefreshCounter
        # double the number of seconds up to 30 min
        self.__autoRefreshCounter = min(2*secs, 1800)
        self.__autoRefresh = self.dataTree.after(secs*1000, self._automaticRefreshData)
                
                
class DataTextBox(RoundedTextBox):
    def __init__(self, canvas, text, x, y, bgColor, textColor='black'):
        RoundedTextBox.__init__(self, canvas, text, x, y, bgColor, textColor)