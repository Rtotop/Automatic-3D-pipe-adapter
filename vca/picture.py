import numpy as np
from matplotlib import pyplot as plt


def generate_cross_section_from_mesh(mesh, cut_plane_normal=[1, 0, 0], cut_plane_origin=[0, 0, 0], filename="section_from_mesh.png"):
    """
    Генерирует 2D-изображение продольного сечения 3D-меша.
    По умолчанию режет плоскостью X=0 (вертикальный разрез вдоль YZ).
    """
    # Нормаль и точка плоскости
    plane_normal = np.array(cut_plane_normal)
    plane_origin = np.array(cut_plane_origin)

    # Получаем линии пересечения меша с плоскостью
    lines = mesh.section(plane_normal=plane_normal, plane_origin=plane_origin)

    if lines is None:
        print("⚠️ Сечение не найдено!")
        return

    # Преобразуем в 2D (проекция на плоскость)
    try:
        # Преобразуем в 2D-координаты на плоскости
        section_2d, to_3d = lines.to_planar()
    except Exception as e:
        print(f"⚠️ Не удалось спроецировать сечение: {e}")
        return

    # Рисуем
    fig, ax = plt.subplots(figsize=(5, 8))
    section_2d.show(ax=ax)
    ax.set_aspect('equal')
    ax.set_title('Сечение 3D-модели\n(плоскость X=0)', fontsize=11)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Сечение из 3D-модели сохранено как '{filename}'")
