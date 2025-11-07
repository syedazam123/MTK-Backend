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

sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../"))

import mtk_license as license

import math

class FirstFaceGetter(mtk.ModelData_ModelElementVoidVisitor):
    def __init__(self):
        mtk.ModelData_ModelElementVoidVisitor.__init__(self)
        self.myFace = None

    def VisitPart(self, thePart: mtk.ModelData_Part):
        if self.myFace is None:
            aBodies = thePart.Bodies()
            if thePart.NumberOfBodies() > 0:
                self.ExploreBRep(aBodies)

    def ExploreBRep(self, theBodies: mtk.Collections_BodyList):
        for aBody in theBodies:
            aShapeIt = mtk.ModelData_ShapeIterator(aBody, mtk.ShapeType_Face)
            for aShape in aShapeIt:
                self.myFace = mtk.ModelData_Face.Cast(aShape)
                break
            
    def FirstFace(self):
        return self.myFace

def PrintFaceTriangulationInfo(theFace: mtk.ModelData_Face):
    anITS = theFace.Triangulation()

    print(f"Face triangulation contains {anITS.NumberOfTriangles()} triangles.")

    aNumberOfTrianglesToPrint = min(4, anITS.NumberOfTriangles())

    for i in range(aNumberOfTrianglesToPrint):
        print(f"Triangle index {i} with vertices: ")
        for j in range(3):
            aVertexIndex = anITS.TriangleVertexIndex (i, j);
            aPoint = anITS.TriangleVertex(i, j);
            print(f"  Vertex index {aVertexIndex} with coords",
                  f"(X: {aPoint.X()}, Y: {aPoint.Y()}, Z: {aPoint.Z()})")

def main(theSource: str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()

    if not mtk.ModelData_ModelReader().Read(mtk.UTF16String(theSource), aModel):
        print("Failed to read the file " + theSource)
        return 1

    # Set up mesher and parameters
    aParam = mtk.ModelAlgo_MeshGeneratorParameters()
    aParam.SetAngularDeflection(math.pi * 10 / 180)
    aParam.SetChordalDeflection(0.003)

    aMesher = mtk.ModelAlgo_MeshGenerator(aParam)
    aMesher.Generate(aModel)

    aVisitor = FirstFaceGetter();
    aModel.Accept(aVisitor);

    aFace = aVisitor.FirstFace();
    PrintFaceTriangulationInfo(aFace)

    print("Completed")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + os.path.abspath(Path(__file__).resolve()) + " <input_file>, where:")
        print("    <input_file>  is a name of the file to be read")
        sys.exit(1)

    aSource = os.path.abspath(sys.argv[1])

    sys.exit(main(aSource))
