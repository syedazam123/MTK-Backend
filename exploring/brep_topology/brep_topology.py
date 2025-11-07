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
import os

from pathlib import Path

import manufacturingtoolkit.CadExMTK as mtk

sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../"))

import mtk_license as license

class UnorientedShapeKey:
    def __init__(self, theShape: mtk.ModelData_Shape):
        self.myShape = theShape

    def __hash__(self):
        aHasher = mtk.ModelData_UnorientedShapeHash()
        return int(aHasher(self.myShape))

    def __eq__(self, other):
        if id(other) == id(self):
            return True
        if isinstance(other, UnorientedShapeKey):
            anEqualityChecker = mtk.ModelData_UnorientedShapeEqual()
            return anEqualityChecker(other.myShape, self.myShape)
        return False

class PartBRepVisitor(mtk.ModelData_ModelElementVoidVisitor):
    def __init__(self):
        super().__init__()
        self.myNestingLevel = 0
        self.myShapeSet = set()

    def PrintUniqueShapesCount(self):
        print();
        print(f"Total unique shapes count: {len(self.myShapeSet)}")

    def VisitPart(self, thePart: mtk.ModelData_Part):
        aBodies = thePart.Bodies()
        if thePart.NumberOfBodies() > 0:
            self.ExploreBRep(aBodies)

    def ExploreBRep(self, theBodies: mtk.Collections_BodyList):
        for i, aBody in enumerate(theBodies):
            print("Body ", i, ": type ", self.PrintBodyType(aBody))
            aShapeIt = mtk.ModelData_ShapeIterator(aBody)
            for aShape in aShapeIt:
                self.ExploreShape(aShape)

    # Recursive iterating over the Shape until reaching vertices
    def ExploreShape(self, theShape: mtk.ModelData_Shape):
        self.myShapeSet.add(UnorientedShapeKey(theShape))
        self.myNestingLevel += 1
        aShapeIt = mtk.ModelData_ShapeIterator(theShape)
        while aShapeIt.HasNext():
            aShape = aShapeIt.Next()
            self.PrintShapeInfo(aShape)
            self.ExploreShape(aShape)

        self.myNestingLevel -= 1

    # Returns body type name
    def PrintBodyType(self, theBody: mtk.ModelData_Body) -> str:
        if mtk.ModelData_SolidBody.CompareType(theBody): 
            return "Solid"
        if mtk.ModelData_SheetBody.CompareType(theBody):
            return "Sheet"
        if mtk.ModelData_WireframeBody.CompareType(theBody): 
            return "Wireframe"
        return "Undefined"

    # Prints shape type name and prints shape info in some cases
    def PrintShapeInfo(self, theShape: mtk.ModelData_Shape) -> str:
        self.PrintTabulation()

        aType = theShape.Type()
        if aType == mtk.ShapeType_Solid: 
            print("Solid", end="")
        elif aType == mtk.ShapeType_Shell: 
            print("Shell", end="")
        elif aType == mtk.ShapeType_Wire:
            print("Wire", end="")
            self.PrintWireInfo(mtk.ModelData_Wire.Cast(theShape))
        elif aType == mtk.ShapeType_Face:
            print("Face", end="")
            self.PrintFaceInfo(mtk.ModelData_Face.Cast(theShape))
        elif aType == mtk.ShapeType_Edge:
            print("Edge", end="")
            self.PrintEdgeInfo(mtk.ModelData_Edge.Cast(theShape))
        elif aType == mtk.ShapeType_Vertex:
            print("Vertex", end="")
            self.PrintVertexInfo(mtk.ModelData_Vertex.Cast(theShape))
        else:
            print("Undefined", end="")

        print()

    def PrintOrientationInfo(self, theShape: mtk.ModelData_Shape):
        print(". Orientation: ", end="")
        anOrientation = theShape.Orientation()
        if anOrientation == mtk.ShapeOrientation_Forward:
            print("Forward", end="")
        elif anOrientation == mtk.ShapeOrientation_Reversed:
            print("Reversed", end="")

    def PrintWireInfo(self, theWire: mtk.ModelData_Wire):
        self.myNestingLevel += 1
        self.PrintOrientationInfo(theWire)
        self.myNestingLevel -= 1

    def PrintFaceInfo(self, theFace: mtk.ModelData_Face):
        self.myNestingLevel += 1
        self.PrintOrientationInfo(theFace)
        print()
        aSurface = theFace.Surface()
        self.PrintTabulation()
        print(f"Surface: {self.PrintSurfaceType(aSurface)}", end="")
        self.myNestingLevel -= 1

    def PrintSurfaceType(self, theSurface: mtk.Geom_Surface) -> str:
        aType = theSurface.Type()
        if aType == mtk.SurfaceType_Plane: 
            return "Plane"
        if aType == mtk.SurfaceType_Cylinder: 
            return "Cylinder"
        if aType == mtk.SurfaceType_Cone: 
            return "Cone"
        if aType == mtk.SurfaceType_Sphere: 
            return "Sphere"
        if aType == mtk.SurfaceType_Torus: 
            return "Torus"
        if aType == mtk.SurfaceType_LinearExtrusion: 
            return "LinearExtrusion"
        if aType == mtk.SurfaceType_Revolution: 
            return "Revolution"
        if aType == mtk.SurfaceType_Bezier: 
            return "Bezier"
        if aType == mtk.SurfaceType_BSpline: 
            return "BSpline"
        if aType == mtk.SurfaceType_Offset: 
            return "Offset"
        return "Undefined"

    def PrintEdgeInfo(self, theEdge: mtk.ModelData_Edge):
        self.myNestingLevel += 1
        if theEdge.IsDegenerated():
            print("(Degenerated)", end="")
        self.PrintOrientationInfo(theEdge)
        print(f". Tolerance {theEdge.Tolerance()}", end="")

        if not theEdge.IsDegenerated():
            print()
            aCurve, aParamFirst, aParamLast = theEdge.Curve()
            self.PrintTabulation()
            print(f"Curve: {self.PrintCurveType(aCurve)}", end="")

        self.myNestingLevel -= 1

    def PrintCurveType(self, theCurve: mtk.Geom_Curve) -> str:
        aType = theCurve.Type()
        if aType == mtk.CurveType_Line: 
            return "Line"
        if aType == mtk.CurveType_Circle: 
            return "Circle"
        if aType == mtk.CurveType_Ellipse: 
            return "Ellipse"
        if aType == mtk.CurveType_Hyperbola: 
            return "Hyperbola"
        if aType == mtk.CurveType_Parabola: 
            return "Parabola"
        if aType == mtk.CurveType_Bezier: 
            return "Bezier"
        if aType == mtk.CurveType_BSpline: 
            return "BSpline"
        if aType == mtk.CurveType_Offset: 
            return "Offset"
        return "Undefined"

    def PrintVertexInfo(self, theVertex: mtk.ModelData_Vertex):
        self.PrintOrientationInfo(theVertex)
        print(f". Tolerance {theVertex.Tolerance()}", end="")

    def PrintTabulation(self):
        print("- " * self.myNestingLevel, end="")

import sys

from os.path import abspath, dirname
from pathlib import Path

def main(theSource:str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()

    if not mtk.ModelData_ModelReader().Read(mtk.UTF16String(theSource), aModel):
        print("Failed to read the file " + theSource)
        return 1

    # Explore B-Rep representation of model parts
    aVisitor = PartBRepVisitor()
    aModel.Accept(aVisitor)

    aVisitor.PrintUniqueShapesCount()

    print("Completed")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + os.path.abspath(Path(__file__).resolve()) + " <input_file>, where:")
        print("    <input_file>  is a name of the file to be read")
        sys.exit(1)

    aSource = os.path.abspath(sys.argv[1])
    sys.exit(main(aSource))
