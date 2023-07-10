try:
    from skimage import measure
except:
    from slicer.util import pip_install
    pip_install("scikit-image")
    from skimage import measure
try:
    from trimesh import base
except:
    from slicer.util import pip_install
    pip_install("trimesh")
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
