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


def bWshape(shape):
    verts, face, normals, values = measure.marching_cubes(shape)
    mesh=base.Trimesh(vertices=verts, faces=face, vertex_normals=normals, validate=True)
    return mesh

def updateVertices(mesh, newVert):
    mesh = base.Trimesh(vertices=newVert, faces=mesh.faces, vertex_normals=mesh.vertex_normals, validate=True)
    return mesh
