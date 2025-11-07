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


import sys
import os
import json
import math
from enum import Enum

# Add the MTK python path
mtk_path = r'C:\MTK\python'
if mtk_path not in sys.path:
    sys.path.insert(0, mtk_path)

import MTK

# ============================
# FEATURE TYPES
# ============================
class FeatureType(Enum):
    THROUGH_HOLE = "Through Hole"
    BLIND_HOLE = "Blind Hole"
    FLAT_SIDE_MILLED_FACE = "Flat Side Milled Face"
    CURVED_MILLED_FACE = "Curved Milled Face"
    CIRCULAR_MILLED_FACE = "Circular Milled Face"
    POCKET = "Pocket"
    SLOT = "Slot"
    BOSS = "Boss"
    CHAMFER = "Chamfer"
    FILLET = "Fillet"
    UNKNOWN = "Unknown Feature"

# ============================
# HELPER FUNCTIONS
# ============================
def get_feature_shape(theFeature):
    """
    Extract the geometric shape from a feature using MTK API.
    Returns the shape object or None if unavailable.
    """
    try:
        feature_type = type(theFeature).__name__
        
        if feature_type == "ThroughHoleFeature":
            return theFeature.GetHoleShape()
        elif feature_type == "BlindHoleFeature":
            return theFeature.GetHoleShape()
        elif feature_type == "PocketFeature":
            return theFeature.GetPocketShape()
        elif feature_type == "SlotFeature":
            return theFeature.GetSlotShape()
        elif feature_type == "BossFeature":
            return theFeature.GetBossShape()
        elif feature_type == "ChamferFeature":
            return theFeature.GetChamferFaces()
        elif feature_type == "FilletFeature":
            return theFeature.GetFilletFaces()
        elif feature_type == "FlatSideMilledFaceFeature":
            return theFeature.GetFace()
        elif feature_type == "CurvedMilledFaceFeature":
            return theFeature.GetFace()
        elif feature_type == "CircularMilledFaceFeature":
            return theFeature.GetFace()
        else:
            print(f"[WARNING] Unknown feature type for shape extraction: {feature_type}")
            return None
            
    except Exception as e:
        print(f"[WARNING] Could not get shape for feature type {type(theFeature).__name__}: {e}")
        return None

def compute_feature_measurements(theFeature):
    """
    Compute volume, surface area, and centroid for a given feature.
    Returns a dict with 'volume', 'surface_area', 'centroid' or "N/A" if unavailable.
    """
    measurements = {
        'volume': "N/A",
        'surface_area': "N/A",
        'centroid': "N/A"
    }
    
    try:
        shape = get_feature_shape(theFeature)
        if shape is None:
            print(f"[WARNING] No shape available for feature {type(theFeature).__name__}")
            return measurements
        
        # Compute volume
        try:
            gprops = MTK.GProp_GProps()
            MTK.BRepGProp.VolumeProperties_s(shape, gprops)
            volume = gprops.Mass()
            measurements['volume'] = f"{volume:.3f}"
        except Exception as e:
            print(f"[WARNING] Could not compute volume: {e}")
        
        # Compute surface area
        try:
            gprops = MTK.GProp_GProps()
            MTK.BRepGProp.SurfaceProperties_s(shape, gprops)
            surface_area = gprops.Mass()
            measurements['surface_area'] = f"{surface_area:.3f}"
        except Exception as e:
            print(f"[WARNING] Could not compute surface area: {e}")
        
        # Compute centroid
        try:
            gprops = MTK.GProp_GProps()
            MTK.BRepGProp.VolumeProperties_s(shape, gprops)
            centroid = gprops.CentreOfMass()
            measurements['centroid'] = f"({centroid.X():.3f}, {centroid.Y():.3f}, {centroid.Z():.3f})"
        except Exception as e:
            print(f"[WARNING] Could not compute centroid: {e}")
            
    except Exception as e:
        print(f"[WARNING] Error computing measurements for feature: {e}")
    
    return measurements

def merge_feature_measurements_into_json(output_folder, features_with_measurements):
    """
    Read the existing process_data.json, locate features in the nested structure,
    and inject computed measurements into each feature's parameters array.
    """
    json_path = os.path.join(output_folder, "process_data.json")
    
    if not os.path.exists(json_path):
        print(f"[WARNING] process_data.json not found at {json_path}")
        return
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Navigate to the feature groups
        if "parts" not in data or len(data["parts"]) == 0:
            print("[WARNING] No parts found in process_data.json")
            return
        
        part = data["parts"][0]
        if "featureRecognition" not in part:
            print("[WARNING] No featureRecognition found in process_data.json")
            return
        
        if "featureGroups" not in part["featureRecognition"]:
            print("[WARNING] No featureGroups found in process_data.json")
            return
        
        feature_groups = part["featureRecognition"]["featureGroups"]
        
        # Counter to match features by index
        feature_index = 0
        total_features_in_json = 0
        
        # Iterate through feature groups
        for group in feature_groups:
            # Check if group has subGroups or features directly
            if "subGroups" in group:
                # Complex group with subgroups
                for subgroup in group["subGroups"]:
                    if "features" in subgroup:
                        for feature in subgroup["features"]:
                            total_features_in_json += 1
                            if feature_index < len(features_with_measurements):
                                measurements = features_with_measurements[feature_index]
                                
                                # Initialize parameters array if it doesn't exist
                                if "parameters" not in feature:
                                    feature["parameters"] = []
                                
                                # Add measurements to parameters
                                if measurements['volume'] != "N/A":
                                    feature["parameters"].append({
                                        "name": "Volume",
                                        "units": "mm^3",
                                        "value": measurements['volume']
                                    })
                                
                                if measurements['surface_area'] != "N/A":
                                    feature["parameters"].append({
                                        "name": "Surface Area",
                                        "units": "mm^2",
                                        "value": measurements['surface_area']
                                    })
                                
                                if measurements['centroid'] != "N/A":
                                    feature["parameters"].append({
                                        "name": "Centroid",
                                        "units": "mm",
                                        "value": measurements['centroid']
                                    })
                                
                                feature_index += 1
            
            elif "features" in group:
                # Simple group with features directly
                for feature in group["features"]:
                    total_features_in_json += 1
                    if feature_index < len(features_with_measurements):
                        measurements = features_with_measurements[feature_index]
                        
                        # Initialize parameters array if it doesn't exist
                        if "parameters" not in feature:
                            feature["parameters"] = []
                        
                        # Add measurements to parameters
                        if measurements['volume'] != "N/A":
                            feature["parameters"].append({
                                "name": "Volume",
                                "units": "mm^3",
                                "value": measurements['volume']
                            })
                        
                        if measurements['surface_area'] != "N/A":
                            feature["parameters"].append({
                                "name": "Surface Area",
                                "units": "mm^2",
                                "value": measurements['surface_area']
                            })
                        
                        if measurements['centroid'] != "N/A":
                            feature["parameters"].append({
                                "name": "Centroid",
                                "units": "mm",
                                "value": measurements['centroid']
                            })
                        
                        feature_index += 1
        
        # Check for feature count mismatch
        if feature_index != len(features_with_measurements):
            print(f"[WARNING] Feature count mismatch: {feature_index} features in JSON, {len(features_with_measurements)} features processed")
        
        if total_features_in_json != len(features_with_measurements):
            print(f"[WARNING] Total features in JSON ({total_features_in_json}) doesn't match processed features ({len(features_with_measurements)})")
        
        # Write updated JSON back
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[SUCCESS] Injected measurements for {feature_index} features into process_data.json")
        
    except Exception as e:
        print(f"[ERROR] Failed to merge measurements into JSON: {e}")
        import traceback
        traceback.print_exc()

# ============================
# PART PROCESSOR CLASS
# ============================
class PartProcessor:
    def __init__(self, theModel, thePartId, theOutput):
        self._model = theModel
        self._part_id = thePartId
        self._output_folder = theOutput
        self._features = {}
        self._features_with_measurements = []  # Store features with their measurements
        self._whole_part_measurements = {
            'volume': None,
            'surface_area': None,
            'centroid': None
        }
        
    def ProcessSolid(self, theSolid):
        print("[INFO] Processing solid for feature recognition...")
        
        recognizer = MTK.FeatureRecognizer()
        recognizer.SetProcessType(MTK.FeatureRecognizer.ProcessType.Milling)
        recognizer.Recognize(theSolid)
        
        features = recognizer.GetFeatures()
        print(f"[SUCCESS] Feature recognition completed")
        
        # Group and count features
        for feature in features:
            feature_name = self._get_feature_name(feature)
            if feature_name not in self._features:
                self._features[feature_name] = []
            self._features[feature_name].append(feature)
        
        print("[INFO] Computing per-feature measurements...")
        
        # Compute measurements for each feature
        for feature_name, feature_list in self._features.items():
            for feature in feature_list:
                measurements = compute_feature_measurements(feature)
                self._features_with_measurements.append(measurements)
        
        print(f"[SUCCESS] Computed measurements for {len(self._features_with_measurements)} features")
        
        # Print feature summary with grouped parameters
        self._print_feature_summary()
    
    def _get_feature_name(self, theFeature):
        feature_type = type(theFeature).__name__
        
        if feature_type == "ThroughHoleFeature":
            return FeatureType.THROUGH_HOLE.value
        elif feature_type == "BlindHoleFeature":
            return FeatureType.BLIND_HOLE.value
        elif feature_type == "FlatSideMilledFaceFeature":
            return FeatureType.FLAT_SIDE_MILLED_FACE.value
        elif feature_type == "CurvedMilledFaceFeature":
            return FeatureType.CURVED_MILLED_FACE.value
        elif feature_type == "CircularMilledFaceFeature":
            return FeatureType.CIRCULAR_MILLED_FACE.value
        elif feature_type == "PocketFeature":
            return FeatureType.POCKET.value
        elif feature_type == "SlotFeature":
            return FeatureType.SLOT.value
        elif feature_type == "BossFeature":
            return FeatureType.BOSS.value
        elif feature_type == "ChamferFeature":
            return FeatureType.CHAMFER.value
        elif feature_type == "FilletFeature":
            return FeatureType.FILLET.value
        else:
            return FeatureType.UNKNOWN.value
    
    def _print_feature_summary(self):
        """Print a summary of features with grouped parameters"""
        for feature_name, feature_list in self._features.items():
            print(f"    {feature_name}(s): {len(feature_list)}")
            
            # Group features by similar parameters
            if feature_name == FeatureType.THROUGH_HOLE.value or feature_name == FeatureType.BLIND_HOLE.value:
                self._print_hole_groups(feature_list)
    
    def _print_hole_groups(self, holes):
        """Group holes by radius, depth, and axis"""
        hole_groups = {}
        
        for hole in holes:
            try:
                shape = hole.GetHoleShape()
                axis = hole.GetAxis()
                
                # Get radius and depth
                radius = None
                depth = None
                
                if hasattr(hole, 'GetRadius'):
                    radius = hole.GetRadius()
                
                if hasattr(hole, 'GetDepth'):
                    depth = hole.GetDepth()
                elif type(hole).__name__ == "ThroughHoleFeature":
                    # For through holes, estimate depth from bounding box
                    bbox = MTK.Bnd_Box()
                    MTK.BRepBndLib.Add_s(shape, bbox)
                    if not bbox.IsVoid():
                        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
                        depth = max(xmax - xmin, ymax - ymin, zmax - zmin)
                
                # Create a key for grouping
                axis_str = f"({axis.X():.3f}, {axis.Y():.3f}, {axis.Z():.3f})"
                
                # Round values for grouping
                radius_rounded = round(radius, 5) if radius else None
                depth_rounded = round(depth, 1) if depth else None
                
                key = (radius_rounded, depth_rounded, axis_str)
                
                if key not in hole_groups:
                    hole_groups[key] = []
                hole_groups[key].append(hole)
                
            except Exception as e:
                print(f"        [WARNING] Could not process hole: {e}")
        
        # Print grouped holes
        for (radius, depth, axis_str), group_holes in hole_groups.items():
            print(f"        {len(group_holes)} Hole(s) with")
            if radius is not None:
                print(f"          radius: {radius} mm")
            if depth is not None:
                print(f"          depth: {depth} mm")
            print(f"          axis: {axis_str} ")
    
    def ComputeWholePart(self, theSolid):
        """Compute volume, surface area, and centroid for the whole part"""
        try:
            # Volume
            gprops_vol = MTK.GProp_GProps()
            MTK.BRepGProp.VolumeProperties_s(theSolid, gprops_vol)
            volume = gprops_vol.Mass()
            self._whole_part_measurements['volume'] = volume
            print(f"[SUCCESS] Computed volume: {volume:.3f} mm^3")
            
            # Surface Area
            gprops_surf = MTK.GProp_GProps()
            MTK.BRepGProp.SurfaceProperties_s(theSolid, gprops_surf)
            surface_area = gprops_surf.Mass()
            self._whole_part_measurements['surface_area'] = surface_area
            print(f"[SUCCESS] Computed surface area: {surface_area:.3f} mm^2")
            
            # Centroid
            centroid = gprops_vol.CentreOfMass()
            centroid_str = f"({centroid.X():.3f}, {centroid.Y():.3f}, {centroid.Z():.3f})"
            self._whole_part_measurements['centroid'] = centroid_str
            print(f"[SUCCESS] Computed centroid: {centroid_str}")
            
        except Exception as e:
            print(f"[ERROR] Failed to compute whole-part measurements: {e}")
    
    def ExportMeasurementsOnly(self):
        """Export only the whole-part measurements to process_metrics.json"""
        output_path = os.path.join(self._output_folder, "process_metrics.json")
        
        try:
            data = {
                "volume": self._whole_part_measurements['volume'],
                "surface_area": self._whole_part_measurements['surface_area'],
                "centroid": self._whole_part_measurements['centroid']
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[SUCCESS] Wrote whole-part measurements to: {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to write measurements: {e}")
    
    def ExportFeatureMeasurements(self):
        """Merge per-feature measurements into the existing process_data.json"""
        merge_feature_measurements_into_json(self._output_folder, self._features_with_measurements)
    
    def GetFeatureCount(self):
        """Return total count of all features"""
        return sum(len(features) for features in self._features.values())

# ============================
# MAIN FUNCTION
# ============================
def main():
    if len(sys.argv) < 3:
        print("Usage: python feature_recognizer.py <model_path> <output_folder>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    output_folder = sys.argv[2]
    
    try:
        # Activate license
        print("[INFO] Activating MTK license...")
        key = MTK.LicenseKey()
        key.SetKey(r"C:\MTK\license\Eval_CADInterfacesAndProcessingToolkit.key")
        MTK.UnlockLicense(key)
        print("[SUCCESS] MTK license activated")
        
        # Read model
        print(f"[INFO] Reading model from: {model_path}")
        model = MTK.Model()
        modelName = model.ReadFile(model_path)
        print(f"[SUCCESS] Model loaded: {modelName}")
        
        print(f"[INFO] Output folder: {output_folder}")
        
        # Process each part
        for part_idx in range(model.GetPartCount()):
            part = model.GetPart(part_idx)
            part_id = part.GetId()
            print(f"[INFO] Part ID: {part_id}")
            
            print(f"[INFO] Starting feature recognition (milling)...")
            print(f'Part #{part_idx} ["{part.GetName()}"] - solid #{0} has:')
            
            # Create processor
            proc = PartProcessor(model, part_id, output_folder)
            
            # Process solids
            for solid_idx in range(part.GetSolidCount()):
                solid = part.GetSolid(solid_idx)
                
                # Compute whole-part measurements
                proc.ComputeWholePart(solid)
                
                # Recognize features
                proc.ProcessSolid(solid)
            
            # Print total
            total_features = proc.GetFeatureCount()
            print(f"\n    Total features: {total_features}\n")
            
            # Export whole-part measurements to process_metrics.json
            proc.ExportMeasurementsOnly()
            
            # Inject per-feature measurements into process_data.json
            proc.ExportFeatureMeasurements()
        
    except Exception as e:
        print(f"[ERROR] Feature recognition failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
