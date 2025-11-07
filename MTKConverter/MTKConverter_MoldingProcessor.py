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

import manufacturingtoolkit.CadExMTK as mtk

import MTKConverter_PartProcessor as part_proc

class MTKConverter_MoldingData(part_proc.MTKConverter_ProcessData):
    def __init__(self, thePart: mtk.ModelData_Part):
        super().__init__(thePart)
        self.myFeatureList = mtk.MTKBase_FeatureList()
        self.myIssueList = mtk.MTKBase_FeatureList()

class MTKConverter_MoldingProcessor(part_proc.MTKConverter_VoidPartProcessor):
    def __init__(self, theExtraDataModel: mtk.ModelData_Model):
        super().__init__()
        self.myExtraDataModel = theExtraDataModel
        self.myCurrentNewFaces = mtk.ModelData_SheetBody()

    def __AddNewFacesFromFeatures(self, theFeatureList : mtk.MTKBase_FeatureList, theSolid : mtk.ModelData_Solid):
        aFaceIdSet = set()
        aShapeIt = mtk.ModelData_ShapeIterator(theSolid, mtk.ShapeType_Face)
        for aFace in aShapeIt:
            aFaceIdSet.add(aFace.Id())

        for aFeature in theFeatureList:
            aShapeFeature = mtk.MTKBase_ShapeFeature.Cast(aFeature)
            aFaceIt = mtk.ModelData_ShapeIterator(aShapeFeature.Shape(), mtk.ShapeType_Face)
            for aFace in aFaceIt:
                if aFace.Id() not in aFaceIdSet:
                    self.myCurrentNewFaces.Append(mtk.ModelData_Face.Cast(aFace))

    def ProcessSolid (self, thePart: mtk.ModelData_Part, theSolid: mtk.ModelData_Solid):
        aMoldingData = MTKConverter_MoldingData(thePart)
        self.myData.append(aMoldingData)

        aParams = mtk.Molding_FeatureRecognizerParameters()
        aFeatureRecognizer = mtk.Molding_FeatureRecognizer(aParams)
        anAnalyzer = mtk.Molding_Analyzer()
        anAnalyzer.AddTool(aFeatureRecognizer)
        aData = anAnalyzer.Perform(theSolid)
        if aData.IsEmpty():
            return

        # Features
        for i in aData.FeatureList():
            aMoldingData.myFeatureList.Append(i)
        self.__AddNewFacesFromFeatures(aMoldingData.myFeatureList, theSolid)

        # Issues
        aParameters = mtk.DFMMolding_AnalyzerParameters()
        aDFMAnalyzer = mtk.DFMMolding_Analyzer(aParameters)
        aMoldingData.myIssueList = aDFMAnalyzer.Perform(aData)

    def PostPartProcess(self, thePart: mtk.ModelData_Part):
        if len(self.myCurrentNewFaces.Shapes()) == 0:
            return

        anExtraDataPart = mtk.ModelData_Part(thePart.Name())
        anExtraDataPart.SetUuid(thePart.Uuid())
        anExtraDataPart.AddBody(self.myCurrentNewFaces)

        self.myExtraDataModel.AddRoot(anExtraDataPart)
        self.myCurrentNewFaces = mtk.ModelData_SheetBody()