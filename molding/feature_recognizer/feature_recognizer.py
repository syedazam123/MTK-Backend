# $Id$
#
# Copyright (C) 2008-2014, Roman Lygin. All rights reserved.
# Copyright (C) 2014-2025, CADEX. All rights reserved.
#
# This file is part of the Manufacturing Toolkit software.
#
# You may use this file under the terms of the BSD license as follows:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
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

import math
import os
import sys

from pathlib import Path

import manufacturingtoolkit.CadExMTK as mtk

sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../"))
sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../helpers/"))

import mtk_license as license

import shape_processor
import feature_group

def ToDegrees(theAngleRad: float):
    return theAngleRad * 180.0 / math.pi

def PrintFeatureParameters(theFeature: mtk.MTKBase_Feature):
    if mtk.Molding_ScrewBoss.CompareType(theFeature):
        aScrewBoss = mtk.Molding_ScrewBoss.Cast(theFeature)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("outer radius", aScrewBoss.OuterRadius(),             "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("inner radius", aScrewBoss.InnerRadius(),             "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("draft angle",  ToDegrees (aScrewBoss.DraftAngle()),  "deg")
    elif mtk.MTKBase_Boss.CompareType(theFeature):
        aBoss = mtk.MTKBase_Boss.Cast(theFeature)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("length",      aBoss.Length(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("height",      aBoss.Height(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("width",       aBoss.Width(),  "mm")
    elif mtk.Molding_Rib.CompareType(theFeature):
        aRib = mtk.Molding_Rib.Cast(theFeature)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("length",      aRib.Length(),                 "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("height",      aRib.Height(),                 "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("thickness",   aRib.Thickness(),              "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("draft angle", ToDegrees (aRib.DraftAngle()), "deg")

def PrintFeatures(theFeatureList: mtk.MTKBase_FeatureList):
    aManager = feature_group.FeatureGroupManager()

    #group by parameters to provide more compact information about features
    for aFeature in theFeatureList:
        if mtk.Molding_ScrewBoss.CompareType(aFeature):
            aScrewBoss = mtk.Molding_ScrewBoss.Cast(aFeature)
            aManager.AddFeature ("Screw Boss(es)", "Screw Boss(es)", True, aScrewBoss)
        elif mtk.MTKBase_Boss.CompareType(aFeature):
            aBoss = mtk.MTKBase_Boss.Cast(aFeature)
            aManager.AddFeature ("Boss(es)", "Boss(es)", True, aBoss)
        elif mtk.Molding_Rib.CompareType(aFeature):
            aRib = mtk.Molding_Rib.Cast(aFeature)
            aManager.AddFeature ("Rib(s)", "Rib(s)", True, aRib)

    aManager.Print ("features", PrintFeatureParameters)

class PartProcessor(shape_processor.SolidProcessor):
    def __init__(self):
        super().__init__()

    def ProcessSolid(self, theSolid: mtk.ModelData_Solid):
        # Set up recognizer
        aRecognizerParameters = mtk.Molding_FeatureRecognizerParameters();
        aRecognizerParameters.SetMaxRibThickness (30.0)
        aRecognizerParameters.SetMaxRibDraftAngle (0.2)
        aRecognizerParameters.SetMaxRibTaperAngle (0.1)
        
        aRecognizer = mtk.Molding_FeatureRecognizer(aRecognizerParameters)
        aFeatureList = aRecognizer.Perform (theSolid)
        PrintFeatures(aFeatureList)

def main(theSource: str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()
    aReader = mtk.ModelData_ModelReader()

    # Reading the file
    if not aReader.Read(mtk.UTF16String(theSource), aModel):
        print("Failed to open and convert the file " + theSource)
        return 1

    print("Model: ", aModel.Name(), "\n", sep="")

    # Processing
    aPartProcessor = PartProcessor()
    aVisitor = mtk.ModelData_ModelElementUniqueVisitor(aPartProcessor)
    aModel.Accept(aVisitor)

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: <input_file>, where:")
        print("    <input_file> is a name of the file to be read")
        sys.exit()

    aSource = os.path.abspath(sys.argv[1])

    sys.exit(main(aSource))
