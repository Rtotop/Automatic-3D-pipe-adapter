def its_insert_part_by_out_diameter_and_wall_thickness(out_diameter: float, wall_thickness: float) -> float:
    return out_diameter - 2 * wall_thickness

def insert_part_by_out_diameter_and_wall_thickness(out_diameter: float, wall_thickness_adapter: float) -> float:
    return out_diameter + 2 * wall_thickness_adapter
