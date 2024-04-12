def bWshape(shape, threshold):
    """Creates a triangular mesh shape using marching cubes algorithm."""
    from skimage import measure
    from trimesh import base

    verts, face, normals, _ = measure.marching_cubes(shape, level=threshold, allow_degenerate=False)
    mesh=base.Trimesh(vertices=verts, faces=face, vertex_normals=normals, validate=True)
    return mesh


def updateVertices(mesh, newVert):
    """Creates a mesh using a previous mesh's faces with new vertices locations."""
    from trimesh import base

    mesh = base.Trimesh(vertices=newVert, faces=mesh.faces, vertex_normals=mesh.vertex_normals, validate=True)
    return mesh
