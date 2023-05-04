from skimage import measure
from trimesh import base


def bWshape(shape):
    verts, face, normals, values = measure.marching_cubes(shape)
    mesh=base.Trimesh(vertices=verts, faces=face, vertex_normals=normals, validate=True)
    return mesh

def updateVertices(mesh, newVert):
    mesh = base.Trimesh(vertices=newVert, faces=mesh.faces, vertex_normals=mesh.vertex_normals, validate=True)
    return mesh
