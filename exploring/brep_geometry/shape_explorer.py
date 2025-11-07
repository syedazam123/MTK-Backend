#!/usr/bin/env python3

# $Id$

# Copyright (C) 2008-2014, Roman Lygin. All rights reserved.
# Copyright (C) 2014-2025, CADEX. All rights reserved.

# This file is part of the Manufacturing Toolkit software.

# You may use this file under the terms of the BSD license as follows:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys
from pathlib import Path
import os

import manufacturingtoolkit.CadExMTK as mtk
from base_explorer import BaseExplorer
from surface_explorer import SurfaceExplorer
from curve_explorer import CurveExplorer
from pcurve_explorer import PCurveExplorer

class ShapeExplorer(mtk.ModelData_ModelElementVoidVisitor, BaseExplorer):
    def __init__(self):
        BaseExplorer.__init__(self)
        mtk.ModelData_ModelElementVoidVisitor.__init__(self)

    def VisitPart(self, thePart: mtk.ModelData_Part):
        aBodies = thePart.Bodies()
        if thePart.NumberOfBodies() > 0:
            print(f"Part = \"{thePart.Name()}\"")
            self.ExploreBRep(aBodies)

    def ExploreBRep(self, theBodies: mtk.Collections_BodyList):
        for i, aBody in enumerate(theBodies):
            print(f"Body {i}: {self.BodyType(aBody)}")
            aShapeIt = mtk.ModelData_ShapeIterator(aBody)
            for aShape in aShapeIt:
                self.ExploreShape(aShape)

    # Recursive iterating over the Shape until reaching vertices
    def ExploreShape(self, theShape: mtk.ModelData_Shape):
        if theShape.Type() == mtk.ShapeType_Face:
            self.myCurrentFace = mtk.ModelData_Face.Cast(theShape)
        self.myNestingLevel += 1
        for aShape in mtk.ModelData_ShapeIterator(theShape):
            self.PrintShape(aShape)
            self.ExploreShape(aShape)

        if theShape.Type() == mtk.ShapeType_Face:
            self.myCurrentFace = None

        self.myNestingLevel -= 1

    # Returns body type name
    def BodyType(self, theBody: mtk.ModelData_Body) -> str:
        if mtk.ModelData_SolidBody.CompareType(theBody): 
            return "Solid"
        if mtk.ModelData_SheetBody.CompareType(theBody):
            return "Sheet"
        if mtk.ModelData_WireframeBody.CompareType(theBody): 
            return "Wireframe"
        return "Undefined"

    # Returns shape type name and prints shape info in some cases
    def PrintShape(self, theShape: mtk.ModelData_Shape):
        self.PrintTabulation()
        aType = theShape.Type()
        if aType == mtk.ShapeType_Solid:
            print("Solid", end="")
        elif aType == mtk.ShapeType_Shell:  
            self.PrintShell(mtk.ModelData_Shell.Cast(theShape))
        elif aType == mtk.ShapeType_Wire:   
            self.PrintWire(mtk.ModelData_Wire.Cast(theShape))
        elif aType == mtk.ShapeType_Face:   
            self.PrintFace(mtk.ModelData_Face.Cast(theShape))
        elif aType == mtk.ShapeType_Edge:   
            self.PrintEdge(mtk.ModelData_Edge.Cast(theShape))
        elif aType == mtk.ShapeType_Vertex: 
            self.PrintVertex(mtk.ModelData_Vertex.Cast(theShape))
        else:
            print("Undefined", end="")

        print()

    def PrintShell(self, theShell: mtk.ModelData_Shell):
        self.PrintName("Shell")
        self.myNestingLevel += 1
        self.PrintOrientation(theShell.Orientation())
        self.myNestingLevel -= 1

    def PrintWire(self, theWire: mtk.ModelData_Wire):
        self.PrintName("Wire")
        self.myNestingLevel += 1
        self.PrintOrientation(theWire.Orientation())
        self.myNestingLevel -= 1

    def PrintFace(self, theFace: mtk.ModelData_Face):
        self.PrintName("Face")
        self.myNestingLevel += 1
        self.PrintOrientation(theFace.Orientation())
        print()
        aSurface = theFace.Surface()
        self.PrintTabulation()
        print("Surface: ")
        SurfaceExplorer.PrintSurface(aSurface)
        self.myNestingLevel -= 1

    def PrintEdge(self, theEdge: mtk.ModelData_Edge):
        self.PrintName("Edge")
        self.myNestingLevel += 1
        if theEdge.IsDegenerated():
            print("Degenerated: ", end="")
        self.PrintOrientation(theEdge.Orientation())
        self.PrintNamedParameter("Tolerance", theEdge.Tolerance())

        if not theEdge.IsDegenerated():
            aCurve, first, second = theEdge.Curve()
            print()
            self.PrintTabulation()
            self.PrintName("Curve")
            self.PrintRange("Edge Range", first, second)
            CurveExplorer.PrintCurveInfo(aCurve)
            
        if self.myCurrentFace:
            aPCurve, first, second = theEdge.PCurve(self.myCurrentFace)
            print()
            self.PrintTabulation()
            self.PrintName("PCurve")
            self.PrintRange("Edge Range", first, second)
            PCurveExplorer.PrintPCurveInfo(aPCurve)
            
        self.myNestingLevel -= 1

    def PrintVertex(self, theVertex:mtk.ModelData_Vertex):
        self.PrintName("Vertex")
        aLoc = theVertex.Point()
        aTolerance = theVertex.Tolerance()
        self.PrintOrientation(theVertex.Orientation())
        self.PrintNamedParameter("Tolerance", aTolerance)
        self.PrintNamedParameter("Location",  aLoc)
