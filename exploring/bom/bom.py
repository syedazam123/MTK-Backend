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

class SceneGraphVisitor(mtk.ModelData_ModelElementVoidVisitor):
    def __init__(self):
        super().__init__()
        self.myNestingLevel = 0
        self.margin = 0; # This variable is used for formatting of output table
        self.myElementMap = {}

    def PrintName(self, theElement: mtk.ModelData_ModelElement, theName: str):
        print("--- " * self.myNestingLevel, end="")

        if theName:
            print(f"{theElement}: {theName}")
        else:
            print(f"{theElement}: noname")

        # Calculating spacing for output table columns
        self.margin = max(self.margin, theName.Length())

    def UpdateTable(self, theElement: mtk.ModelData_ModelElement):
        if not self.myElementMap.get(theElement):
            self.myElementMap[theElement] = 1
        else:
            self.myElementMap[theElement] +=  1

    def PrintElementType(self, theElement: mtk.ModelData_ModelElement) -> str:
        if mtk.ModelData_Part.CompareType(theElement):
            return "Part"
        elif mtk.ModelData_Assembly.CompareType(theElement):
            return "Assembly"
        elif mtk.ModelData_Instance.CompareType(theElement):
            return "Instance"
        return "Undefined"

    def PrintCounts(self):
        print("Total:")
        print("\t" + "name".ljust(self.margin) + " | " + "type".ljust(self.margin) + " | count")

        for i in self.myElementMap:
            aName = str(i.Name())
            aType = self.PrintElementType(i)
            print("\t" + aName.ljust(self.margin) + " | " + 
                  aType.ljust(self.margin) + " | " + str(self.myElementMap[i]))

    def VisitPart(self, thePart: mtk.ModelData_Part):
        self.PrintName("Part", thePart.Name())
        self.UpdateTable(thePart)

    def VisitEnterAssembly(self, theAssembly: mtk.ModelData_Assembly) -> bool:
        self.PrintName("Assembly", theAssembly.Name())
        self.UpdateTable(theAssembly)
        self.myNestingLevel += 1
        return True

    def VisitEnterInstance(self, theInstance: mtk.ModelData_Instance) -> bool:
        self.PrintName("Instance", theInstance.Name())
        self.myNestingLevel += 1
        return True
            
    def VisitLeaveAssembly(self, theAssembly: mtk.ModelData_Assembly):
        self.myNestingLevel -= 1

    def VisitLeaveInstance(self, theInstance: mtk.ModelData_Instance):
        self.myNestingLevel -= 1

def main(theSource: str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()

    if not mtk.ModelData_ModelReader().Read(mtk.UTF16String(theSource), aModel):
        print("Failed to read the file " + theSource)
        return 1

    aVisitor = SceneGraphVisitor()

    aModel.Accept(aVisitor)
    aVisitor.PrintCounts()

    print("Completed")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + os.path.abspath(Path(__file__).resolve()) + " <input_file>, where:")
        print("    <input_file>  is a name of the file to be read")
        sys.exit()

    aSource = os.path.abspath(sys.argv[1])

    sys.exit(main(aSource))
