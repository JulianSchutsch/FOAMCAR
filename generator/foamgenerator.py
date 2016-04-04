#
# Copyright: Julian Schutsch
#
# Creates custom OpenFOAM files surrounding the present body with inlet and outlets.

import re
import os
import numpy
import math
import subprocess
import foam

floatStr =  r'(\S*)'
cmExpression = re.compile(r"\s*Cm\s*=\s*"+floatStr+r"\s*")
cdExpression = re.compile(r"\s*Cd\s*=\s*"+floatStr+r"\s*")
clExpression = re.compile(r"\s*Cl\s*=\s*"+floatStr+r"\s*")
pressureExpression = re.compile(r"\s*pressure\s:\s*\(\s*"+floatStr+r"\s*"+floatStr+r"\s*"+floatStr+"\s*\)\s*")
forceExpression = re.compile(r"\s*sum of forces:")
momentExpression = re.compile(r"\s*sum of moments:")

def createRotatedBox(center, lengths, angle):
    center = numpy.array(center)
    h0 = numpy.array([lengths[0]/2, 0, 0])
    h1 = numpy.array([0, lengths[1]/2, 0])
    h2 = numpy.array([0, 0, lengths[2]/2])
    c = math.cos(angle)
    s = math.sin(angle)
    rotationMatrix = numpy.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])

    p1 = (rotationMatrix.dot(-h0-h1-h2)+center)
    p2 = (rotationMatrix.dot(h0-h1-h2)+center)
    p3 = (rotationMatrix.dot(h0+h1-h2)+center)
    p4 = (rotationMatrix.dot(-h0+h1-h2)+center)
    p5 = (rotationMatrix.dot(-h0-h1+h2)+center)
    p6 = (rotationMatrix.dot(h0-h1+h2)+center)
    p7 = (rotationMatrix.dot(h0+h1+h2)+center)
    p8 = (rotationMatrix.dot(-h0+h1+h2)+center)
    return p1, p2, p3, p4, p5, p6, p7, p8

def createBlockMeshDict(settings):
    # Helper function to get coefficients from indicies
    def select(p, s):
      return [p[i] for i in s]

    blockMeshDict = foam.FoamWriter(os.path.join(settings.rootPath, "constant", "polyMesh", "blockMeshDict"), "blockMeshDict")
    foam.FoamConvertToMeters(blockMeshDict, 1)
    vertices = foam.FoamVertices(blockMeshDict)
    blocks = foam.FoamBlocks(blockMeshDict)
    p = createRotatedBox([0,0,4], [30,16,8], settings.angle)
    foam.FoamHex(blocks, vertices, p, [20,20,20], [1,1,1])
    foam.FoamEdges(blockMeshDict)
    boundaries = foam.FoamBoundary(blockMeshDict)
    b = foam.FoamBoundaryPatch(boundaries, "frontAndBack")
    foam.FoamBoundaryFace(b, vertices, select(p, (3,7,6,2)))
    foam.FoamBoundaryFace(b, vertices, select(p, (1,5,4,0)))
    b = foam.FoamBoundaryPatch(boundaries, "inlet")
    foam.FoamBoundaryFace(b, vertices, select(p, (0,4,7,3)))
    b = foam.FoamBoundaryPatch(boundaries, "outlet")
    foam.FoamBoundaryFace(b, vertices, select(p, (2,6,5,1)))
    b = foam.FoamBoundaryWall(boundaries, "lowerWall")
    foam.FoamBoundaryFace(b, vertices, select(p, (0,3,2,1)))
    b = foam.FoamBoundaryPatch(boundaries, "upperWall")
    foam.FoamBoundaryFace(b, vertices, select(p, (4,5,6,7)))
    blockMeshDict.writeElements()

def createInitialConditions(settings):
    initialConditions = foam.FoamWriter(os.path.join(settings.rootPath, "0.org", "include", "initialConditions"), object=None)
    flowVelocity = settings.flowVelocity
    vehicleVelocity = settings.vehicleVelocity
    initialConditions.write("flowVelocity (%f %f %f);"%(flowVelocity[0], flowVelocity[1], flowVelocity[2]))
    initialConditions.write("vehicleVelocity (%f %f %f);"%(vehicleVelocity[0], vehicleVelocity[1], vehicleVelocity[2]))
    initialConditions.write("pressure 0;")
    initialConditions.write("turbulentKE 0.24;")
    initialConditions.write("turbulentOmega 1.78;")
    initialConditions.writeElements()

def extractDragCoefficients(settings):
    cm = None
    cd = None
    cl = None
    with open(os.path.join(settings.rootPath, "log.simpleFoam")) as f:
        for line in f.readlines():
            cmMatch = cmExpression.match(line)
            cdMatch = cdExpression.match(line)
            clMatch = clExpression.match(line)
            if cmMatch:
                cm = float(cmMatch.group(1))
            if cdMatch:
                cd = float(cdMatch.group(1))
            if clMatch:
                cl = float(clMatch.group(1))
    return cm, cd, cl

def extractPressureCoefficients(settings):
    F = None
    M = None
    mode = None
    with open(os.path.join(settings.rootPath, "log.simpleFoam")) as f:
        for line in f.readlines():
            if forceExpression.match(line):
                mode = "F"
            if momentExpression.match(line):
                mode = "M"
            match = pressureExpression.match(line)
            if match:
                if mode=="F":
                    F = [float(match.group(1)), float(match.group(2)), float(match.group(3))]
                if mode=="M":
                    M = [float(match.group(1)), float(match.group(2)), float(match.group(3))]
    return F, M

def calculatePressureCoefficients(settings):
    oldDir = os.getcwd()
    os.chdir(settings.rootPath)
    createBlockMeshDict(settings)
    createInitialConditions(settings)
    subprocess.call(os.path.join(settings.rootPath, "Allclean"))
    subprocess.call(os.path.join(settings.rootPath, "Allrun"))
    F,M = extractPressureCoefficients(settings)
    os.chdir(oldDir)
    return F,M
