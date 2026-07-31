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
    board = org.create_board(12, 8, border_x=10, border_y=10)
    board.label = "Board"
    name = "wall-v"
    wallv = org.create_wall(1, 2, 5, SkadisOrganizer.Orientation.VERTICAL, True)
    wallv.label = name
    wallh = org.create_wall(3, 4, 4, SkadisOrganizer.Orientation.HORIZONTAL, False)
    name = "wall-h"
    wallh.label = name
    adapter = org.create_adapter(1, 4)
    adapter.name = "adapter"

    show_objects = (
        # hook,
        # snap_hook,
        # snap_groove,
        board,
        wallv,
        wallh,
        adapter,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%