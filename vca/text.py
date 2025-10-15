import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.textpath import TextPath
import numpy as np
import shapely.geometry as geom
import shapely.ops as ops
from shapely.affinity import scale, translate
import trimesh


def _quadratic_bezier(p0, p1, p2, n=20):
    """Аппроксимация квадратичной кривой Безье (CURVE3)."""
    t = np.linspace(0, 1, n)
    return (1 - t)[:, None]**2 * p0 + 2 * (1 - t)[:, None] * t[:, None] * p1 + t[:, None]**2 * p2

def _cubic_bezier(p0, p1, p2, p3, n=20):
    """Аппроксимация кубической кривой Безье (CURVE4)."""
    t = np.linspace(0, 1, n)
    return (
        (1 - t)[:, None]**3 * p0 +
        3 * (1 - t)[:, None]**2 * t[:, None] * p1 +
        3 * (1 - t)[:, None] * t[:, None]**2 * p2 +
        t[:, None]**3 * p3
    )

def text_to_polygons(text, font_size=20, font_family="Arial", curve_samples=20):
    """
    Преобразует текст в список полигонов Shapely (2D).
    """
    # Создаём TextPath — 2D-контур текста
    fp = FontProperties(family=font_family)
    tp = TextPath((0, 0), text, size=font_size, prop=fp)

    # Извлекаем все замкнутые контуры (path codes)
    polygons = []
    current_path = []
    i = 0
    vertices_list = tp.vertices
    codes_list = tp.codes

    # Обходим вручную, чтобы обрабатывать CURVE3/CURVE4 правильно
    while i < len(codes_list):
        code = codes_list[i]
        if code == Path.MOVETO:
            if current_path and len(current_path) >= 3:
                polygons.append(np.array(current_path))
            current_path = [vertices_list[i].copy()]
            i += 1

        elif code == Path.LINETO:
            current_path.append(vertices_list[i].copy())
            i += 1

        elif code == Path.CURVE3:
            # Квадратичная кривая: требует 2 точки (контрольная + конечная)
            if i + 1 >= len(vertices_list):
                i += 1
                continue
            p0 = current_path[-1]  # начальная точка
            p1 = vertices_list[i]  # контрольная
            p2 = vertices_list[i + 1]  # конечная
            # Аппроксимируем кривую, исключая первую точку (она уже есть)
            curve_points = _quadratic_bezier(p0, p1, p2, n=curve_samples)[1:]
            current_path.extend(curve_points)
            i += 2  # потребляли 2 точки

        elif code == Path.CURVE4:
            # Кубическая кривая: требует 3 точки
            if i + 2 >= len(vertices_list):
                i += 1
                continue
            p0 = current_path[-1]
            p1 = vertices_list[i]
            p2 = vertices_list[i + 1]
            p3 = vertices_list[i + 2]
            curve_points = _cubic_bezier(p0, p1, p2, p3, n=curve_samples)[1:]
            current_path.extend(curve_points)
            i += 3

        elif code == Path.CLOSEPOLY:
            # Замыкаем контур: соединяем с первой точкой
            if current_path and len(current_path) >= 2:
                # Не добавляем дубликат, Shapely сам замкнёт
                pass
            if current_path and len(current_path) >= 3:
                polygons.append(np.array(current_path))
            current_path = []
            i += 1

        else:
            i += 1

    # Последний контур
    if current_path and len(current_path) >= 3:
        polygons.append(np.array(current_path))

    # Преобразуем в Shapely-полигоны
    shapely_polys = []
    for poly_coords in polygons:
        try:
            poly = geom.Polygon(poly_coords)
            if poly.is_valid and not poly.is_empty and poly.area > 1e-8:
                shapely_polys.append(poly)
        except Exception as e:
            continue

    if not shapely_polys:
        raise ValueError("Не удалось создать полигоны из текста")

    # Объединяем
    merged = ops.unary_union(shapely_polys)
    if merged.geom_type == 'Polygon':
        return [merged]
    elif merged.geom_type == 'MultiPolygon':
        return [p for p in merged.geoms if p.area > 1e-8]
    else:
        return shapely_polys


def polygons_to_mesh(polygons, height=5.0):
    meshes = []
    for poly in polygons:
        if poly.area < 1e-6:
            continue
        try:
            mesh = trimesh.creation.extrude_polygon(poly, height=height)
            meshes.append(mesh)
        except Exception as e:
            print(f"Пропущен полигон из-за ошибки: {e}")
            continue

    if not meshes:
        raise ValueError("Не удалось создать ни один 3D-меш")

    combined = trimesh.util.concatenate(meshes)
    return combined


def text_3d(text: str, font_size=30, extrude_height=5.0, font_family="Arial", curve_samples=30):
    """
    Создаёт 3D-меш из текста с гладкими кривыми.
    """
    polygons = text_to_polygons(
        text,
        font_size=font_size,
        font_family=font_family,
        curve_samples=curve_samples
    )
    mesh = polygons_to_mesh(polygons, height=extrude_height)
    mesh.apply_translation(-mesh.centroid)
    return mesh