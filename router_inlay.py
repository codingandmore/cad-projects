from typing import Iterable
from build123d import *
from ocp_vscode import show_clear,show, show_all

length = 200
width = length
thickness = 5
router_cutout_diameter = 35

three_hole_radius = 58.5
two_hole_radius = 67
height_adjustment_radius = 66.5
rounded_corner_radius = 4.25
cs_angle = 90

# height adjustment screw:
height_adjustment_screw_radius = 3

# plate mounting screws M6:
m6_diameter = 6.1
m6_radius = m6_diameter / 2
m6_counter_sink_radius = 6.5 # 12mm for M6 according to DIN 7991

# router mounting screws M4:
m4_diameter = 4 # M4 screws
m4_radius = m4_diameter / 2
m4_counter_sink_radius = 4.5 # 8mm for M4 according to DIN 7991

corner_hole_offset = 12.5

def construct() -> Part:
    with BuildPart() as part:
        with BuildSketch() as sketch:
            RectangleRounded(length, width, radius=rounded_corner_radius)
            # central router cutout
            Circle(router_cutout_diameter / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness)

        # mounting holes at the corners:
        with Locations(part.faces().sort_by(Axis.Z)[-1]):
            hw = width / 2
            hl = length / 2
            locs = [(-hw + corner_hole_offset, -hl + corner_hole_offset),
                    (-hw + corner_hole_offset, hl - corner_hole_offset),
                    (hw - corner_hole_offset, -hl + corner_hole_offset),
                    (hw - corner_hole_offset, hl - corner_hole_offset)]
            with Locations(locs):
                CounterSinkHole(m6_radius, m6_counter_sink_radius, counter_sink_angle=cs_angle)

            # height adjustment screw
            with Locations(Rot(Z=-28)): # perform a rotation coplanar with Plane.XY
                with Locations((height_adjustment_radius, 0)):
                    Hole(height_adjustment_screw_radius)
            # three hole arms:
            with PolarLocations(0, 3, start_angle=34.5):
                with Locations((three_hole_radius, 0)):
                    CounterSinkHole(m4_radius, m4_counter_sink_radius, counter_sink_angle=cs_angle)
            # two hole arms:
            with PolarLocations(0, 2, start_angle=26):
                with Locations((two_hole_radius, 0)):
                    CounterSinkHole(m4_radius, m4_counter_sink_radius, counter_sink_angle=cs_angle)
    show_all()
    return part.part


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
    exporter.add_code_to_metadata()
    exporter.write(name)

if __name__ == "__main__":
    part = construct()
    export((part), "router_inlay.3mf")
