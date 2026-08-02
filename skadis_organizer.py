import copy
from build123d import *
from math import asin, acos, atan, ceil, degrees, sin, cos, tan, radians, radians, pi, sqrt
from enum import Enum

class SkadisOrganizer:
    class Orientation(Enum):
        HORIZONTAL = 1
        VERTICAL = 2


    # constants, do not change:
    slot_spacing = 20
    skadis_slot_len = 15
    skadis_slot_w = 5
    clearance = 0.3
    wall_thickness = skadis_slot_w
    double_slot_spacing = 2 * slot_spacing
    clearance_depth = 0.1
    peg_h = skadis_slot_len - clearance
    peg_w = skadis_slot_w - clearance
    peg_d = skadis_slot_w - clearance_depth
    board_thickness = 5


    def __init__(self, wall_height:int= 30):
        self. wall_height = wall_height

    def create_board(self, x_units: int, y_units: int, border_x: int=0, border_y: int=0, start_indented: bool=False) -> Part:
        with BuildPart() as partBuilder:
            with BuildSketch(Plane.XY):
                with Locations((-border_x, -border_y, 0)):
                    Rectangle(x_units * self.slot_spacing + 2 * border_x, y_units * self.slot_spacing + 2 * border_y, align=(Align.MIN, Align.MIN))
                half_x = int(x_units / 2)
                half_y = int(y_units / 2)
                x1_off, x2_off = (self.slot_spacing, 0) if start_indented else (0, self.slot_spacing)
                with Locations((x1_off, 0)):
                    with GridLocations(x_spacing=self.double_slot_spacing, y_spacing=self.double_slot_spacing,
                                x_count=half_x, y_count=half_y, align=(Align.MIN, Align.MIN)):
                        SlotOverall(self.skadis_slot_len, self.skadis_slot_w, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
                with Locations((x2_off, self.slot_spacing)):
                    with GridLocations(x_spacing=self.double_slot_spacing, y_spacing=self.double_slot_spacing,
                                    x_count=half_x, y_count=half_y, align=(Align.MIN, Align.MIN)):
                        SlotOverall(self.skadis_slot_len, self.skadis_slot_w, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)

            extrude(amount=-self.board_thickness)
        return partBuilder.part

    def create_wall(self, x_units: int, y_units: int, len_units: int, orientation: Orientation, left_groove: bool=False, name: str = None) -> Compound:
        # depending on if we are on an even or odd row the first slot is offseted
        feet_offset = 0
        if x_units & 1 != y_units & 1:
            feet_offset = self.slot_spacing
        return self._create_wall_intern(x_units, y_units, len_units, orientation, left_groove, feet_offset, False, name)

    def create_adapter(self, x_units: int, y_units: int, len_units: int=1, name: str = None) -> Compound:
        if x_units & 1 != y_units & 1:
            feet_offset = self.slot_spacing if len_units > 1 else -1 # no feet
        else:
            feet_offset = self.slot_spacing * 2 if len_units > 2 else -1 # no feet
        return self._create_wall_intern(x_units, y_units, len_units, self.Orientation.HORIZONTAL, False, feet_offset, True, name)

    # internal functions
    def _create_hook(self, cut_to_thickness: bool=False)-> Part:
        with BuildPart() as partBuilder:
            with BuildSketch(Plane.XY):
                SlotOverall(self.peg_h / 2, self.peg_w, -0, (Align.MIN, Align.CENTER))
            extrude(amount=-self.peg_d)
            with BuildSketch(Plane.XY.offset(-self.peg_d)):
                SlotOverall(self.peg_h, self.peg_w, 0, (Align.CENTER, Align.CENTER))
            extrude(amount=-self.peg_d)
            if cut_to_thickness:
                with BuildSketch(Plane.XY):
                    with Locations((self.skadis_slot_w, 0)):
                        Rectangle(self.peg_w, self.peg_w, align=(Align.MIN, Align.CENTER))
                extrude(amount=-self.peg_d*2, mode=Mode.SUBTRACT)
            joint_loc = Location((0,0,0))
            RigidJoint(label="foot-jt", joint_location=joint_loc)
        return partBuilder.part

    def _create_snap_hook_internal(self, with_support: bool=True, for_subtract: bool=False):
        mid_point_y = self.wall_height / 2

        with BuildPart() as partBuilder:
            with BuildSketch(Plane.XZ):
                if (for_subtract):
                    with Locations((0, mid_point_y)):
                        Rectangle(self.wall_thickness, 4, align=(Align.MIN, Align.MIN))
                else:
                    with Locations((0, mid_point_y)):
                        Rectangle(0.2, 2, align=(Align.MIN, Align.MIN))
                    with Locations((0, mid_point_y + 2)):
                        Rectangle(self.wall_thickness, 2, align=(Align.MIN, Align.MIN))
                triangle_len = 1.1
                triangle_mid = self.wall_thickness / 2
                triangle_top = (triangle_mid, mid_point_y + 4 + triangle_len)
                triangle_bottom_left = (triangle_mid - triangle_len, mid_point_y + 4)
                triangle_bottom_right = (triangle_mid + triangle_len, mid_point_y + 4)
                with BuildLine():
                    Line(triangle_top, triangle_bottom_right)
                    Line(triangle_top, triangle_bottom_left)
                    Line(triangle_bottom_left, triangle_bottom_right)
                make_face()
            half_hook = extrude(amount=self.wall_thickness - 2)
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

        return partBuilder.part

    def _create_snap_hook(self, with_support: bool=True) -> Part:
        hook = self._create_snap_hook_internal(False)
        RigidJoint(label="hookjt", to_part=hook, joint_location=Location((0, -(self.wall_thickness-2)/2,self. wall_height / 2)))
        return hook

    def _create_snap_groove(self):
        snap_hook = self._create_snap_hook_internal(False, True)
        face = snap_hook.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
        joint_loc = Location(face.center_location.position, 180)
        RigidJoint(label="groovejt", to_part=snap_hook, joint_location=joint_loc)
        return snap_hook

    def _create_wall_intern(
            self,
            x_units: int,
            y_units: int,
            len_units: int,
            orientation: Orientation,
            left_groove: bool,
            feet_offset: int,
            is_adapter: bool = False,
            name: str = None,
        ) -> Compound:

        # main part:
        wall = self._create_wall_with_groove_intern(x_units, y_units, len_units, orientation, left_groove, feet_offset, is_adapter, name)

        # create hook at end
        snap_hook = self._create_snap_hook()
        wall.joints["wallendjt"].connect_to(snap_hook.joints["hookjt"])


        # print(f'{no_feet=}, {len_units=}, {feet_offset=}, {remaining_wall_len=}')
        wall_elems = [wall, snap_hook]
        if is_adapter:
            snap_hook2 = self._create_snap_hook()
            wall.joints["wallstartjt"].connect_to(snap_hook2.joints["hookjt"])
            wall_elems += snap_hook2

        # create feet:
        if feet_offset >= 0:
            remaining_wall_len = len_units * self.slot_spacing - feet_offset
            no_feet = ceil(remaining_wall_len / (self.slot_spacing * 2))
            wall_elems += self._create_feet(orientation, no_feet, wall)
        return Compound(children=wall_elems)

    def _create_wall_with_groove_intern(
            self,
            x_units: int,
            y_units: int,
            len_units: int,
            orientation: Orientation,
            left_groove: bool,
            feet_offset: int,
            is_adapter: bool = False,
            name: str = None,
        ) -> Part:
        x0 = x_units * self.slot_spacing
        if is_adapter:
            x0 += self.wall_thickness
        loc = (x0, y_units * self.slot_spacing)

        with BuildPart() as builder:
            with BuildSketch(Plane.XY):
                with Locations(loc):
                    len_rect = len_units * self.slot_spacing
                    if orientation is self.Orientation.VERTICAL:
                        Rectangle(self.skadis_slot_w, len_rect, align=(Align.MIN, Align.MIN))
                    else:
                        if is_adapter:
                            len_rect -= self.wall_thickness
                        Rectangle(len_rect, self.skadis_slot_w, align=(Align.MIN, Align.MIN))
            extrude(amount=self.wall_height)

            joint_loc_feet = faces().filter_by(Plane.XY).sort_by(Axis.Z)[0].center_location
            joint_loc_feet.orientation = (0, 0, 0)
            if orientation is self.Orientation.VERTICAL:
                joint_loc_end = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1].center_location
                joint_loc_start = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0].center_location
                joint_loc_mid = copy.copy(joint_loc_start)
                joint_loc_feet.position -= (self.skadis_slot_w / 2, (len_units * self.slot_spacing / 2) - self.skadis_slot_w / 2 - feet_offset, 0)
                if left_groove:
                    joint_loc_start.position += (-self.skadis_slot_w / 2, self.skadis_slot_w / 2, 0)
                    joint_loc_start.orientation = (0, 0, 180)
                else:
                    joint_loc_start.orientation = (0, 0, 270)
                joint_loc_end.orientation = (0, 0, 90)
                joint_loc_mid.position += (-self.skadis_slot_w / 2, self.skadis_slot_w / 2 + self.slot_spacing, 0)
                joint_loc_mid.orientation = (0, 0, 180)
                text_face = faces().filter_by(Plane.YZ).sort_by(Axis.X)[0]
                text_orig = text_face.center() + (0, text_face.length / 2, text_face.width / 2)
                text_x_dir=(0, -1, 0)
                text_z_dir=(-1, 0, 0)
            else:
                joint_loc_end = faces().filter_by(Plane.YZ).sort_by(Axis.X)[-1].center_location
                joint_loc_start = faces().filter_by(Plane.YZ).sort_by(Axis.X)[0].center_location
                joint_loc_mid = copy.copy(joint_loc_start)
                joint_loc_feet.position -= (len_units * self.slot_spacing / 2 - feet_offset, 0, 0)
                joint_loc_end.orientation = (0, 0, 0)
                joint_loc_mid.position += (self.skadis_slot_w / 2 + self.slot_spacing, self.skadis_slot_w / 2, 0)
                joint_loc_mid.orientation = (0, 0, 90)
                if left_groove:
                    joint_loc_start.position += (self.skadis_slot_w / 2, self.skadis_slot_w / 2, 0)
                    joint_loc_start.orientation = (0, 0, 90)
                else:
                    joint_loc_start.orientation = (0, 0, 180)
                text_face = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0]
                text_orig = text_face.center() + (-text_face.length / 2, 0, text_face.width / 2)
                text_x_dir=(1, 0, 0)
                text_z_dir=(0, -1, 0)
            RigidJoint(label="wallstartjt", joint_location=joint_loc_start)

            # add text
            if name:
                text_plane = Plane(origin=text_orig, x_dir=text_x_dir, z_dir=text_z_dir)
                with BuildSketch(text_plane):
                    with Locations((3,-3)):
                        Text(name, font_size=5, align=(Align.MIN, Align.MAX))
                extrude(amount=+0.6, mode=Mode.ADD)
        wall = builder.part

        # create groove at start
        if not is_adapter:
            snap_groove = self._create_snap_groove()
            wall.joints["wallstartjt"].connect_to(snap_groove.joints["groovejt"])

        with BuildPart() as builder:
            add(wall)
            if not is_adapter:
                add(snap_groove, mode=Mode.SUBTRACT)
            RigidJoint(label="wallstartjt", joint_location=joint_loc_start)
            RigidJoint(label="wallendjt", joint_location=joint_loc_end)
            RigidJoint(label="wallfootjt", joint_location=joint_loc_feet)
            RigidJoint(label="wallmidjt", joint_location=joint_loc_mid)
            # add all other grooves along the wall
            if left_groove:
                count = len_units
                snap_groove2 = snap_groove
            else:
                # create and connect a second groove rotated 90° to first one
                snap_groove2 = self._create_snap_groove()
                builder.joints["wallmidjt"].connect_to(snap_groove2.joints["groovejt"])
                count = len_units - 1

            if orientation is self.Orientation.VERTICAL:
                xc = 1
                yc = count
            else:
                xc = count
                yc = 1

            if count > 0:
                with GridLocations(x_spacing=self.slot_spacing, y_spacing=self.slot_spacing,
                        x_count=xc, y_count=yc, align=(Align.MIN, Align.MIN)):
                    add(snap_groove2, mode=Mode.SUBTRACT)
        wall = builder.part
        wall.label = name
        return wall

    def _create_feet(self, orientation: Orientation, no_feet: int, wall: Part) -> list[Part]:
        foot = self._create_hook(cut_to_thickness=True if orientation is self.Orientation.VERTICAL else False)
        wall.joints["wallfootjt"].connect_to(foot.joints["foot-jt"])
        feet_elems = [foot]

        for p in range (1,  no_feet):
            pos = p * self.slot_spacing * 2
            if orientation is self.Orientation.VERTICAL:
                l = Location((0, pos, 0))
            else:
                l = Location((pos, 0, 0))
            f = foot.moved(l)
            feet_elems += f
        return feet_elems
