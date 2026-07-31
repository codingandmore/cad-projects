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
    org = SkadisOrganizer(wall_height=30)
    board = org.create_board(27, 17, border_x=10, border_y=10, start_indented=True)
    board.label = "Board"

    walla = org.create_wall(2, 5, 9, SkadisOrganizer.Orientation.VERTICAL, True)
    walla.label = "A"

    wallb = org.create_wall(4, 5, 6, SkadisOrganizer.Orientation.VERTICAL, True)
    wallb.label = "B"

    wallc = org.create_wall(6, 5, 4, SkadisOrganizer.Orientation.VERTICAL, True)
    wallc.label = "C"
    walld = org.create_wall(13, 5, 6, SkadisOrganizer.Orientation.VERTICAL, True)
    walld.label = "D"
    walle = org.create_wall(16, 2, 12, SkadisOrganizer.Orientation.VERTICAL, True)
    walle.label = "E"
    wallf = org.create_wall(18, 2, 12, SkadisOrganizer.Orientation.VERTICAL)
    wallf.label = "F"
    wallg = org.create_wall(2, 14, 12, SkadisOrganizer.Orientation.HORIZONTAL, True)
    wallg.label = "G"
    adapterh1 = org.create_adapter(2, 5, 2)
    adapterh1.label = "H1A"
    adapterh2 = org.create_adapter(4, 5, 2)
    adapterh2.label = "H2A"
    adapterh3 = org.create_adapter(6, 5, 2)
    adapterh3.label = "H3A"
    wallh3 = org.create_wall(8, 5, 5, SkadisOrganizer.Orientation.HORIZONTAL)
    wallh3.label = "H3"
    walli = org.create_wall(2, 2, 14, SkadisOrganizer.Orientation.HORIZONTAL)
    walli.label = "I"
    wallj = org.create_wall(14, 14, 11, SkadisOrganizer.Orientation.HORIZONTAL, True)
    wallj.label = "J"
    wallk = org.create_wall(6, 9, 7, SkadisOrganizer.Orientation.HORIZONTAL, True)
    wallk.label = "k"
    walll = org.create_wall(4, 11, 9, SkadisOrganizer.Orientation.HORIZONTAL, True)
    walll.label = "L"
    # show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    show_all(reset_camera=Camera.KEEP)
    # export([part1, part2], "drawer-1.3mf")


# %%