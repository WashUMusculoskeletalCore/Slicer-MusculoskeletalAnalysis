from skimage import measure
from trimesh import base

# Creates a triangular mesh shape using marching cubes algorithm 
def bWshape(shape):
    verts, face, normals, values = measure.marching_cubes(shape)
    mesh=base.Trimesh(vertices=verts, faces=face, vertex_normals=normals, validate=True)
    return mesh

# Creates a mesh using a previous mesh's faces with new vertices locations
def updateVertices(mesh, newVert):
    mesh = base.Trimesh(vertices=newVert, faces=mesh.faces, vertex_normals=mesh.vertex_normals, validate=True)
    return mesh
