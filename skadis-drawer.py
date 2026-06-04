# %%
import copy
from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from math import asin, acos, atan, degrees, sin, cos, tan, radians, radians, pi, sqrt
from typing import Iterable

skadis_slot_h = 15
skadis_slot_w = 5
clearance = 0.3
wall_height = 30
wall_thickness = skadis_slot_w
slot_spacing = 20
double_slot_spacing = 2 * slot_spacing
hook_offset_row = slot_spacing - skadis_slot_w + clearance / 2 # initial offset for hook to align with next wall
peg_h = skadis_slot_h - clearance
peg_w = skadis_slot_w - clearance

clearance_depth = 0.1
peg_d = skadis_slot_w - clearance_depth
skadis_slot_d = 5


def create_hook():
    with BuildPart() as part:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, 0, (Align.MIN, Align.CENTER))
        extrude(amount=peg_d)
        with BuildSketch(Plane.XY.offset(peg_d)):
            SlotOverall(peg_h, peg_w, 0, (Align.CENTER, Align.CENTER))
        extrude(amount=peg_d)
    return part

def create_hook_90():
    with BuildPart() as part:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, -90, (Align.MIN, Align.CENTER))
        extrude(amount=peg_d)
        with BuildSketch(Plane.XY.offset(peg_d)):
            SlotOverall(peg_h, peg_w, -90, (Align.CENTER, Align.CENTER))
        extrude(amount=peg_d)
        with BuildSketch(Plane.XY):
            with Locations((0, skadis_slot_h - skadis_slot_w)):
                Rectangle(peg_w, peg_w, align=(Align.CENTER, Align.MAX))
        extrude(amount=peg_d*2, mode=Mode.SUBTRACT)
    return part

def create_snap_hook():
    mid_point_y = wall_height / 2
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XZ):
            with Locations((0, mid_point_y)):
                Rectangle(0.2, 2, align=(Align.MIN, Align.MIN))
            with Locations((0, mid_point_y + 2)):
                Rectangle(5, 2, align=(Align.MIN, Align.MIN))
            triangle_len = 1.1
            triangle_mid = 2.5
            triangle_top = (2.5, mid_point_y + 4 + triangle_len)
            triangle_bottom_left = (triangle_mid - triangle_len, mid_point_y + 4)
            triangle_bottom_right = (triangle_mid + triangle_len, mid_point_y + 4)
            with BuildLine():
                Line(triangle_top, triangle_bottom_right)
                Line(triangle_top, triangle_bottom_left)
                Line(triangle_bottom_left, triangle_bottom_right)
            make_face()
        half_hook = extrude(amount=wall_thickness - 2)
        half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1]
        half_hook = fillet(half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1], 1.0)
        half_hook = fillet(half_hook.faces().filter_by(Axis.X).sort_by(Axis.X)[-1].edges(), 0.5)        # add support bar
        with BuildSketch(Plane.XZ):
            with Locations((4, mid_point_y)):
                Rectangle(1, 4, align=(Align.MIN, Align.MIN))
        extrude(amount=-1)

    half_hook = partBuilder.part
    mirror_plane = Plane.XY.offset(mid_point_y)
    with BuildPart() as partBuilder:
        add(half_hook)
        mirror(half_hook, mirror_plane)
        RigidJoint(label="hookjt", joint_location=Location((0, -(wall_thickness-2)/2, mid_point_y)))

    return partBuilder.part

def create_snap_groove(from_snap_hook: Part):
    with BuildPart() as outer_hook:
        offset(from_snap_hook.part, amount=0.3)
    return outer_hook.part

def create_wall(x_units: int, y_units: int, len_units: int):
    # main part:
    loc = (x_units * slot_spacing, y_units * slot_spacing)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                Rectangle(skadis_slot_w, len_units * slot_spacing, align=(Align.CENTER, Align.MIN))
        extrude(amount=wall_height)
        joint_loc = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1].center_location
        print(joint_loc)
        joint_loc.orientation = (0, 0, 90)
        print(joint_loc)
        RigidJoint(label="wallendjt", joint_location=joint_loc)
    wall = builder.part

    # start extension:
    loc = (loc[0], loc[1]-5)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                Rectangle(5, 5, align=(Align.CENTER, Align.MIN))
        extrude(amount=wall_height)
    start_block = builder.part

    # end extension:
    # loc = (loc[0], loc[1] + len_units * slot_spacing)
    # with BuildPart() as builder:
    #     with BuildSketch(Plane.XY):
    #         with Locations(loc):
    #             Rectangle(5, 5, align=(Align.CENTER, Align.MIN))
    #     extrude(amount=wall_height)

    # create hook as end
    snap_hook = create_snap_hook()
    wall.joints["wallendjt"].connect_to(snap_hook.joints["hookjt"])
    wall_assembly = Compound(label="wall", children=[wall, start_block, snap_hook])
    return wall_assembly

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

# %%
if __name__ == '__main__':
    show_clear()
    # hook = create_hook()
    # hook.label = "hook"
    # hook90 = create_hook_90()
    # hook90.label = "hook90"
    # snap_hook = create_snap_hook()
    # snap_hook.label = "SnapHook"
    # outer_hook = create_snap_groove(snap_hook)
    # outer_hook.label = "SnapHookGroove"
    wall = create_wall(2, 3, 5)
    wall.label = "wall-1"
    # sb.label = "sb"
    # eb.label = "eb"
    show_objects = (
        # hook,
        # hook90,
        # snap_hook,
        # outer_hook,
        wall,
        # sb,
        # eb,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%
