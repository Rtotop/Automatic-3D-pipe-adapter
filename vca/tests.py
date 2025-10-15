import os
import unittest

from adapter import generate_stl
from calc import insert_part_by_out_diameter_and_wall_thickness
from calc import its_insert_part_by_out_diameter_and_wall_thickness
from con_mesh import ConMesh
from text import text_3d


class TestGenerateSTL(unittest.TestCase):
    test_filename = ''

    def test_text(self):
        self.assertEqual(ConMesh(27.0, 39.0, 2).text, '35 x 27')
        self.assertEqual(ConMesh(27.06, 39.04, 2).text, '35 x 27')
        self.assertEqual(ConMesh(39.6, 27.4, 2).text, '35.6 x 27.4')

    def test_stl_generation(self):
        """Тест: генерация STL-файла"""
        r_cylinder1 = 39
        r_cylinder2 = 37
        thickness = 2.0
        len_cylinder = 30.0

        self.test_filename = f'vacuum_cleaner_adapter_{r_cylinder1}_{r_cylinder2}.stl'

        # Удаляем файл, если он существует
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

        # Вызываем функцию
        generate_stl(r_cylinder1, r_cylinder2, thickness, len_cylinder)

        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(self.test_filename), "Файл STL не был создан")

        # Проверяем, что файл не пустой
        self.assertGreater(os.path.getsize(self.test_filename), 0, "Файл STL пустой")

    def test_cross_section_generation(self):
        r_cylinder1 = 39
        r_cylinder2 = 37
        thickness = 2.0
        len_cylinder = 30.0
        self.test_filename = f'vacuum_cleaner_adapter_{r_cylinder1}_{r_cylinder2}.stl'
        """Тест: генерация сечения из модели"""
        # Удаляем файл сечения, если он существует
        section_filename = "cylinder_section_from_mesh.png"
        if os.path.exists(section_filename):
            os.remove(section_filename)

        # Вызываем функцию
        generate_stl(r_cylinder1, r_cylinder2, thickness, len_cylinder)

        # Проверяем, что файл сечения создан
        self.assertTrue(os.path.exists(section_filename), "Файл сечения не был создан")

        # Проверяем, что файл не пустой
        self.assertGreater(os.path.getsize(section_filename), 0, "Файл сечения пустой")

    # def tearDown(self):
    #     # Удаляем временные файлы после тестов
    #     if self.test_filename and os.path.exists(self.test_filename):
    #         os.remove(self.test_filename)
    #     if os.path.exists("cylinder_section_from_mesh.png"):
    #         os.remove("cylinder_section_from_mesh.png")

    def test_text_3d(self):
        mesh = text_3d('2')
        output_file = "digits_1234_manual.stl"
        mesh.export(output_file)

    def test_stl_generation_with_calc(self):
        thickness = 2.0
        len_cylinder = 35.0
        depth=0.6
        r_cylinder1 = insert_part_by_out_diameter_and_wall_thickness(out_diameter=35.5, wall_thickness_adapter=thickness)
        r_cylinder2 = its_insert_part_by_out_diameter_and_wall_thickness(out_diameter=45.7, wall_thickness=3.5)
        # Вызываем функцию
        generate_stl(r_cylinder1, r_cylinder2, thickness, len_cylinder, depth)
