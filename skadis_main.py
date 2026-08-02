from typing import Iterable
from ocp_vscode import show_clear,show, show_all, Camera
from build123d import *

from skadis_organizer import SkadisOrganizer

# %%
def export (parts: Iterable[Part], name: str):
    exporter = Mesher()

    for part in parts:
        exporter.add_shape(part)

    exporter.add_meta_data(
        name_space="custom",
        name="name",
        value=name,
        metadata_type="str",
        must_preserve=False,
    )
    exporter.write(name)


if __name__ == '__main__':
    show_clear()
    org = SkadisOrganizer(wall_height=30, first_row_indented=True, with_support=True)
    # board = org.create_board(12, 8, border_x=10, border_y=10, name="Board")
    wallv = org.create_wall(1, 2, 5, SkadisOrganizer.Orientation.VERTICAL, True, "wall-v")
    wallh = org.create_wall(3, 4, 4, SkadisOrganizer.Orientation.HORIZONTAL, False, "wall-h")
    adapter = org.create_adapter(SkadisOrganizer.AdapterType.LEFT_HOOK, 3, 3, 2, "A1")
    wallh1 = org.create_wall(1, 1, 3, SkadisOrganizer.Orientation.HORIZONTAL, False, "H1")
    adapter2 = org.create_adapter(SkadisOrganizer.AdapterType.RIGHT_GROOVE, 4, 1, 3, name="A2")
    show_objects = (
        # board,
        wallv,
        wallh1,
        adapter,
        adapter2,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%