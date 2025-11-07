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

sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + r"/../../"))

import mtk_license as license

class ProgressBarObserver(mtk.ProgressStatus_Observer):
    def __init__(self):
        super().__init__()

    def ChangedValue(self, theInfo: mtk.ProgressStatus):
        print(theInfo.Value())

    def Completed(self, theInfo: mtk.ProgressStatus):
        print(f"{theInfo.Value()}: complete!")

def main(theSource: str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()

    # An observer must outlive progress status,
    # so it is created outside the using scope
    anObserver = ProgressBarObserver()

    with mtk.ProgressStatus() as aStatus:
        # Register an observer to progress status
        aStatus.Register(anObserver)

        # The top scope occupies the whole progress status range
        with mtk.ProgressScope(aStatus) as aTopScope:
             # 50% of TopScope for file importing
            with mtk.ProgressScope(aTopScope, 50) as aReaderScope:
                aReader = mtk.ModelData_ModelReader()
                # Connect progress status object
                aReader.SetProgressStatus(aStatus)
                aReader.Read(mtk.UTF16String(theSource), aModel)
                        
            if not aModel.IsEmpty() and not aStatus.WasCanceled():
                # The remaining 50% of TopScope for meshing
                with mtk.ProgressScope(aTopScope, 50):
                    aMesher = mtk.ModelAlgo_MeshGenerator()
                    # Connect progress status object
                    aMesher.SetProgressStatus(aStatus)
                    aMesher.Generate(aModel)

    # Observer will be automatically unregistered from progress status on destruction (end of the "with" scope).

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: " + os.path.abspath(Path(__file__).resolve()) + " <input_file>, where:")
        print("    <input_file>  is a name of the file to be read")
        sys.exit(1)

    aSource = os.path.abspath(sys.argv[1])

    sys.exit(main(aSource))
