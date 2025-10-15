import numpy as np
import trimesh
from trimesh import Trimesh
from trimesh import transformations as tf
from trimesh.util import concatenate

from con_mesh import ConMesh
from con_mesh import InsertText
from cone import create_hollow_cone_with_wall_thickness
from cylinder import create_embossed_text_on_cylinder
from cylinder import create_hollow_cylinder
from cylinder import create_hollow_frustum
from picture import generate_cross_section_from_mesh
from ring import create_ring


def create_adapter(con: ConMesh, len_cylinder: float) -> Trimesh:
    cylinder1 = create_hollow_cylinder(con.r_base_outer, con.r_base_inner, len_cylinder, segments=128, y_offset=0)
    cylinder2 = create_hollow_frustum(con.r_top_outer, con.r_top_inner, len_cylinder, segments=128, y_offset=con.height + len_cylinder)

    if con.insert_text == InsertText.Base:
        engraving = create_embossed_text_on_cylinder(
            text=con.text,
            r_outer=con.r_base_outer,
            extrude_depth=con.engrave_depth,
            height=len_cylinder,
            y_offset=0,
            font_size=10.0
        )
        cylinder1 = concatenate([cylinder1, engraving])
    elif con.insert_text == InsertText.Top:
        engraving = create_embossed_text_on_cylinder(
            text=con.text,
            r_outer=con.r_top_outer,
            extrude_depth=con.engrave_depth,
            height=len_cylinder,
            y_offset=con.height + len_cylinder,
            font_size=10.0
        )
        cylinder2 = concatenate([cylinder2, engraving])

    # Вершина конуса сверху на высоте c + cone_height
    cone_mesh = create_hollow_cone_with_wall_thickness(
        con=con,
        center_x=0,
        center_z=0,
        y_base=len_cylinder,
        segments=128,
        cut_height=con.height  # усечь конус на c4
    )
    # Объединяем все
    combined_data = concatenate([cylinder1, cone_mesh, cylinder2])
    transform = tf.rotation_matrix(np.pi / 2, [1, 0, 0])  # +90° вокруг X
    combined_data.apply_transform(transform)

    return combined_data

def generate_stl(d_cylinder1: float, d_cylinder2: float, thickness: float, len_cylinder: float, depth: float=1) -> None:
    con = ConMesh(d_cylinder1, d_cylinder2, thickness_cylinder=thickness)
    con.engrave_depth = depth

    combined_data = create_adapter(con, len_cylinder)
    combined_data.export(f'vca_{d_cylinder1}_{d_cylinder2}.stl', file_type='stl_ascii')

    ring_base, ring_top = create_ring(con, 7)
    ring_base.export(f'vca_test_base_ring_{d_cylinder1}.stl', file_type='stl_ascii')
    ring_top.export(f'vca_test_top_ring_{d_cylinder2}.stl', file_type='stl_ascii')

    # Генерируем сечение ИЗ МОДЕЛИ
    # generate_cross_section_from_mesh(
    #     combined_data,
    #     cut_plane_normal=[1, 0, 0],   # режем плоскостью X=0
    #     cut_plane_origin=[0, 0, 0],
    #     filename="cylinder_section_from_mesh.png"
    # )
    print(f'vacuum_cleaner_adapter_{d_cylinder1}_{d_cylinder2}.stl')
