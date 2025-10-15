import numpy as np
from trimesh import Trimesh

from con_mesh import ConMesh


def create_hollow_cone_with_wall_thickness(
        con: ConMesh, center_x=0, center_z=0, y_base=0, segments=64, cut_height=None
) -> Trimesh:

    if cut_height is None or cut_height > con.height:
        cut_height = con.height

    y_cut = y_base + cut_height

    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Радиусы на срезе (cut)
    r_cut = con.r_base_outer + (con.r_top_outer - con.r_base_outer) * (cut_height / con.height)

    outer_base_ring = []
    outer_cut_ring = []

    # Создаем внешнюю поверхность: внешний радиус
    for angle in angles:
        x_base = center_x + con.r_base_outer * np.cos(angle)
        z_base = center_z + con.r_base_outer * np.sin(angle)
        outer_base_ring.append(np.array([x_base, y_base, z_base]))

        x_cut = center_x + r_cut * np.cos(angle)
        z_cut = center_z + r_cut * np.sin(angle)
        outer_cut_ring.append(np.array([x_cut, y_cut, z_cut]))

    # Внутренний радиус — по условию, чтобы толщина по горизонтали равнялась z
    r_base_inner = con.r_base_outer - con.thickness_cylinder
    r_cut_inner = r_cut - con.thickness_cylinder

    inner_base_ring = []
    inner_cut_ring = []

    for angle in angles:
        # Внутренние точки на основании и срезе
        x_base_inner = center_x + r_base_inner * np.cos(angle)
        z_base_inner = center_z + r_base_inner * np.sin(angle)
        inner_base_ring.append(np.array([x_base_inner, y_base, z_base_inner]))

        x_cut_inner = center_x + r_cut_inner * np.cos(angle)
        z_cut_inner = center_z + r_cut_inner * np.sin(angle)
        inner_cut_ring.append(np.array([x_cut_inner, y_cut, z_cut_inner]))

    # Собираем вершины
    vertices = np.array(outer_base_ring + outer_cut_ring + inner_base_ring + inner_cut_ring)
    s = segments
    faces = []

    # Формируем стороны боковой поверхности
    for i in range(s):
        next_i = (i + 1) % s
        # Внешняя боковая поверхность
        faces.append([i, next_i, s + next_i])
        faces.append([i, s + next_i, s + i])
        # Внутренняя боковая поверхность (нормали внутрь, инвертируем порядок)
        a = 2 * s + i
        b = 2 * s + next_i
        c = 3 * s + next_i
        d = 3 * s + i
        faces.append([a, c, b])
        faces.append([a, d, c])
        # Основание — внутренний и внешний круг
        faces.append([i, 2 * s + i, 2 * s + next_i])
        faces.append([i, 2 * s + next_i, next_i])
        # Верхние крышки (среза)
        faces.append([s + i, 3 * s + i, 3 * s + next_i])
        faces.append([s + i, 3 * s + next_i, s + next_i])

    faces = np.array(faces)
    return Trimesh(vertices=vertices, faces=faces)
