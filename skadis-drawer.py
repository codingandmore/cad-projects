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
wall_thickness = skadis_slot_w # do not change!
slot_spacing = 20
double_slot_spacing = 2 * slot_spacing
hook_offset_row = slot_spacing - skadis_slot_w + clearance / 2 # initial offset for hook to align with next wall
peg_h = skadis_slot_h - clearance
peg_w = skadis_slot_w - clearance

clearance_depth = 0.1
peg_d = skadis_slot_w - clearance_depth
skadis_slot_d = 5


def create_hook(cut_to_thickness: bool=False):
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, -90, (Align.MIN, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY.offset(-peg_d)):
            SlotOverall(peg_h, peg_w, -90, (Align.CENTER, Align.CENTER))
        extrude(amount=-peg_d)
        if cut_to_thickness:
            with BuildSketch(Plane.XY):
                with Locations((0, -skadis_slot_w)):
                    Rectangle(peg_w, peg_w, align=(Align.CENTER, Align.MAX))
            extrude(amount=-peg_d*2, mode=Mode.SUBTRACT)
        joint_loc = Location((0,0,0))
        RigidJoint(label="foot-jt", joint_location=joint_loc)
    return partBuilder.part

def create_hook_90():
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, 0, (Align.MIN, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY.offset(-peg_d)):
            SlotOverall(peg_h, peg_w, 0, (Align.CENTER, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY):
            with Locations((0, skadis_slot_h - skadis_slot_w)):
                Rectangle(peg_w, peg_w, align=(Align.CENTER, Align.MAX))
        extrude(amount=-peg_d*2, mode=Mode.SUBTRACT)
    return partBuilder.part

def create_snap_hook_internal(with_support: bool=True, for_subtract: bool=False):
    mid_point_y = wall_height / 2

    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XZ):
            if (for_subtract):
                with Locations((0, mid_point_y)):
                    Rectangle(wall_thickness, 4, align=(Align.MIN, Align.MIN))
            else:
                with Locations((0, mid_point_y)):
                    Rectangle(0.2, 2, align=(Align.MIN, Align.MIN))
                with Locations((0, mid_point_y + 2)):
                    Rectangle(wall_thickness, 2, align=(Align.MIN, Align.MIN))
            triangle_len = 1.1
            triangle_mid = wall_thickness / 2
            triangle_top = (triangle_mid, mid_point_y + 4 + triangle_len)
            triangle_bottom_left = (triangle_mid - triangle_len, mid_point_y + 4)
            triangle_bottom_right = (triangle_mid + triangle_len, mid_point_y + 4)
            with BuildLine():
                Line(triangle_top, triangle_bottom_right)
                Line(triangle_top, triangle_bottom_left)
                Line(triangle_bottom_left, triangle_bottom_right)
            make_face()
        half_hook = extrude(amount=wall_thickness - 2)
        if (for_subtract):
            offset(amount=0.3)
        else:
            half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1]
            half_hook = fillet(half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1], 1.0)
            half_hook = fillet(half_hook.faces().filter_by(Axis.X).sort_by(Axis.X)[-1].edges(), 0.5)
            # add support bar
            if (with_support):
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

def create_snap_hook(with_support: bool=True):
    return  create_snap_hook_internal(False)

def create_snap_groove():
    mid_point_y = wall_height / 2
    snap_hook = create_snap_hook_internal(False, True)
    RigidJoint(label="groovejt", to_part=snap_hook, joint_location=Location((0, -(wall_thickness-2)/2, mid_point_y)))
    return snap_hook

def create_wall(x_units: int, y_units: int, len_units: int):
    # main part:
    loc = (x_units * slot_spacing, y_units * slot_spacing)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                Rectangle(skadis_slot_w, len_units * slot_spacing, align=(Align.CENTER, Align.MIN))
        extrude(amount=wall_height)
        # create joints at start and to attach extensions
        joint_loc = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1].center_location
        joint_loc.orientation = (0, 0, 90)
        RigidJoint(label="wallendjt", joint_location=joint_loc)
        joint_loc = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0].center_location
        joint_loc.orientation = (0, 0, 270)
        RigidJoint(label="wallstartjt", joint_location=joint_loc)
        joint_loc = faces().filter_by(Plane.XY).sort_by(Axis.Z)[0].center_location
        joint_loc.position -= (0, (len_units * slot_spacing / 2), 0)
        joint_loc.orientation = (0, 0, 0)
        RigidJoint(label="wallfootjt", joint_location=joint_loc)
    wall = builder.part

    # start extension:
    # create groove at start
    snap_groove = create_snap_groove()
    wall.joints["wallstartjt"].connect_to(snap_groove.joints["groovejt"])

    # create bar
    loc = (loc[0], loc[1] - wall_thickness)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                Rectangle(wall_thickness, wall_thickness, align=(Align.CENTER, Align.MIN))
        extrude(amount=wall_height)
        add(snap_groove, mode=Mode.SUBTRACT)
    start_block = builder.part

    # end extension:
    # loc = (loc[0], loc[1] + len_units * slot_spacing)
    # with BuildPart() as builder:
    #     with BuildSketch(Plane.XY):
    #         with Locations(loc):
    #             Rectangle(wall_thickness, wall_thickness, align=(Align.CENTER, Align.MIN))
    #     extrude(amount=wall_height)


    # create hook at end
    snap_hook = create_snap_hook()
    wall.joints["wallendjt"].connect_to(snap_hook.joints["hookjt"])

    # create feet:
    foot = create_hook()
    wall.joints["wallfootjt"].connect_to(foot.joints["foot-jt"])
    # with GridLocations(x_spacing=1, y_spacing=slot_spacing, x_count=1, y_count=len_units):
    #     foot = copy.copy(foot)
    # locs = GridLocations(x_spacing=1, y_spacing=slot_spacing * 2, x_count=1, y_count=int(len_units / 2))# .local_locations
    wall_elems = [wall, start_block, snap_hook, foot]
    print(foot.position)
    for p in range (1,  int(len_units / 2) + 1):
        l = Location((0, p * slot_spacing * 2, 0))
        f = foot.moved(l)
        wall_elems += f
    print(len(wall_elems))
    wall_assembly = Compound(label="wall", children=wall_elems)
    # attach feet
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
    # snap_hook = create_snap_hook(False)
    # snap_hook.label = "SnapHook"
    # snap_groove = create_snap_groove()
    # snap_groove.label = "SnapHookGroove"
    wall = create_wall(2, 3, 5)
    wall.label = "wall-1"
    # sb.label = "sb"
    # eb.label = "eb"
    show_objects = (
        # hook,
        # hook90,
        # snap_hook,
        # snap_groove,
        wall,
        # sb,
        # eb,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%
