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

import os
import sys
from pathlib import Path

import manufacturingtoolkit.CadExMTK as mtk

sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../"))

import mtk_license as license

class Pattern:
    def __init__(self, theShape: mtk.Drawing_CurveSet, theName: str, theNumber: int):
        self.myDrawingDrawing_View = mtk.Drawing_View()
        self.myDrawingDrawing_View.Add(theShape)
        self.myName = theName
        self.myNumber = theNumber

def main():
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aComputer = mtk.Nesting_Computer()

    # Configuring nesting parameters
    aParams = mtk.Nesting_ComputerParameters()
    aParams.SetIterationCount(10)               # Number of iterations for optimization process
    aParams.SetGenerationSize(10)               # Initial count of random layouts; larger values may improve optimization
    aParams.SetMutationRate(0.5)                # Probability of random shape rearrangement to escape local optima
    aParams.SetPartToPartDistance(1.0)          # Minimum distance between shapes
    aParams.SetPartToSheetBoundaryDistance(1.0) # Minimum distance between shapes and sheet edges
    aParams.SetMirrorControl(False)             # Allows mirrored shapes to improve layout efficiency
    aParams.SetRotationCount(4)                 # Number of allowed rotation angles (e.g., 4 allows 0°, 90°, 180°, and 270°)
    aParams.SetCurveTolerance(10)               # Side length of squares used for polygonal approximation of curves

    aComputer.SetParameters(aParams)

    # Define material size and number (e.g., 1 sheets of 100x100 mm)
    aComputer.AddMaterial(100.0, 100.0, 1)

    aPatterns = [
        Pattern(CreateRectangle(50.0, 50.0), "Rectangle 50x50", 1),
        Pattern(CreateRectangle(20.0, 10.0), "Rectangle 20x10", 10)
    ]

    PrintPatternsInfo(aPatterns)

    # Load patterns into the computer
    for aPattern in aPatterns:
        aComputer.AddPattern(aPattern.myDrawingDrawing_View, aPattern.myNumber)

    # Start the Nesting process
    aData = aComputer.Perform()

    # Print nesting information
    PrintNestingInfo(aData)

def CreateRectangle(theWidth: float, theHeight: float) -> mtk.Drawing_CurveSet:
    aRectangle = mtk.Drawing_CurveSet()

    aL1 = mtk.Geom_Line2d(mtk.Geom_Point2d(0, 0), mtk.Geom_Direction2d(1, 0))
    aL1.SetTrim(0, theWidth)

    aL2 = mtk.Geom_Line2d(mtk.Geom_Point2d(theWidth, 0), mtk.Geom_Direction2d(0, 1))
    aL2.SetTrim(0, theHeight)

    aL3 = mtk.Geom_Line2d(mtk.Geom_Point2d(theWidth, theHeight), mtk.Geom_Direction2d(-1, 0))
    aL3.SetTrim(0, theWidth)

    aL4 = mtk.Geom_Line2d(mtk.Geom_Point2d(0, theHeight), mtk.Geom_Direction2d(0, -1))
    aL4.SetTrim(0, theHeight)

    aRectangle.AddCurve(aL1)
    aRectangle.AddCurve(aL2)
    aRectangle.AddCurve(aL3)
    aRectangle.AddCurve(aL4)

    return aRectangle

def PrintPatternsInfo(thePatterns: list):
    print("------- Patterns Info -------")
    for aPattern in thePatterns:
        print(f"{aPattern.myName}: {aPattern.myNumber}")

def PrintNestingInfo(theData: mtk.Nesting_Data):
    print("\n------- Nesting Info -------")

    aTotalEfficiency = 0.0
    aTotalScrap = 0.0
    aSheets = theData.Sheets()

    for i in range(len(aSheets)):
        print(f"# Sheet {i}")
        print(f"    Nested Parts: {aSheets[i].NestedParts()}")
        aTotalScrap += aSheets[i].Scrap()
        print(f"    Scrap: {aSheets[i].Scrap() * 100}%")
        aTotalEfficiency += aSheets[i].PlacementEfficiency()
        print(f"    Placement Efficiency: {aSheets[i].PlacementEfficiency() * 100}%\n")

    print(f"Average Scrap: {aTotalScrap / len(aSheets) * 100}%")
    print(f"Average Placement Efficiency: {aTotalEfficiency / len(aSheets) * 100}%")

if __name__ == "__main__":
    main()
