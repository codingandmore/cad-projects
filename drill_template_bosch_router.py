from typing import Iterable
from build123d import *
from ocp_vscode import show_clear,show, show_all

# length = 50
width = 7
thickness = 1
angle = 0
diameter_circle = 95  # diameter of motor and main arc, 103 for arc on connection side
# outer diameter of case: 150, center is shifted to inner diameter by center_holes_distance
radius_circle = diameter_circle / 2
hole_diameter = 4
hole_radius = hole_diameter / 2
small_hole_radius = 1
slot_offset = 5

three_hole_radius = 58.5
two_hole_radius = 67
height_adjustment_radius = 66.5
center_holes_distance = 3.75

def drill_template() -> Part:
    with BuildPart() as part:
        with BuildSketch() as sketch:
            Circle(radius_circle)
            Circle(radius_circle - 4, mode=Mode.SUBTRACT)
            # horizontal markers
            sl = 3 # side length of marker triangle
            with Locations((-radius_circle - center_holes_distance, 0)):
                Triangle(a=sl, A=60, B=60, rotation=30, mode=Mode.SUBTRACT)
            with Locations((radius_circle - center_holes_distance, 0)):
                Triangle(a=sl, A=60, B=60, rotation=-30, mode=Mode.SUBTRACT)
            # top
            with Locations((0, radius_circle)):
                Triangle(a=sl, A=60, B=60, rotation=180, mode=Mode.SUBTRACT)
            # bottom
            with Locations((0, -radius_circle)):
                Triangle(a=sl, A=60, B=60, rotation=0, mode=Mode.SUBTRACT)

            # height adjustment screw
            with Locations(Rot(Z=-28)): # perform a rotation coplanar with `Plane.XY
                length = height_adjustment_radius + slot_offset
                SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
                with Locations((length-5, 0)):
                    Circle(hole_radius, mode=Mode.SUBTRACT)
            # three hole arms:
            with PolarLocations(0, 3, start_angle=34.5):
                length = three_hole_radius + slot_offset
                with Locations((0, 0)):
                    SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
                with Locations((three_hole_radius, 0)):
                    Circle(hole_radius, mode=Mode.SUBTRACT)
            # two hole arms:
            with PolarLocations(0, 2, start_angle=26):
                length = two_hole_radius + slot_offset
                with Locations((0, 0)):
                    SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
                with Locations((two_hole_radius, 0)):
                    Circle(hole_radius, mode=Mode.SUBTRACT)
            # center hole inner circle:
            with Locations((0, 0)):
                Circle(small_hole_radius, mode=Mode.SUBTRACT)
            # center hole outer circle:
            with Locations((-center_holes_distance, 0)):
                Circle(small_hole_radius / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness)
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
    p = drill_template()
    export([p], name="drill_template_v2.stl")
