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
    # hook = create_hook(False)
    # hook.label = "hook"
    # snap_hook = create_snap_hook(False)
    # snap_hook.label = "SnapHook"
    # snap_groove = create_snap_groove()
    # snap_groove.label = "SnapHookGroove"
    org = SkadisOrganizer(wall_height=30)
    board = org.create_board(12, 8, border_x=10, border_y=10, start_indented=False)
    board.label = "Board"
    name = "wall-v"
    wallv = org.create_wall(1, 2, 5, SkadisOrganizer.Orientation.VERTICAL, True, name)
    name = "wall-h"
    wallh = org.create_wall(3, 4, 4, SkadisOrganizer.Orientation.HORIZONTAL, False, name)
    adapter = org.create_adapter(1, 4, 2, "A1")
    # wallh1 = org.create_wall(3, 1, 1, SkadisOrganizer.Orientation.HORIZONTAL)
    # wallh1.label = "H1"
    adapter2 = org.create_adapter(1, 3, 2, "A2")
    show_objects = (
        # hook,
        # snap_hook,
        # snap_groove,
        board,
        wallv,
        wallh,
        adapter,
        adapter2,
        # wallh1,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%