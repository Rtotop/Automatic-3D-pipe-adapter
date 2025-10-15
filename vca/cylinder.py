import numpy as np
import trimesh
from trimesh import Trimesh

from text import text_3d


def create_hollow_cylinder(r_outer, r_inner, height, segments=64, y_offset=0) -> Trimesh:

    vertices = []
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Наружные окружности (низ и верх)
    for y in [y_offset, y_offset + height]:
        for angle in angles:
            x = r_outer * np.cos(angle)
            z = r_outer * np.sin(angle)
            vertices.append([x, y, z])

    # Внутренние окружности (низ и верх)
    for y in [y_offset, y_offset + height]:
        for angle in angles:
            x = r_inner * np.cos(angle)
            z = r_inner * np.sin(angle)
            vertices.append([x, y, z])

    vertices = np.array(vertices)
    circle_points = segments
    faces = []

    def quad_to_triangles(v1, v2, v3, v4):
        return [[v1, v2, v3], [v1, v3, v4]]

    # Внешняя стенка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = i
        top1 = i + circle_points
        bottom2 = next_i
        top2 = next_i + circle_points
        faces.extend(quad_to_triangles(bottom1, bottom2, top2, top1))

    # Внутренняя стенка (нормали внутрь — порядок вершин инвертирован)
    offset_inner_bottom = 2 * circle_points
    offset_inner_top = 3 * circle_points
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = offset_inner_bottom + i
        top1 = offset_inner_top + i
        bottom2 = offset_inner_bottom + next_i
        top2 = offset_inner_top + next_i
        faces.extend(quad_to_triangles(bottom1, top1, top2, bottom2))

    # Верхняя крышка (кольцо между внешним и внутренним радиусом)
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_top1 = circle_points + i
        outer_top2 = circle_points + next_i
        inner_top1 = 3 * circle_points + i
        inner_top2 = 3 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_top1, outer_top2, inner_top2, inner_top1))

    # Нижняя крышка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_bottom1 = i
        outer_bottom2 = next_i
        inner_bottom1 = 2 * circle_points + i
        inner_bottom2 = 2 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_bottom1, outer_bottom2, inner_bottom2, inner_bottom1))

    faces = np.array(faces)
    return Trimesh(vertices=vertices, faces=faces)


def create_embossed_text_on_cylinder(text, r_outer, extrude_depth, height, y_offset=0, font_size=3.0) -> Trimesh:
    text_mesh = text_3d(text, font_size, extrude_height=extrude_depth)
    text_mesh.export('text_mesh.stl')

    verts = text_mesh.vertices.copy()

    # 2. Нормализуем X: сдвигаем начало текста в 0
    x_min = verts[:, 0].min()
    verts[:, 0] -= x_min
    text_length = verts[:, 0].max()

    # 3. (Опционально) масштабируем, чтобы не превысить разумную длину на цилиндре
    max_circumference_ratio = 0.9
    max_allowed = 2 * np.pi * r_outer * max_circumference_ratio
    if text_length > max_allowed:
        scale = max_allowed / text_length
        verts[:, 0] *= scale

    # 4. Преобразуем линейную координату X → угол theta
    theta = -verts[:, 0] / r_outer  # s = r * theta → theta = s / r

    # 5. Радиальное расстояние: поверхность цилиндра + экструзия (Z)
    #    Z=0 → на поверхности, Z>0 → НАРУЖУ (выпуклость)
    radial_dist = r_outer + verts[:, 2]

    # 6. Преобразуем в (x, z) на цилиндре
    x_cyl = radial_dist * np.cos(theta)
    z_cyl = radial_dist * np.sin(theta)

    # 7. Позиционируем по высоте Y
    y_text_center = (verts[:, 1].min() + verts[:, 1].max()) / 2
    y_cyl_center = y_offset + height / 2
    y_new = y_cyl_center + (verts[:, 1] - y_text_center)

    # 8. Собираем финальные вершины
    final_vertices = np.column_stack([x_cyl, y_new, z_cyl])

    # 9. Создаём меш
    embossed_mesh = Trimesh(vertices=final_vertices, faces=text_mesh.faces)
    embossed_mesh.fix_normals()
    return embossed_mesh


def create_hollow_frustum(r_outer, r_inner, height, segments=64, y_offset=0) -> Trimesh:
    """
    Создаёт полый усечённый конус (frustum), где верхний диаметр на 1 мм меньше нижнего.

    Параметры:
        r_outer (float): Внешний радиус внизу (в мм).
        r_inner (float): Внутренний радиус внизу (в мм).
        height (float): Высота конуса.
        segments (int): Количество сегментов для аппроксимации окружности.
        y_offset (float): Смещение по оси Y.

    Возвращает:
        Trimesh: Объект полого усечённого конуса.
    """
    # Уменьшаем радиусы на 0.5 мм сверху (т.к. диаметр уменьшается на 1 мм)
    r_outer_top = r_outer - 0.5
    r_inner_top = r_inner - 0.5

    # Защита от отрицательных/некорректных радиусов
    if r_outer_top <= 0 or r_inner_top < 0 or r_inner >= r_outer or r_inner_top >= r_outer_top:
        raise ValueError("Некорректные радиусы: убедитесь, что r_inner < r_outer и r_outer > 0.5")

    vertices = []
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Внешние окружности: низ и верх
    for y, r in [(y_offset, r_outer), (y_offset + height, r_outer_top)]:
        for angle in angles:
            x = r * np.cos(angle)
            z = r * np.sin(angle)
            vertices.append([x, y, z])

    # Внутренние окружности: низ и верх
    for y, r in [(y_offset, r_inner), (y_offset + height, r_inner_top)]:
        for angle in angles:
            x = r * np.cos(angle)
            z = r * np.sin(angle)
            vertices.append([x, y, z])

    vertices = np.array(vertices)
    circle_points = segments
    faces = []

    def quad_to_triangles(v1, v2, v3, v4):
        return [[v1, v2, v3], [v1, v3, v4]]

    # Внешняя стенка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = i
        top1 = i + circle_points
        bottom2 = next_i
        top2 = next_i + circle_points
        faces.extend(quad_to_triangles(bottom1, bottom2, top2, top1))

    # Внутренняя стенка (нормали внутрь — порядок вершин инвертирован)
    offset_inner_bottom = 2 * circle_points
    offset_inner_top = 3 * circle_points
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = offset_inner_bottom + i
        top1 = offset_inner_top + i
        bottom2 = offset_inner_bottom + next_i
        top2 = offset_inner_top + next_i
        faces.extend(quad_to_triangles(bottom1, top1, top2, bottom2))

    # Верхняя крышка (кольцо)
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_top1 = circle_points + i
        outer_top2 = circle_points + next_i
        inner_top1 = 3 * circle_points + i
        inner_top2 = 3 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_top1, outer_top2, inner_top2, inner_top1))

    # Нижняя крышка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_bottom1 = i
        outer_bottom2 = next_i
        inner_bottom1 = 2 * circle_points + i
        inner_bottom2 = 2 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_bottom1, outer_bottom2, inner_bottom2, inner_bottom1))

    faces = np.array(faces)
    return Trimesh(vertices=vertices, faces=faces)