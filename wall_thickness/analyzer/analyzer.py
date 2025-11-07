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
sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../helpers/"))

import mtk_license as license

import shape_processor

class PartProcessor(shape_processor.SolidProcessor):
    def __init__(self):
        super().__init__()
        self.myAnalyzer = mtk.WallThickness_Analyzer()
        self.myResolution = 1000

    def ProcessSolid(self, theSolid: mtk.ModelData_Solid):
        aWTData = self.myAnalyzer.Perform(theSolid, self.myResolution)
        self.PrintWTData(aWTData)

    def PrintWTData(self, theData: mtk.WallThickness_Data):
        if theData.IsEmpty() != True:
            print("    Min thickness = ", theData.MinThickness(), " mm", sep="")
            print("    Max thickness = ", theData.MaxThickness(), " mm\n", sep="")
        else:
            print("    Failed to analyze the wall thickness of this entity.\n")

def main(theSource: str, theRes: int):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    if theRes < 100:
        print("WARNING: Input resolution \"" + theRes + "\" < 100. Will be used default resolution.\n")
        theRes = 1000

    aModel = mtk.ModelData_Model()
    aReader = mtk.ModelData_ModelReader()

    # Reading the file
    if not aReader.Read(mtk.UTF16String(theSource), aModel):
        print("Failed to open and convert the file " + theSource)
        return 1

    print("Model: ", aModel.Name(), "\n", sep="")

    # Processing
    aPartProcessor = PartProcessor()
    aPartProcessor.myResolution = theRes
    aVisitor = mtk.ModelData_ModelElementUniqueVisitor(aPartProcessor)
    aModel.Accept(aVisitor)

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: <input_file> <input_resolution>, where:")
        print("    <input_file> is a name of the file to be read")
        print("    <input_resolution> is an optional argument that determine accuracy")
        print("    of wall thickness calculation.")
        print("    The larger the value, the higher the accuracy of the calculations,")
        print("    but greatly increase computation time and memory usage.")
        print("    Should be at least 100.")
        sys.exit()

    aSource = os.path.abspath(sys.argv[1])
    if len(sys.argv) == 3:
        aRes = sys.argv[2]
    else:
        aRes = 1000

    sys.exit(main(aSource, aRes))
