#!/usr/bin/env python

###
# Copyright (c) 2002, Tamer Fahmy <tamer@tammura.at>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

###
# This is an example from The Inventor Mentor,
# chapter 10, example 8.
#
# This example demonstrates the use of the pick filter
# callback to always select nodekits. This makes it especially
# easy to edit attributes of objects because the nodekit takes
# care of the part creation details.
#

from pivy import *
import math, sys

class UserData:
	sel = None
	editor = None
	ignore = None

##############################################################
## CODE FOR The Inventor Mentor STARTS HERE  (part 1)

# Truncate the pick path so a nodekit is selected
def pickFilterCB(void, pick):
	# See which child of selection got picked
	p = pick.getPath()

	for i in range(p.getLength() - 1, -1, -1):
		n = p.getNode(i)
		if n.isOfType(SoShapeKit_getClassTypeId()):
			break

	# Copy the path down to the nodekit
	return p.copy(0, i+1)

# CODE FOR The Inventor Mentor ENDS HERE
##############################################################


# Create a sample scene graph
def buildScene():
	g = SoGroup()
    
	# Place a dozen shapes in circular formation
	for i in range(12):
		k = SoShapeKit()
		k.setPart("shape", SoCube())
		xf = cast(k.getPart("transform", TRUE), "SoTransform")
		xf.translation.setValue(8*math.sin(i*M_PI/6), 8*math.cos(i*M_PI/6), 0.0)
		g.addChild(k)

	return g

# Update the material editor to reflect the selected object
def selectCB(userData, path):
	kit = cast(path.getTail(), "SoShapeKit")
	kitMtl = cast(kit.getPart("material", TRUE), "SoMaterial")

	# ud = cast(userData, "UserData")
	userData.ignore = TRUE
	userData.editor.setMaterial(kitMtl)
	userData.ignore = FALSE

# This is called when the user chooses a new material
# in the material editor. This updates the material
# part of each selected node kit.
def mtlChangeCB(userData, mtl):
	# Our material change callback is invoked when the
	# user changes the material, and when we change it
	# through a call to SoQtMaterialEditor_setMaterial.
	# In this latter case, we ignore the callback invocation
	# ud = cast(userData, "UserData")

	if userData.ignore:
		return

	sel = userData.sel
    
	# Our pick filter guarantees the path tail will
	# be a shape kit.
	for i in range(sel.getNumSelected()):
		p = sel.getPath(i)
		kit = cast(p.getTail(), "SoShapeKit")
		kitMtl = cast(kit.getPart("material", TRUE), "SoMaterial")
		kitMtl.copyFieldValues(mtl)

def main():
	# Initialization
	mainWindow = SoQt_init(sys.argv[0])
    
	# Create our scene graph.
	sel = SoSelection()
	sel.ref()
	sel.addChild(buildScene())

	# Create a viewer with a render action that displays highlights
	viewer = SoQtExaminerViewer(mainWindow)
	viewer.setSceneGraph(sel)
	boxhra = SoBoxHighlightRenderAction()
	viewer.setGLRenderAction(boxhra)
	viewer.redrawOnSelectionChange(sel)
	viewer.setTitle("Select Node Kits")
	viewer.show()

	# Create a material editor
	ed = SoQtMaterialEditor()
	ed.show()

	# User data for our callbacks
	userData = UserData()
	userData.sel = sel
	userData.editor = ed
	userData.ignore = FALSE
   
	# Selection and material change callbacks
	ed.addPythonMaterialChangedCallback(mtlChangeCB, userData)
	sel.setPythonPickFilterCallback(pickFilterCB)
	sel.addPythonSelectionCallback(selectCB, userData)
   
	SoQt_show(mainWindow)
	SoQt_mainLoop()

if __name__ == "__main__":
    main()