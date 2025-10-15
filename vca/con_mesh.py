from enum import Enum


class InsertText(Enum):
    Top = 1
    Base = 2
    No = 0


class ConMesh:
    d_base_outer: float
    d_top_outer: float
    thickness_cylinder: float
    insert_text: InsertText
    engrave_depth: float = 1

    def __init__(
            self,
            d_base_outer: float,
            d_top_outer: float,
            thickness_cylinder: float,
    ):
        if d_base_outer > d_top_outer:
            self.d_base_outer, self.d_top_outer = d_base_outer, d_top_outer
            self.insert_text = InsertText.Base
        else:
            self.d_base_outer, self.d_top_outer = d_top_outer, d_base_outer
            self.insert_text = InsertText.Top

        if thickness_cylinder > d_top_outer:
            raise ValueError("Толщина стенки слишком велика, внутренний диаметр <= 0")

        self.thickness_cylinder = thickness_cylinder

    @property
    def r1_internal(self) -> float:
        return self.d_base_outer - 2 * self.thickness_cylinder

    @property
    def height_out1(self) -> float:
        return (self.d_base_outer * (3 ** 0.5)) / 2  # Высота внешнего конуса

    @property
    def height(self) -> float:
        c3 = ((self.d_base_outer - self.d_top_outer) / 2) + (3 ** 0.5)
        return c3 + self.thickness_cylinder / 2 + self.thickness_cylinder

    @property
    def thickness(self) -> float:
        return self.thickness_cylinder ** 2

    @property
    def r_base_outer(self) -> float:
        return self.d_base_outer / 2

    @property
    def r_top_outer(self) -> float:
        return self.d_top_outer / 2

    @property
    def r_base_inner(self) -> float:
        return self.r_base_outer - self.thickness_cylinder

    @property
    def r_top_inner(self) -> float:
        return self.r_top_outer - self.thickness_cylinder

    @property
    def d_base_inner(self) -> float:
        return self.d_base_outer - 2 * self.thickness_cylinder

    @property
    def d_top_inner(self) -> float:
        return self.d_top_outer - 2 * self.thickness_cylinder

    @property
    def text(self) -> str:
        def fmt(x):
            x_rounded = int(x * 10) / 10
            if x_rounded == int(x):
                return str(int(x))
            else:
                return f"{x_rounded:.1f}"

        return f"{fmt(self.d_base_inner)} x {fmt(self.d_top_outer)}"
