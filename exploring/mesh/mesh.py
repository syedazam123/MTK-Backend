# $Id$

# Copyright (C) 2008-2014, Roman Lygin. All rights reserved.
# Copyright (C) 2014-2025, CADEX. All rights reserved.

# This file is part of the Manufacturing Toolkit software.

# You may use this file under the terms of the BSD license as follows:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

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

class PartMeshVisitor(mtk.ModelData_ModelElementVoidVisitor):
    def VisitPart(self, thePart: mtk.ModelData_Part):
        print(f"Part = \"{thePart.Name()}\"")
        aBodies = thePart.Bodies()
        if aBodies.size() > 0:
            self.ExploreMeshBodies(aBodies)

    def ExploreMeshBodies(self, theBodies: mtk.Collections_BodyList):
        for i in range(theBodies.size()):
            aBody = theBodies[i]
            if mtk.ModelData_MeshBody.CompareType(aBody):
                aMeshBody = mtk.ModelData_MeshBody.Cast(aBody)
                print(f"MeshBody {i}")
                aMeshShapes = aMeshBody.Shapes()
                for j in range(aMeshShapes.size()):
                    aMeshShape = aMeshShapes[j]
                    print(f"MeshShape {j}", end="")
                    self.PrintMeshShapeInfo(aMeshShape)

    def PrintMeshShapeInfo(self, theMeshShape: mtk.ModelData_MeshShape):
        if mtk.ModelData_IndexedTriangleSet.CompareType(theMeshShape):
            aITS = mtk.ModelData_IndexedTriangleSet.Cast(theMeshShape)
            print(" IndexedTriangleSet type.")
            self.DumpTriangleSet(aITS)
        elif mtk.ModelData_PolylineSet.CompareType(theMeshShape):
            aPLS = mtk.ModelData_PolylineSet.Cast(theMeshShape)
            print(" PolyLineSet type")
            self.DumpPolylineSet(aPLS)
        elif mtk.ModelData_Polyline2dSet.CompareType(theMeshShape):
            aPL2dS = mtk.ModelData_Polyline2dSet.Cast(theMeshShape)
            print(" PolyLine2dSet type")
            self.DumpPolyline2dSet(aPL2dS)
        elif mtk.ModelData_PointSet.CompareType(theMeshShape):
            aPPS = mtk.ModelData_PointSet.Cast(theMeshShape)
            print(" PolyPointSet type")
            self.DumpPointSet(aPPS)
        else:
            print(" Undefined type")

    def DumpPointSet(self, thePS: mtk.ModelData_PointSet):
        aNumberOfPoints = thePS.NumberOfPoints()
        print(f"PointSet: {aNumberOfPoints} points")
        for i in range(aNumberOfPoints):
            aP = thePS.Point(i)
            print(f"Point {i}: ({aP.X()}, {aP.Y()}, {aP.Z()})")

    def DumpPolylineSet(self, thePLS: mtk.ModelData_PolylineSet):
        aNumberOfPolylines = thePLS.NumberOfPolylines()
        print(f"PolylineSet: {aNumberOfPolylines} polylines")
        for i in range(aNumberOfPolylines):
            print(f"Polyline {i}:")
            print(" Node coordinates:")
            aPoly = thePLS.Polyline(i)
            for j in range(aPoly.NumberOfPoints()):
                aP = aPoly.Point(j)
                print(f"({aP.X()}, {aP.Y()}, {aP.Z()})")

    def DumpPolyline2dSet(self, thePLS: mtk.ModelData_Polyline2dSet):
        aNumberOfPolylines2d = thePLS.NumberOfPolylines()
        print(f"Polyline2dSet: {aNumberOfPolylines2d} polylines")
        for i in range(aNumberOfPolylines2d):
            print(f"Polyline2d {i}:")
            print(" Node coordinates:")
            aPoly = thePLS.Polyline(i)
            for j in range(aPoly.NumberOfPoints()):
                aP = aPoly.Point(j)
                print(f"({aP.X()}, {aP.Y()})")

    def DumpTriangleSet(self, theITS: mtk.ModelData_IndexedTriangleSet):
        aNumberOfTriangles = theITS.NumberOfTriangles()
        print(f"IndexedTriangleSet: {aNumberOfTriangles} triangles:")
        for i in range(aNumberOfTriangles):
            print(f"Triangle {i}:")
            for j in range(3):
                aVI = theITS.TriangleVertexIndex(i, j)
                aV = theITS.TriangleVertex(i, j)
                print(f" Node {j}: Vertex {aVI} ({aV.X()}, {aV.Y()}, {aV.Z()})")
                if theITS.HasNormals():
                    aN = theITS.TriangleVertexNormal(i, j)
                    print(f"  Normal: ({aN.X()}, {aN.Y()}, {aN.Z()})")

def main(theSource:str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()

    if not mtk.ModelData_ModelReader().Read(mtk.UTF16String(theSource), aModel):
        print("Failed to read the file " + theSource)
        return 1

    aVisitor = PartMeshVisitor()
    aModel.Accept(aVisitor)

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: <input_file>, where:")
        print("    <input_file> is a name of the file to be read")
        sys.exit()

    aSource = os.path.abspath(sys.argv[1])
    sys.exit(main(aSource))
