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


import os
import sys
import json
import uuid
from pathlib import Path

import manufacturingtoolkit.CadExMTK as mtk

# Search paths
sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../"))
sys.path.append(os.path.abspath(os.path.dirname(Path(__file__).resolve()) + "/../../helpers/"))

import mtk_license as license
import shape_processor
import feature_group

def compute_whole_part_measurements(theSolid):
    measurements = {
        "volume": {"name": "Volume", "units": "mm³", "value": "N/A"},
        "surfaceArea": {"name": "Surface Area", "units": "mm²", "value": "N/A"},
        "centroid": {"name": "Centroid", "units": "mm", "value": "N/A"},
    }
    try:
        shape = theSolid
        if not shape:
            print("[WARNING] No solid shape available for whole-part measurements")
            return measurements

        try:
            volume = mtk.Measurements_Volume.Compute(shape)
            if volume > 0:
                measurements["volume"]["value"] = round(volume, 3)
                print(f"[SUCCESS] Computed volume: {measurements['volume']['value']} mm^3")
        except Exception as e:
            print(f"[WARNING] Volume computation failed: {e}")

        try:
            area = mtk.Measurements_SurfaceArea.Compute(shape)
            if area > 0:
                measurements["surfaceArea"]["value"] = round(area, 3)
                print(f"[SUCCESS] Computed surface area: {measurements['surfaceArea']['value']} mm^2")
        except Exception as e:
            print(f"[WARNING] Surface area computation failed: {e}")

        try:
            centroid = mtk.Measurements_ValidationProperties.ComputeCentroid(shape)
            measurements["centroid"]["value"] = f"({centroid.X():.3f}, {centroid.Y():.3f}, {centroid.Z():.3f})"
            print(f"[SUCCESS] Computed centroid: {measurements['centroid']['value']}")
        except Exception as e:
            print(f"[WARNING] Centroid computation failed: {e}")

    except Exception as e:
        print(f"[WARNING] Error accessing solid shape for measurements: {e}")

    return measurements

def FaceTypeToString(theType):
    aFaceTypeMap = {
        mtk.Machining_FT_FlatFaceMilled:           "Flat Face Milled Face(s)",
        mtk.Machining_FT_FlatSideMilled:           "Flat Side Milled Face(s)",
        mtk.Machining_FT_CurvedMilled:             "Curved Milled Face(s)",
        mtk.Machining_FT_CircularMilled:           "Circular Milled Face(s)",
        mtk.Machining_FT_ConvexProfileEdgeMilling: "Convex Profile Edge Milling Face(s)",
        mtk.Machining_FT_ConcaveFilletEdgeMilling: "Concave Fillet Edge Milling Face(s)",
        mtk.Machining_FT_FlatMilled:               "Flat Milled Face(s)",
        mtk.Machining_FT_TurnDiameter:             "Turn Diameter Face(s)",
        mtk.Machining_FT_TurnForm:                 "Turn Form Face(s)",
        mtk.Machining_FT_TurnFace:                 "Turn Face Face(s)",
    }
    return aFaceTypeMap.get(theType, "Face(s)")

def PocketTypeToString(theType):
    aPocketTypeMap = {
        mtk.Machining_PT_Closed:   "Closed Pocket(s)",
        mtk.Machining_PT_Open:     "Open Pocket(s)",
        mtk.Machining_PT_Through:  "Through Pocket(s)",
    }
    return aPocketTypeMap.get(theType, "Pocket(s)")

def HoleTypeToString(theType):
    aHoleTypeMap = {
        mtk.Machining_HT_Through:    "Through Hole(s)",
        mtk.Machining_HT_FlatBottom: "Flat Bottom Hole(s)",
        mtk.Machining_HT_Blind:      "Blind Hole(s)",
        mtk.Machining_HT_Partial:    "Partial Hole(s)",
    }
    return aHoleTypeMap.get(theType, "Hole(s)")

def TurningGrooveTypeToString(theType):
    aTurningGrooveTypeMap = {
        mtk.Machining_TGT_OuterDiameter: "Outer Diameter Groove(s)",
        mtk.Machining_TGT_InnerDiameter: "Inner Diameter Groove(s)",
        mtk.Machining_TGT_EndFace:       "End Face Groove(s)",
    }
    return aTurningGrooveTypeMap.get(theType, "Turning Groove(s)")

def GetFeatureParameters(theFeature: mtk.MTKBase_Feature):
    # Same as your working version: collect feature parameters for console printing
    params = []
    if mtk.Machining_TurningFace.CompareType(theFeature):
        aTurningFace = mtk.Machining_TurningFace.Cast(theFeature)
        params.append(("radius", aTurningFace.Radius(), "mm"))
    elif mtk.Machining_Countersink.CompareType(theFeature):
        aCountersink = mtk.Machining_Countersink.Cast(theFeature)
        anAxis = aCountersink.Axis().Axis()
        params.extend([
            ("radius", aCountersink.Radius(), "mm"),
            ("depth", aCountersink.Depth(), "mm"),
            ("axis", f"({anAxis.X():.3f}, {anAxis.Y():.3f}, {anAxis.Z():.3f})", ""),
        ])
    elif mtk.Machining_ThreadedHole.CompareType(theFeature):
        aThreadedHole = mtk.Machining_ThreadedHole.Cast(theFeature)
        anAxis = aThreadedHole.Axis().Axis()
        params.extend([
            ("minor radius", aThreadedHole.MinorRadius(), "mm"),
            ("major radius", aThreadedHole.MajorRadius(), "mm"),
            ("thread length", aThreadedHole.ThreadLength(), "mm"),
            ("pitch", aThreadedHole.Pitch(), "mm"),
            ("depth", aThreadedHole.Depth(), "mm"),
            ("axis", f"({anAxis.X():.3f}, {anAxis.Y():.3f}, {anAxis.Z():.3f})", ""),
        ])
    elif mtk.Machining_Hole.CompareType(theFeature):
        aHole = mtk.Machining_Hole.Cast(theFeature)
        anAxis = aHole.Axis().Axis()
        params.extend([
            ("radius", aHole.Radius(), "mm"),
            ("depth", aHole.Depth(), "mm"),
            ("axis", f"({anAxis.X():.3f}, {anAxis.Y():.3f}, {anAxis.Z():.3f})", ""),
        ])
    elif mtk.Machining_SteppedHole.CompareType(theFeature):
        aSteppedHole = mtk.Machining_SteppedHole.Cast(theFeature)
        params.append(("depth", aSteppedHole.Depth(), "mm"))
    elif mtk.Machining_Pocket.CompareType(theFeature):
        aPocket = mtk.Machining_Pocket.Cast(theFeature)
        anAxis = aPocket.Axis().Direction()
        params.extend([
            ("length", aPocket.Length(), "mm"),
            ("width", aPocket.Width(), "mm"),
            ("depth", aPocket.Depth(), "mm"),
            ("axis", f"({anAxis.X():.3f}, {anAxis.Y():.3f}, {anAxis.Z():.3f})", ""),
        ])
    elif mtk.MTKBase_Boss.CompareType(theFeature):
        aBoss = mtk.MTKBase_Boss.Cast(theFeature)
        params.extend([
            ("length", aBoss.Length(), "mm"),
            ("width", aBoss.Width(), "mm"),
            ("height", aBoss.Height(), "mm"),
        ])
    elif mtk.Machining_TurningGroove.CompareType(theFeature):
        aTurningGroove = mtk.Machining_TurningGroove.Cast(theFeature)
        params.extend([
            ("radius", aTurningGroove.Radius(), "mm"),
            ("depth", aTurningGroove.Depth(), "mm"),
            ("width", aTurningGroove.Width(), "mm"),
        ])
    elif mtk.Machining_Bore.CompareType(theFeature):
        aBore = mtk.Machining_Bore.Cast(theFeature)
        params.extend([
            ("radius", aBore.Radius(), "mm"),
            ("depth", aBore.Depth(), "mm"),
        ])
    return params

def PrintFeatureParameters(theFeature: mtk.MTKBase_Feature):
    params = GetFeatureParameters(theFeature)
    for name, value, units in params:
        feature_group.FeatureGroupManager.PrintFeatureParameter(name, value, units)

def GroupByParameters(theFeatures: mtk.MTKBase_FeatureList, theManager: feature_group.FeatureGroupManager):
    for aFeature in theFeatures:
        if mtk.Machining_TurningFace.CompareType(aFeature):
            aTurningFace = mtk.Machining_TurningFace.Cast(aFeature)
            theManager.AddFeature(FaceTypeToString(aTurningFace.Type()), "Turning Face(s)", True, aFeature)
        elif mtk.Machining_Face.CompareType(aFeature):
            aFace = mtk.Machining_Face.Cast(aFeature)
            theManager.AddFeature(FaceTypeToString(aFace.Type()), "", False, aFeature)
        elif mtk.Machining_Countersink.CompareType(aFeature):
            theManager.AddFeature("Countersink(s)", "Countersink(s)", True, aFeature)
        elif mtk.Machining_ThreadedHole.CompareType(aFeature):
            aThreadedHole = mtk.Machining_ThreadedHole.Cast(aFeature)
            aGroupName = "Threaded " + HoleTypeToString(aThreadedHole.Type())
            theManager.AddFeature(aGroupName, "Threaded Hole(s)", True, aFeature)
        elif mtk.Machining_Hole.CompareType(aFeature):
            aHole = mtk.Machining_Hole.Cast(aFeature)
            theManager.AddFeature(HoleTypeToString(aHole.Type()), "Hole(s)", True, aFeature)
        elif mtk.Machining_SteppedHole.CompareType(aFeature):
            theManager.AddFeature("Stepped Hole(s)", "Stepped Hole(s)", True, aFeature)
        elif mtk.Machining_Pocket.CompareType(aFeature):
            aPocket = mtk.Machining_Pocket.Cast(aFeature)
            theManager.AddFeature(PocketTypeToString(aPocket.Type()), "", True, aFeature)
        elif mtk.MTKBase_Boss.CompareType(aFeature):
            theManager.AddFeature("Boss(es)", "Boss(es)", True, aFeature)
        elif mtk.Machining_TurningGroove.CompareType(aFeature):
            aTurningGroove = mtk.Machining_TurningGroove.Cast(aFeature)
            theManager.AddFeature(TurningGrooveTypeToString(aTurningGroove.Type()), "", True, aFeature)
        elif mtk.Machining_Bore.CompareType(aFeature):
            theManager.AddFeature("Bore(s)", "", True, aFeature)

def PrintFeatures(theFeatureList: mtk.MTKBase_FeatureList):
    aManager = feature_group.FeatureGroupManager()
    GroupByParameters(theFeatureList, aManager)
    aManager.Print("features", PrintFeatureParameters)

class PartProcessor(shape_processor.SolidProcessor):
    def __init__(self, operationType, outputFolder, partId):
        super().__init__()
        self._op = operationType
        self._output = Path(outputFolder)
        self._partId = partId
        self._features = []
        self._solids = []

    def ProcessSolid(self, theSolid: mtk.ModelData_Solid):
        print("[INFO] Processing solid for feature recognition...")
        recog = mtk.Machining_FeatureRecognizer()
        recog.Parameters().SetOperation(self._op)
        aFeatureList = recog.Perform(theSolid)
        print("[SUCCESS] Feature recognition completed")
        PrintFeatures(aFeatureList)
        self._features.append(aFeatureList)
        self._solids.append(theSolid)

    def ExportMeasurementsOnly(self):
        if not self._solids:
            print("[WARNING] No solids found; skipping measurements export")
            return
        # Compute once from first processed solid
        meas = compute_whole_part_measurements(self._solids[0])

        # Write separate, non-breaking file
        out = {
            "version": "1",
            "partId": self._partId,
            "measurements": meas,
        }
        out_file = self._output / "process_metrics.json"
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=4)
            print(f"[SUCCESS] Wrote measurements to: {out_file}")
        except Exception as e:
            print(f"[ERROR] Failed writing process_metrics.json: {e}")

def PrintSupportedOperations():
    print("Supported operations:")
    print("    milling:  CNC Machining Milling feature recognition")
    print("    turning:  CNC Machining Lathe+Milling feature recognition")

def OperationType(theOperationStr: str):
    aProcessMap = {
        "milling": mtk.Machining_OT_Milling,
        "turning": mtk.Machining_OT_LatheMilling,
    }
    return aProcessMap.get(theOperationStr, mtk.Machining_OT_Undefined)

def main(theSource: str, theOperationStr: str):
    print("[INFO] Activating MTK license...")
    aKey = license.Value()
    if not mtk.LicenseManager.Activate(aKey):
        print("[ERROR] Failed to activate Manufacturing Toolkit license.")
        return 1
    print("[SUCCESS] MTK license activated")

    aModel = mtk.ModelData_Model()
    aReader = mtk.ModelData_ModelReader()

    print(f"[INFO] Reading model from: {theSource}")
    if not aReader.Read(mtk.UTF16String(theSource), aModel):
        print("[ERROR] Failed to open and convert the file " + theSource)
        return 1
    print(f"[SUCCESS] Model loaded: {aModel.Name()}")

    anOperation = OperationType(theOperationStr)
    if anOperation == mtk.Machining_OT_Undefined:
        print("[ERROR] Unsupported operation:", theOperationStr)
        PrintSupportedOperations()
        return 1

    source_path = Path(theSource)
    output_folder = source_path.parent / f"{source_path.stem}_mtk"
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output folder: {output_folder}")

    part_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{source_path.stem}_{theOperationStr}"))
    print(f"[INFO] Part ID: {part_id}")

    print(f"[INFO] Starting feature recognition ({theOperationStr})...")
    proc = PartProcessor(anOperation, output_folder, part_id)
    visitor = mtk.ModelData_ModelElementUniqueVisitor(proc)
    aModel.Accept(visitor)

    # Write only measurements to separate file; do NOT touch process_data.json
    proc.ExportMeasurementsOnly()

    return 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: feature_recognizer.py <input_file> <operation>")
        PrintSupportedOperations()
        sys.exit(1)
    aSource = os.path.abspath(sys.argv[1])
    anOperation = sys.argv[2]
    sys.exit(main(aSource, anOperation))