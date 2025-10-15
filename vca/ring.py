import numpy as np
from trimesh.util import concatenate

from con_mesh import ConMesh
from cylinder import create_embossed_text_on_cylinder
from cylinder import create_hollow_cylinder
from trimesh import transformations as tf

from cylinder import create_hollow_frustum


def create_ring(con: ConMesh, len_cylinder: float):
    cylinder1 = create_hollow_cylinder(con.r_base_outer, con.r_base_inner, len_cylinder, segments=128, y_offset=0)
    transform = tf.rotation_matrix(np.pi / 2, [1, 0, 0])  # +90° вокруг X
    engraving = create_embossed_text_on_cylinder(
        text=f'insert into inside di={con.d_base_inner}',
        r_outer=con.r_base_outer,
        extrude_depth=con.engrave_depth,
        height=len_cylinder,
        y_offset=0,
        font_size=len_cylinder,
    )
    cylinder1 = concatenate([cylinder1, engraving])
    cylinder1.apply_transform(transform)

    cylinder2 = create_hollow_frustum(con.r_top_outer, con.r_top_inner, len_cylinder, segments=128, y_offset=0)
    engraving = create_embossed_text_on_cylinder(
        text=f"it's insert inside do={con.d_top_outer}",
        r_outer=con.r_top_inner-con.engrave_depth,
        extrude_depth=con.engrave_depth,
        height=len_cylinder,
        y_offset=0,
        font_size=len_cylinder,
    )
    cylinder2 = concatenate([cylinder2, engraving])
    cylinder2.apply_transform(transform)

    return cylinder1, cylinder2