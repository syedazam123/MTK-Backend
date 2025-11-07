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

from enum import Enum

import os
import manufacturingtoolkit.CadExMTK as mtk
import manufacturingtoolkit.MTKView as view
 
import MTKConverter_PartProcessor as part_proc
 
from MTKConverter_Report import MTKConverter_Report
from MTKConverter_MachiningProcessor import MTKConverter_MachiningProcessor
from MTKConverter_MoldingProcessor import MTKConverter_MoldingProcessor
from MTKConverter_SheetMetalProcessor import MTKConverter_SheetMetalProcessor
from MTKConverter_WallThicknessProcessor import MTKConverter_WallThicknessProcessor
 
class MTKConverter_ProcessType(Enum):
    MTKConverter_PT_Undefined        = -1
    MTKConverter_PT_WallThickness    = 0
    MTKConverter_PT_MachiningMilling = 1
    MTKConverter_PT_MachiningTurning = 2
    MTKConverter_PT_Molding          = 3
    MTKConverter_PT_SheetMetal       = 4
 
class MTKConverter_ReturnCode(Enum):
    # General codes
    MTKConverter_RC_OK                     = 0
    MTKConverter_RC_UnknownError           = 1
    MTKConverter_RC_GeneralException       = 2
    MTKConverter_RC_NoValidLicense         = 3
    MTKConverter_RC_InvalidArgumentsNumber = 4
    MTKConverter_RC_InvalidArgument        = 5
 
    # Import errors
    MTKConverter_RC_UnsupportedVersion     = 100
    MTKConverter_RC_UnexpectedFormat       = 101
    MTKConverter_RC_UnsupportedFileVariant = 102
    MTKConverter_RC_ImportError            = 103
 
    # Process errors
    MTKConverter_RC_ProcessError           = 200
 
    # Export errors
    MTKConverter_RC_ExportError            = 300
 
class MTKConverter_Application:
    def __init__(self):
        pass
 
    @staticmethod
    def __ProcessType(theProcessName: str):
        aProcessMap = {
            "wall_thickness":    MTKConverter_ProcessType.MTKConverter_PT_WallThickness,
            "machining_milling": MTKConverter_ProcessType.MTKConverter_PT_MachiningMilling,
            "machining_turning": MTKConverter_ProcessType.MTKConverter_PT_MachiningTurning,
            "molding":           MTKConverter_ProcessType.MTKConverter_PT_Molding,
            "sheet_metal":       MTKConverter_ProcessType.MTKConverter_PT_SheetMetal
        }
 
        if theProcessName in aProcessMap:
            return aProcessMap[theProcessName]
        else:
            return MTKConverter_ProcessType.MTKConverter_PT_Undefined
 
    @staticmethod
    def __Import(theFilePath: str, theModel: mtk.ModelData_Model):
        print("Importing ", theFilePath, "...", sep="", end="")
 
        aReader = mtk.ModelData_ModelReader()
        if not aReader.Read(mtk.UTF16String(theFilePath), theModel):
            print("\nERROR: Failed to import ", theFilePath, ". Exiting", sep="")
            return MTKConverter_ReturnCode.MTKConverter_RC_ImportError
 
        return MTKConverter_ReturnCode.MTKConverter_RC_OK
 
    @staticmethod
    def __CreateOriginModelThumbnail (theFilePath: mtk.UTF16String, theModel: mtk.ModelData_Model):
        aWriter = view.View_ImageWriter()
        aParameters = aWriter.Parameters()
        aParameters.SetImageHeight (800)
        aParameters.SetImageWidth (600)
        aParameters.SetViewCameraProjection (view.CameraProjectionType_Perspective)
        aParameters.SetViewCameraPosition (view.CameraPositionType_Default)
        aParameters.SetViewIsFitAll (True)
        aParameters.SetViewAntialiasing (view.AntialiasingMode_High)
        aParameters.SetViewBackground (view.View_ColorBackgroundStyle (view.View_Color (255, 255, 255)))
        aWriter.SetParameters (aParameters)
 
        aRes = aWriter.WriteFile (theModel, theFilePath)
        return aRes
 
    @staticmethod
    def __ApplyProcessorToModel (theProcessor: part_proc.MTKConverter_PartProcessor,
                                 theModel: mtk.ModelData_Model,
                                 theReport: MTKConverter_Report):
        aVisitor = mtk.ModelData_ModelElementUniqueVisitor(theProcessor)
        theModel.Accept(aVisitor)
        for i in theProcessor.myData:
            theReport.AddData(i)
 
    @staticmethod
    def __Process (theProcess: str,
                   theModel: mtk.ModelData_Model,
                   theReport: MTKConverter_Report,
                   theProcessModel: mtk.ModelData_Model):
        print("Processing ", theProcess, "... ", sep="", end="")
 
        theModel.AssignUuids()
 
        aProcessType = MTKConverter_Application.__ProcessType(theProcess)
        if aProcessType == MTKConverter_ProcessType.MTKConverter_PT_MachiningMilling:
            aProcessor = MTKConverter_MachiningProcessor(mtk.Machining_OT_Milling)
            MTKConverter_Application.__ApplyProcessorToModel(aProcessor, theModel, theReport)
        elif aProcessType == MTKConverter_ProcessType.MTKConverter_PT_MachiningTurning:
            aProcessor = MTKConverter_MachiningProcessor(mtk.Machining_OT_LatheMilling)
            MTKConverter_Application.__ApplyProcessorToModel(aProcessor, theModel, theReport)
        elif aProcessType == MTKConverter_ProcessType.MTKConverter_PT_Molding:
            anExtraDataName = str(theModel.Name()) + "_extra"
            theProcessModel.SetName(mtk.UTF16String(anExtraDataName))
            aProcessor = MTKConverter_MoldingProcessor(theProcessModel)
            MTKConverter_Application.__ApplyProcessorToModel(aProcessor, theModel, theReport)
        elif aProcessType == MTKConverter_ProcessType.MTKConverter_PT_SheetMetal:
            anUnfoldedName = str(theModel.Name()) + "_unfolded"
            theProcessModel.SetName(mtk.UTF16String(anUnfoldedName))
            aProcessor = MTKConverter_SheetMetalProcessor(theProcessModel)
            MTKConverter_Application.__ApplyProcessorToModel(aProcessor, theModel, theReport)
        elif aProcessType == MTKConverter_ProcessType.MTKConverter_PT_WallThickness:
            aProcessor = MTKConverter_WallThicknessProcessor(800)
            MTKConverter_Application.__ApplyProcessorToModel(aProcessor, theModel, theReport)
        else:
            return MTKConverter_ReturnCode.MTKConverter_RC_InvalidArgument
 
        return MTKConverter_ReturnCode.MTKConverter_RC_OK
 
    @staticmethod
    def __Export(theFolderPath: mtk.UTF16String,
                 theModel: mtk.ModelData_Model,
                 theToGenerateScreenshot: bool,
                 theReport: MTKConverter_Report,
                 theProcessModel: mtk.ModelData_Model):
        print("Exporting ", theFolderPath, "...", sep="", end="")
 
        os.mkdir(theFolderPath)
 
        aModelPath = theFolderPath + "/" + str(theModel.Name()) + ".mtkweb" + "/scenegraph.mtkweb"
        if not theModel.Save(mtk.UTF16String(aModelPath), mtk.ModelData_Model.FileFormatType_MTKWEB):
            print("\nERROR: Failed to export ", aModelPath, ". Exiting", sep="")
            return MTKConverter_ReturnCode.MTKConverter_RC_ExportError
 
        aThumbnailPath = theFolderPath + "/thumbnail.png"
        if theToGenerateScreenshot and not MTKConverter_Application.__CreateOriginModelThumbnail(mtk.UTF16String(aThumbnailPath), theModel):
            print("\nERROR: Failed to create thumbnail ", aThumbnailPath, ". Exiting", sep="")
            return MTKConverter_ReturnCode.ExportError
 
        if not theProcessModel.IsEmpty():
            aProcessModelPath = theFolderPath + "/" + str(theProcessModel.Name()) + ".mtkweb" + "/scenegraph.mtkweb"
            if not theProcessModel.Save(mtk.UTF16String(aProcessModelPath), mtk.ModelData_Model.FileFormatType_MTKWEB):
                print("\nERROR: Failed to export ", aProcessModelPath, ". Exiting", sep="")
                return MTKConverter_ReturnCode.MTKConverter_RC_ExportError
 
        aJsonPath = theFolderPath + "\\process_data.json"
        if not theReport.WriteToJSON (aJsonPath):
            print("\nERROR: Failed to create JSON file ", aJsonPath, ". Exiting", sep="")
            return MTKConverter_ReturnCode.MTKConverter_RC_ExportError
 
        return MTKConverter_ReturnCode.MTKConverter_RC_OK
 
    def Run(self, theSource: str, theProcess: str, theTarget: str, theToGenerateScreenshot: str = ""):
        aModel = mtk.ModelData_Model()
        aProcessModel = mtk.ModelData_Model()
        aReport = MTKConverter_Report()
        aToGenerateScreenshot = True
 
        if theToGenerateScreenshot == "--no-screenshot":
            aToGenerateScreenshot = False
        aRes = MTKConverter_ReturnCode.MTKConverter_RC_OK
        try:
            aRes = MTKConverter_Application.__Import (theSource, aModel)
            print("Done.")
            if aRes == MTKConverter_ReturnCode.MTKConverter_RC_OK:
                aRes = MTKConverter_Application.__Process (theProcess, aModel, aReport, aProcessModel)
                print("Done.")
            if aRes == MTKConverter_ReturnCode.MTKConverter_RC_OK:
                aRes = MTKConverter_Application.__Export (theTarget, aModel, aToGenerateScreenshot, aReport, aProcessModel)
                print("Done.")
        except Exception as anE:
            print("Failed.\nERROR: ", anE, sep="")
            return MTKConverter_ReturnCode.MTKConverter_RC_GeneralException
        except:
            print("Failed.\nERROR: Unhandled exception caught.")
            return MTKConverter_ReturnCode.MTKConverter_RC_GeneralException
 
        return aRes