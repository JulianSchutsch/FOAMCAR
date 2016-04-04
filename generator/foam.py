#
# Copyright: Julian Schutsch 2014
#
# Helper classes to create OpenFOAM files

class FoamWriter:
    def __init__(self, filename, object):
        if object is not None:
            self.content = "FoamFile{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object "+object+";\n}\n"
        else:
            self.content = ""
        self.indentLen = 0
        self.elements = []
        self.filename = filename

    def add(self, element):
        self.elements.append(element)

    def indent(self):
        self.indentLen+=4

    def unindent(self):
        self.indentLen-=4

    def write(self, str):
        self.content+=" "*self.indentLen+str+"\n"

    def writeElements(self):
        for element in self.elements:
            element.writeTo(self)
        with open(self.filename, "w+") as file:
            file.write(self.content)

class FoamVertices:
    def __init__(self, writer):
        self.vertices = []
        writer.add(self)

    def writeTo(self, writer):
        writer.write("vertices")
        writer.write("(")
        writer.indent()
        for vertice in self.vertices:
            writer.write("(%f %f %f)"%(vertice[0], vertice[1], vertice[2]))
        writer.unindent()
        writer.write(");")

    def create(self, vertice):
        for i, v in enumerate(self.vertices):
            if (v==vertice).all():
                return i
        self.vertices.append(vertice)
        return len(self.vertices)-1

class FoamBlocks:
    def __init__(self, writer):
        self.elements = []
        self.elements = []
        writer.add(self)

    def add(self, element):
        self.elements.append(element)

    def writeTo(self, writer):
        writer.write("blocks")
        writer.write("(")
        writer.indent()
        for element in self.elements:
            element.writeTo(writer)
        writer.unindent()
        writer.write(");")

class FoamHex:
    def __init__(self, blocks, vertices, vertexList, refinement, grading):
        blocks.add(self)
        self.vertices = [vertices.create(vertex) for vertex in vertexList]
        self.refinement = refinement
        self.grading = grading

    def writeTo(self, writer):
        vertices = "hex ("+" ".join(str(v) for v in self.vertices)+")"
        refinement = "(%i %i %i)"%(self.refinement[0], self.refinement[1], self.refinement[2])
        grading = " simpleGrading (%f %f %f)"%(self.grading[0], self.grading[1], self.grading[2])
        writer.write(vertices+refinement+grading)

class FoamEdges:
    def __init__(self, writer):
        writer.add(self)

    def writeTo(self, writer):
        writer.write("edges")
        writer.write("(")
        writer.write(");")

class FoamBoundary:
    def __init__(self, writer):
        writer.add(self)
        self.elements = []

    def add(self, element):
        self.elements.append(element)

    def writeTo(self, writer):
        writer.write("boundary")
        writer.write("(")
        writer.indent()
        for element in self.elements:
            element.writeTo(writer)
        writer.unindent()
        writer.write(");")

class FoamBoundaryPatch:
    def __init__(self, boundaries, name):
        boundaries.add(self)
        self.name = name
        self.faces = []

    def add(self, face):
        self.faces.append(face)

    def writeTo(self, writer):
        writer.write(self.name)
        writer.write("{")
        writer.indent()
        writer.write("type patch;")
        writer.write("faces")
        writer.write("(")
        writer.indent()
        for face in self.faces:
            face.writeTo(writer)
        writer.unindent()
        writer.write(");")
        writer.unindent()
        writer.write("}")

class FoamBoundaryWall:
    def __init__(self, boundaries, name):
        boundaries.add(self)
        self.name = name
        self.faces = []

    def add(self, face):
        self.faces.append(face)

    def writeTo(self, writer):
        writer.write(self.name)
        writer.write("{")
        writer.indent()
        writer.write("type wall;")
        writer.write("faces")
        writer.write("(")
        writer.indent()
        for face in self.faces:
            face.writeTo(writer)
        writer.unindent()
        writer.write(");")
        writer.unindent()
        writer.write("}")

class FoamBoundaryFace:
    def __init__(self, patch, vertices, vertexList):
        self.vertices = [vertices.create(vertex) for vertex in vertexList]
        patch.add(self)

    def writeTo(self, writer):
        writer.write("(%i %i %i %i)"%(self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3]))

class FoamConvertToMeters:
    def __init__(self, writer, unit):
        writer.add(self)
        self.unit = unit

    def writeTo(self, writer):
        writer.write("convertToMeters "+str(self.unit)+";")

