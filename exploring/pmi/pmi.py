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

class TabulatedOutput:
    myNestingLevel = 0

    @classmethod
    def WriteLine(cls, theObject: str):
        cls.PrintTabulation()
        print(theObject)

    @classmethod
    def IncreaseIndent(cls):
       cls.myNestingLevel += 1

    @classmethod
    def DecreaseIndent(cls):
        cls.myNestingLevel -= 1

    @classmethod
    def PrintTabulation(cls):
        if cls.myNestingLevel <= 0:
            return
        # Emulate tabulation like tree.
        for i in range(cls.myNestingLevel - 1):
            if i < 2 or i == 3:
                print("|  ", end="")
            else:
                print("   ", end="")
        print("|__", end="")
        if cls.myNestingLevel > 3:
            print(" ", end="")

class SceneGraphVisitor(mtk.ModelData_ModelElementVisitor):
    def VisitPart(self, thePart: mtk.ModelData_Part):
        self.PrintName("Part", thePart.Name())
        self.ExplorePMI(thePart)

    def VisitEnterInstance(self, theInstance: mtk.ModelData_Instance):
        TabulatedOutput.IncreaseIndent()
        self.PrintName("Instance", theInstance.Name())
        self.ExplorePMI(theInstance)
        return True

    def VisitEnterAssembly(self, theAssembly: mtk.ModelData_Assembly):
        TabulatedOutput.IncreaseIndent()
        self.PrintName("Assembly", theAssembly.Name())
        self.ExplorePMI(theAssembly)
        return True

    def VisitLeaveInstance(self, theInstance: mtk.ModelData_Instance):
        TabulatedOutput.DecreaseIndent()

    def VisitLeaveAssembly(self, theAssembly: mtk.ModelData_Assembly):
        TabulatedOutput.DecreaseIndent()

    def ExplorePMI(self, theSGE: mtk.ModelData_ModelElement):
        aPMIData : mtk.PMI_Data = theSGE.PMI()
        if aPMIData:
            TabulatedOutput.WriteLine("PMI Data:")
            TabulatedOutput.IncreaseIndent()
            
            anElements = aPMIData.Elements()
            for anElement in anElements:
                TabulatedOutput.WriteLine(f"PMI Element: {anElement.Name()}")

                TabulatedOutput.IncreaseIndent()

                aSemanticRepresentation = anElement.SemanticRepresentation()
                if aSemanticRepresentation:
                    TabulatedOutput.WriteLine("Semantic Representation:")
                    TabulatedOutput.IncreaseIndent()
                    aVisitor = PMISemanticVisitor()
                    aSemanticRepresentation.Accept(aVisitor)
                    TabulatedOutput.DecreaseIndent()

                aGraphicalRepresentation = anElement.GraphicalRepresentation()
                if aGraphicalRepresentation:
                    TabulatedOutput.WriteLine("Graphical Representation:")
                    TabulatedOutput.IncreaseIndent()
                    aVisitor = PMIGraphicalVisitor()
                    aGraphicalRepresentation.Accept(aVisitor)
                    TabulatedOutput.DecreaseIndent()

                TabulatedOutput.DecreaseIndent()
            TabulatedOutput.DecreaseIndent()

    def PrintName(self, theSGElement: str, theName: str):
        if theName:
            TabulatedOutput.WriteLine(f"{theSGElement}: {theName}")
        else:
            TabulatedOutput.WriteLine(f"{theSGElement}: <noname>")

class PMISemanticVisitor(mtk.PMI_SemanticComponentVisitor):
    def VisitDatumComponent(self, theComponent: mtk.PMI_DatumComponent):
        TabulatedOutput.WriteLine("Datum") 
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Label: {theComponent.Label()}")
        self.PrintAttributes(theComponent)
        TabulatedOutput.DecreaseIndent()

    def VisitDimensionComponent(self, theComponent: mtk.PMI_DimensionComponent):
        TabulatedOutput.WriteLine("Dimension")
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Nominal Value: {theComponent.NominalValue()}")
        TabulatedOutput.WriteLine(f"Type of dimension: {int(theComponent.TypeOfDimension())}")
        self.PrintAttributes(theComponent)
        TabulatedOutput.DecreaseIndent()

    def VisitGeometricToleranceComponent(self, theComponent: mtk.PMI_GeometricToleranceComponent):
        TabulatedOutput.WriteLine("Geometric tolerance")
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Magnitude: {theComponent.Magnitude()}")
        TabulatedOutput.WriteLine(f"Type of tolerance: {int(theComponent.TypeOfTolerance())}")
        TabulatedOutput.WriteLine(f"Tolerance zone form: {int(theComponent.ToleranceZoneForm())}")
        self.PrintAttributes(theComponent)
        TabulatedOutput.DecreaseIndent()
        
    def VisitSurfaceFinishComponent(self, theComponent: mtk.PMI_SurfaceFinishComponent):
        TabulatedOutput.WriteLine("Surface Finish")
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Material removal: {int(theComponent.MaterialRemoval())}")
        TabulatedOutput.WriteLine(f"Lay direction: {int(theComponent.LayDirection())}")
        TabulatedOutput.WriteLine(f"All around flag: {int(theComponent.IsAllAround())}")
        TabulatedOutput.WriteLine(f"Manufacturing method: {theComponent.ManufacturingMethod()}")
        self.PrintAttributes(theComponent)
        TabulatedOutput.DecreaseIndent()

    def PrintAttributes(self, theComponent: mtk.PMI_SemanticComponent):
        if theComponent.HasAttributes():
            aVisitor = PMISemanticAttributeVisitor()
            theComponent.Accept(aVisitor)

class PMISemanticAttributeVisitor(mtk.PMI_SemanticAttributeVisitor):
    def VisitModifierAttribute(self, theAttribute: mtk.PMI_ModifierAttribute):
        TabulatedOutput.WriteLine(f"Modifier: {theAttribute.Modifier()}")

    def VisitModifierWithValueAttribute(self, theAttribute: mtk.PMI_ModifierWithValueAttribute):
        TabulatedOutput.WriteLine(f"ModifierWithValue: modifier={theAttribute.Modifier()}, value={theAttribute.Value()}")
    
    def VisitQualifierAttribute(self, theAttribute: mtk.PMI_QualifierAttribute):
        TabulatedOutput.WriteLine(f"Qualifier: {theAttribute.Qualifier()}")

    def VisitPlusMinusBoundsAttribute(self, theAttribute: mtk.PMI_PlusMinusBoundsAttribute):
        TabulatedOutput.WriteLine(f"PlusMinusBounds: ({theAttribute.LowerBound()}, {theAttribute.UpperBound()})")
    
    def VisitRangeAttribute(self, theAttribute: mtk.PMI_RangeAttribute):
        TabulatedOutput.WriteLine(f"Range: [{theAttribute.LowerLimit()}, {theAttribute.UpperLimit()}]")

    def VisitLimitsAndFitsAttribute(self, theAttribute: mtk.PMI_LimitsAndFitsAttribute):
        TabulatedOutput.WriteLine(f"LimitsAndFits: value={theAttribute.Value()} + {type}={theAttribute.Type()}")

    def VisitDatumTargetAttribute(self, theAttribute: mtk.PMI_DatumTargetAttribute):
        TabulatedOutput.WriteLine(f"DatumTarget: index={theAttribute.Index()}, description={theAttribute.Description()}")

    def VisitDatumRefAttribute(self, theAttribute: mtk.PMI_DatumRefAttribute):
        TabulatedOutput.WriteLine(f"DatumRef: precedence={theAttribute.Precedence()}, targetLabel={theAttribute.TargetLabel()}")

    def VisitDatumRefCompartmentAttribute(self, theAttribute: mtk.PMI_DatumRefCompartmentAttribute):
        TabulatedOutput.WriteLine("DatumRefCompartment:")

        TabulatedOutput.IncreaseIndent()

        aNumberOfReferences = theAttribute.NumberOfReferences()
        if aNumberOfReferences > 0:
            TabulatedOutput.WriteLine("References:")
            TabulatedOutput.IncreaseIndent()
            for i in range(aNumberOfReferences):
                theAttribute.Reference(i).Accept(self)
            TabulatedOutput.DecreaseIndent()

        aNumberOfModifierAttributes = theAttribute.NumberOfModifierAttributes()
        if aNumberOfModifierAttributes > 0:
            TabulatedOutput.WriteLine("Modifiers:")
            TabulatedOutput.IncreaseIndent()
            for i in range(aNumberOfModifierAttributes):
                theAttribute.ModifierAttribute(i).Accept(self)
            TabulatedOutput.DecreaseIndent()

        TabulatedOutput.DecreaseIndent()

    def VisitMaximumValueAttribute(self, theAttribute: mtk.PMI_MaximumValueAttribute):
        TabulatedOutput.WriteLine(f"MaximumValue: {theAttribute.MaxValue()}")

    def VisitDisplacementAttribute(self, theAttribute: mtk.PMI_DisplacementAttribute):
        TabulatedOutput.WriteLine(f"Displacement: {theAttribute.Displacement()}")

    def VisitLengthUnitAttribute(self, theAttribute: mtk.PMI_LengthUnitAttribute):
        TabulatedOutput.WriteLine(f"LengthUnit: {theAttribute.Unit()}")

    def VisitAngleUnitAttribute(self, theAttribute: mtk.PMI_AngleUnitAttribute):
        TabulatedOutput.WriteLine(f"AngleUnit: {theAttribute.Unit()}")
        
    def VisitMachiningAllowanceAttribute(self, theAttribute: mtk.PMI_MachiningAllowanceAttribute):
        TabulatedOutput.WriteLine("Machining allowance")
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Value: {theAttribute.Value()}")
        TabulatedOutput.WriteLine(f"Upper bound: {theAttribute.UpperBound()}")
        TabulatedOutput.WriteLine(f"Lower bound: {theAttribute.LowerBound()}")
        TabulatedOutput.DecreaseIndent()

    def VisitSurfaceTextureRequirementAttribute(self, theAttribute: mtk.PMI_SurfaceTextureRequirementAttribute):
        TabulatedOutput.WriteLine(f"Surface texture requirement #: {int(theAttribute.Precedence())}")
        TabulatedOutput.IncreaseIndent()
        TabulatedOutput.WriteLine(f"Specification limit: {int(theAttribute.SpecificationLimit())}")
        TabulatedOutput.WriteLine(f"Filter name: {theAttribute.FilterName()}")
        TabulatedOutput.WriteLine(f"Short wave filter: {theAttribute.ShortWaveFilter()}")
        TabulatedOutput.WriteLine(f"Long wave filter: {theAttribute.LongWaveFilter()}")
        TabulatedOutput.WriteLine(f"Surface parameter: {int(theAttribute.SurfaceParameter())}")
        TabulatedOutput.WriteLine(f"Evaluation length: {theAttribute.EvaluationLength()}")
        TabulatedOutput.WriteLine(f"Comparison rule: {int(theAttribute.ComparisonRule())}")
        TabulatedOutput.WriteLine(f"Limit value: {theAttribute.LimitValue()}")
        TabulatedOutput.DecreaseIndent()         

class PMIGraphicalVisitor(mtk.PMI_GraphicalComponentVisitor):
    def VisitOutlinedComponent(self, theComponent: mtk.PMI_OutlinedComponent):
        TabulatedOutput.WriteLine("Outline")
        TabulatedOutput.IncreaseIndent()
        aVisitor = PMIOutlineVisitor()
        theComponent.Outline().Accept(aVisitor)
        TabulatedOutput.DecreaseIndent()

    def VisitTextComponent(self, theComponent: mtk.PMI_TextComponent):
        TabulatedOutput.WriteLine(f"Text [{theComponent.Text()}]")

    def VisitTriangulatedComponent(self, theComponent: mtk.PMI_TriangulatedComponent):
        TabulatedOutput.WriteLine(f"Triangulation [{theComponent.TriangleSet().NumberOfTriangles()} triangles]")

class PMIOutlineVisitor(mtk.PMI_OutlineVisitor):
    def VisitPolyOutline(self, theOutline: mtk.PMI_PolyOutline):
        TabulatedOutput.WriteLine(f"PolyLine set [{theOutline.LineSet().NumberOfPolylines()} polylines]")

    def VisitPoly2dOutline(self, theOutline: mtk.PMI_Poly2dOutline):
        TabulatedOutput.WriteLine(f"PolyLine2d set [{theOutline.LineSet().NumberOfPolylines()} polylines]")
    
    def VisitCurveOutline(self, theOutline: mtk.PMI_CurveOutline):
        TabulatedOutput.WriteLine(f"Curve set [{theOutline.NumberOfCurves()} curves]")
    
    def VisitCurve2dOutline(self, theOutline: mtk.PMI_Curve2dOutline):
        TabulatedOutput.WriteLine(f"Curve2d set [{theOutline.NumberOfCurves()} curves]")

    def VisitEnterCompositeOutline(self, theOutline: mtk.PMI_CompositeOutline):
        TabulatedOutput.WriteLine("Composite outline:")
        TabulatedOutput.IncreaseIndent()
        return True

    def VisitLeaveCompositeOutline(self, theOutline: mtk.PMI_CompositeOutline):
        TabulatedOutput.DecreaseIndent()

def main(theSource: str):
    aKey = license.Value()

    if not mtk.LicenseManager.Activate(aKey):
        print("Failed to activate Manufacturing Toolkit license.")
        return 1

    aModel = mtk.ModelData_Model()
    aReader = mtk.ModelData_ModelReader()
    aParams = mtk.ModelData_ModelReaderParameters()
    aParams.SetReadPMI(True)
    aReader.SetParameters(aParams)

    # Reading the file
    if not aReader.Read(mtk.UTF16String(theSource), aModel):
        print("Failed to open and convert the file " + theSource)
        return 1

    print("Model: ", aModel.Name(), "\n", sep="")

    # Create a PMI visitor
    aVisitor = SceneGraphVisitor()
    aModel.Accept(aVisitor)

    print("Completed")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: <input_file>, where:")
        print("    <input_file> is a name of the file to be read")
        sys.exit()

    aSource = os.path.abspath(sys.argv[1])

    sys.exit(main(aSource))
