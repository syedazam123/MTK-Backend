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
from pathlib import Path
import os

import manufacturingtoolkit.CadExMTK as mtk
from base_explorer import BaseExplorer

class CurveExplorer(BaseExplorer):
    # Prints curve type name and prints shape info in some cases
    @classmethod
    def PrintCurveInfo(cls, theCurve: mtk.Geom_Curve):
        if theCurve.Type() == mtk.CurveType_Line:
            cls.PrintLine(mtk.Geom_Line.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Circle:
            cls.PrintCircle(mtk.Geom_Circle.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Ellipse:
            cls.PrintEllipse(mtk.Geom_Ellipse.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Hyperbola:
            cls.PrintHyperbola(mtk.Geom_Hyperbola.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Parabola:
            cls.PrintParabola(mtk.Geom_Parabola.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Bezier:
            cls.PrintBezierCurve(mtk.Geom_BezierCurve.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_BSpline:
            cls.PrintBSplineCurve(mtk.Geom_BSplineCurve.Cast(theCurve))
        elif theCurve.Type() == mtk.CurveType_Offset:
            cls.PrintOffsetCurve(mtk.Geom_OffsetCurve.Cast(theCurve))

    @classmethod
    def PrintLine(cls, theLine: mtk.Geom_Line):
        cls.PrintName("Line")
        aLoc = theLine.Location()
        aDir = theLine.Direction()
        cls.PrintDomain(theLine)
        cls.PrintNamedParameter("Location",  aLoc)
        cls.PrintNamedParameter("Direction", aDir)

    @classmethod
    def PrintCircle(cls, theCircle: mtk.Geom_Circle):
        cls.PrintName("Circle")
        aRadius = theCircle.Radius()
        cls.PrintElementary(theCircle)
        cls.PrintNamedParameter("Radius", aRadius)

    @classmethod
    def PrintEllipse(cls, theEllipse: mtk.Geom_Ellipse):
        cls.PrintName("Ellipse")
        aMajorRadius = theEllipse.MajorRadius()
        aMinorRadius = theEllipse.MinorRadius()
        cls.PrintElementary(theEllipse)
        cls.PrintNamedParameter("Major Radius", aMajorRadius)
        cls.PrintNamedParameter("Minor Radius", aMinorRadius)

    @classmethod
    def PrintHyperbola(cls, theHyperbola: mtk.Geom_Hyperbola):
        cls.PrintName("Hyperbola")
        aMajorRadius = theHyperbola.MajorRadius()
        aMinorRadius = theHyperbola.MinorRadius()
        cls.PrintElementary(theHyperbola)
        cls.PrintNamedParameter("Major Radius", aMajorRadius)
        cls.PrintNamedParameter("Minor Radius", aMinorRadius)

    @classmethod
    def PrintParabola(cls, theParabola: mtk.Geom_Parabola):
        cls.PrintName("Parabola")
        aFocal = theParabola.Focal()
        cls.PrintElementary(theParabola)
        cls.PrintNamedParameter("Focal", aFocal)

    @classmethod
    def PrintBezierCurve(cls, theBezier: mtk.Geom_BezierCurve):
        cls.PrintName("Bezier Curve")
        aDegree = theBezier.Degree()
        aNumberOfPoles = theBezier.NumberOfPoles()
        cls.PrintDomain(theBezier)
        cls.PrintNamedParameter("Degree",          aDegree)
        cls.PrintNamedParameter("Number Of Poles", aNumberOfPoles)

        def PrintPole(i):
            aPole = theBezier.Pole(i)
            cls.PrintParameter(aPole)

        cls.Print2dCollection("Poles", aNumberOfPoles, PrintPole)

        def PrintWeight(i):
            aWeight = theBezier.Weight(i)
            cls.PrintParameter(aWeight)

        cls.Print2dCollection("Weights", aNumberOfPoles, PrintWeight)

    @classmethod
    def PrintBSplineCurve(cls, theBSpline: mtk.Geom_BSplineCurve):
        cls.PrintName("BSpline Curve")
        aDegree = theBSpline.Degree()
        aNumberOfKnots = theBSpline.NumberOfKnots()
        aNumberOfPoles = theBSpline.NumberOfPoles()
        cls.PrintDomain(theBSpline)
        cls.PrintNamedParameter("Degree", aDegree)
        cls.PrintNamedParameter("Number Of Knots", aNumberOfKnots)
        cls.PrintNamedParameter("Number Of Poles", aNumberOfPoles)

        def PrintKnot(i):
            aKnot = theBSpline.Knot(i)
            cls.PrintParameter(aKnot)

        cls.Print2dCollection("Knots", aNumberOfKnots, PrintKnot)

        def PrintMultiplicity(i):
            aMultiplicity = theBSpline.Multiplicity(i)
            cls.PrintParameter(aMultiplicity)

        cls.Print2dCollection("Multiplicities", aNumberOfKnots, PrintMultiplicity)

        def PrintPole(i):
            aPole = theBSpline.Pole(i)
            cls.PrintParameter(aPole)

        cls.Print2dCollection("Poles", aNumberOfPoles, PrintPole)

        def PrintWeight(i):
            aWeight = theBSpline.Weight(i)
            cls.PrintParameter(aWeight)

        cls.Print2dCollection("Weights", aNumberOfPoles, PrintWeight)

    @classmethod
    def PrintOffsetCurve(cls, theOffset: mtk.Geom_OffsetCurve):
        cls.PrintName("Offset Curve")
        aDir = theOffset.Direction()
        anOffset = theOffset.Offset()
        cls.PrintDomain(theOffset)
        cls.PrintNamedParameter("Direction", aDir)
        cls.PrintNamedParameter("Offset",    anOffset)
        print("Basis Curve = ", end="")
        cls.PrintCurveInfo(theOffset.BasisCurve())
