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

import feature_group
import shape_processor

def ToDegrees(theAngleRad: float):
    return theAngleRad * 180.0 / math.pi

def PrintFeatureParameters(theIssue: mtk.MTKBase_Feature):
    if mtk.DFMMolding_IrregularCoreDepthScrewBossIssue.CompareType(theIssue):
        aICDSBIssue = mtk.DFMMolding_IrregularCoreDepthScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual height",     aICDSBIssue.ActualHeight(),    "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual core depth", aICDSBIssue.ActualCoreDepth(), "mm")
    elif mtk.DFMMolding_IrregularCoreDiameterScrewBossIssue.CompareType(theIssue):
        aICDSBIssue = mtk.DFMMolding_IrregularCoreDiameterScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min core diameter", aICDSBIssue.ExpectedMinCoreDiameter(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max core diameter", aICDSBIssue.ExpectedMaxCoreDiameter(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual core diameter",       aICDSBIssue.ActualCoreDiameter(),      "mm")
    elif mtk.DFMMolding_IrregularWallThicknessScrewBossIssue.CompareType(theIssue):
        aIWTSBIssue = mtk.DFMMolding_IrregularWallThicknessScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max thickness", aIWTSBIssue.ExpectedMaxThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min thickness", aIWTSBIssue.ExpectedMinThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual thickness",       aIWTSBIssue.ActualThickness(),      "mm")
    elif mtk.DFMMolding_HighScrewBossIssue.CompareType(theIssue):
        aHSBIssue = mtk.DFMMolding_HighScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max height", aHSBIssue.ExpectedMaxHeight(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual height",       aHSBIssue.ActualHeight(),  "mm")
    elif mtk.DFMMolding_SmallBaseRadiusRibIssue.CompareType(theIssue):
        aSBRRIssue = mtk.DFMMolding_SmallBaseRadiusRibIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min base radius", aSBRRIssue.ExpectedMinBaseRadius(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual base radius",       aSBRRIssue.ActualBaseRadius(),      "mm")
    elif mtk.DFMMolding_SmallBaseRadiusScrewBossIssue.CompareType(theIssue):
        aSBRSBIssue = mtk.DFMMolding_SmallBaseRadiusScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min base radius", aSBRSBIssue.ExpectedMinBaseRadius(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual base radius",       aSBRSBIssue.ActualBaseRadius(),      "mm")
    elif mtk.DFMMolding_SmallDraftAngleScrewBossIssue.CompareType(theIssue):
        aSDASBIssue = mtk.DFMMolding_SmallDraftAngleScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min draft angle", ToDegrees (aSDASBIssue.ExpectedMinDraftAngle()), "deg")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual draft angle",       ToDegrees (aSDASBIssue.ActualDraftAngle()),      "deg")
    elif mtk.DFMMolding_SmallHoleBaseRadiusScrewBossIssue.CompareType(theIssue):
        aSHBRSBIssue = mtk.DFMMolding_SmallHoleBaseRadiusScrewBossIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min hole base radius", aSHBRSBIssue.ExpectedMinHoleBaseRadius(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual hole base radius",       aSHBRSBIssue.ActualHoleBaseRadius(),      "mm")
    elif mtk.DFMMolding_NonChamferedScrewBossIssue.CompareType(theIssue):
        #no parameters
        pass
    elif mtk.DFMMolding_HighRibIssue.CompareType(theIssue):
        aHRIssue = mtk.DFMMolding_HighRibIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max height", aHRIssue.ExpectedMaxHeight(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual height",       aHRIssue.ActualHeight(),      "mm")
    elif mtk.DFMMolding_IrregularThicknessRibIssue.CompareType(theIssue):
        aITRIssue = mtk.DFMMolding_IrregularThicknessRibIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min thickness", aITRIssue.ExpectedMinThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max thickness", aITRIssue.ExpectedMaxThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual thickness",       aITRIssue.ActualThickness(),      "mm")
    elif mtk.DFMMolding_SmallDraftAngleRibIssue.CompareType(theIssue):
        aSDARIssue = mtk.DFMMolding_SmallDraftAngleRibIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min draft angle", ToDegrees (aSDARIssue.ExpectedMinDraftAngle()), "deg")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual draft angle",       ToDegrees (aSDARIssue.ActualDraftAngle()),      "deg")
    elif mtk.DFMMolding_SmallDistanceBetweenRibsIssue.CompareType(theIssue):
        aSDBRIssue = mtk.DFMMolding_SmallDistanceBetweenRibsIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min distance", aSDBRIssue.ExpectedMinDistanceBetweenRibs(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual distance",       aSDBRIssue.ActualDistanceBetweenRibs(),      "mm")

    elif mtk.DFMMolding_IrregularWallThicknessIssue.CompareType(theIssue):
        aIWTIIssue = mtk.DFMMolding_IrregularWallThicknessIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max thickness", aIWTIIssue.ExpectedMaxThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min thickness", aIWTIIssue.ExpectedMinThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual thickness",       aIWTIIssue.ActualThickness(),      "mm")
    elif mtk.DFMMolding_LargeWallThicknessIssue.CompareType(theIssue):
        aLWTIIssue = mtk.DFMMolding_LargeWallThicknessIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected max thickness", aLWTIIssue.ExpectedMaxThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual thickness",       aLWTIIssue.ActualThickness(),      "mm")
    elif mtk.DFMMolding_SmallWallThicknessIssue.CompareType(theIssue):
        aSWTIIssue = mtk.DFMMolding_SmallWallThicknessIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min thickness", aSWTIIssue.ExpectedMinThickness(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual thickness",       aSWTIIssue.ActualThickness(),      "mm")
    elif mtk.DFMMolding_SmallDraftAngleWallIssue.CompareType(theIssue):
        aSDAWIssue = mtk.DFMMolding_SmallDraftAngleWallIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min draft angle", ToDegrees (aSDAWIssue.ExpectedMinDraftAngle()), "deg")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual draft angle",       ToDegrees (aSDAWIssue.ActualDraftAngle()),      "deg")
    elif mtk.DFMMolding_SmallDistanceBetweenBossesIssue.CompareType(theIssue):
        aSDBBIssue = mtk.DFMMolding_SmallDistanceBetweenBossesIssue.Cast(theIssue)
        feature_group.FeatureGroupManager.PrintFeatureParameter ("expected min distance", aSDBBIssue.ExpectedMinDistanceBetweenBosses(), "mm")
        feature_group.FeatureGroupManager.PrintFeatureParameter ("actual distance",       aSDBBIssue.ActualDistanceBetweenBosses(),      "mm")

def PrintIssues(theIssueList: mtk.MTKBase_FeatureList):
    aManager = feature_group.FeatureGroupManager()

    #group by parameters to provide more compact information about features
    for anIssue in theIssueList:
        if mtk.DFMMolding_IrregularCoreDepthScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Irregular Core Depth Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_IrregularCoreDiameterScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Irregular Core Diameter Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_IrregularWallThicknessScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Irregular Wall Thickness Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_HighScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("High Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_SmallBaseRadiusScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Small Base Radius Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_SmallDraftAngleScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Small Draft Angle Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_SmallHoleBaseRadiusScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Small Hole Base Radius Screw Boss Issue(s)", "Screw Boss(es)", True, anIssue)
        elif mtk.DFMMolding_NonChamferedScrewBossIssue.CompareType(anIssue):
            aManager.AddFeature("Non Chamfered Screw Boss Issue(s)", "Screw Boss(es)", False, anIssue)
        elif mtk.DFMMolding_HighRibIssue.CompareType(anIssue):
            aManager.AddFeature("High Rib Issue(s)", "Rib(s)", True, anIssue)
        elif mtk.DFMMolding_IrregularThicknessRibIssue.CompareType(anIssue):
            aManager.AddFeature("Irregular Thickness Rib Issue(s)", "Rib(s)", True, anIssue)
        elif mtk.DFMMolding_SmallBaseRadiusRibIssue.CompareType(anIssue):
            aManager.AddFeature("Small Base Radius Rib Issue(s)", "Rib(s)", True, anIssue)
        elif mtk.DFMMolding_SmallDraftAngleRibIssue.CompareType(anIssue):
            aManager.AddFeature("Small Draft Angle Rib Issue(s)", "Rib(s)", True, anIssue)
        elif mtk.DFMMolding_SmallDistanceBetweenRibsIssue.CompareType(anIssue):
            aManager.AddFeature("Small Distance Between Ribs Issue(s)", "Rib(s)", True, anIssue)
        elif mtk.DFMMolding_IrregularWallThicknessIssue.CompareType(anIssue):
            aManager.AddFeature("Irregular Wall Thickness Issue(s)", "Wall(s)", True, anIssue)
        elif mtk.DFMMolding_LargeWallThicknessIssue.CompareType(anIssue):
            aManager.AddFeature("Large Wall Thickness Issue(s)", "Wall(s)", True, anIssue)
        elif mtk.DFMMolding_SmallWallThicknessIssue.CompareType(anIssue):
            aManager.AddFeature("Small Wall Thickness Issue(s)", "Wall(s)", True, anIssue)
        elif mtk.DFMMolding_SmallDraftAngleWallIssue.CompareType(anIssue):
            aManager.AddFeature("Small Draft Angle Wall Thickness Issue(s)", "Wall(s)", True, anIssue)
        elif mtk.DFMMolding_SmallDistanceBetweenBossesIssue.CompareType(anIssue):
            aManager.AddFeature("Small Distance Between Bosses Issue(s)", "Boss(es)", True, anIssue)

    aManager.Print ("issues", PrintFeatureParameters)

class PartProcessor(shape_processor.SolidProcessor):
    def __init__(self):
        super().__init__()

    def ProcessSolid(self, theSolid: mtk.ModelData_Solid):
        # Set up recognizer
        aRecognizerParameters = mtk.Molding_FeatureRecognizerParameters()
        aRecognizerParameters.SetMaxRibThickness (30.0)
        aRecognizerParameters.SetMaxRibDraftAngle (0.2)
        aRecognizerParameters.SetMaxRibTaperAngle (0.1)

        aRecognizer = mtk.Molding_FeatureRecognizer(aRecognizerParameters)

        # Set up analyzer
        anAnalyzer = mtk.Molding_Analyzer()
        anAnalyzer.AddTool(aRecognizer)

        # Fill molding data
        aData = anAnalyzer.Perform (theSolid)

        # Run dfm analyzer for found features
        aParameters = mtk.DFMMolding_AnalyzerParameters()
        aDFMAnalyzer = mtk.DFMMolding_Analyzer(aParameters)
        anIssueList = aDFMAnalyzer.Perform(aData)

        PrintIssues(anIssueList)

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
