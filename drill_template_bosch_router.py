from build123d import *
from ocp_vscode import show_clear,show, show_all

# length = 50
width = 8
thickness = 2
angle = 0
diameter_circle = 103
hole_diameter = 2
slot_offset = 5

three_hole_radius = 58.5
two_hole_radius = 67
height_adjustment_radius = 65.5

with BuildPart() as part:
    with BuildSketch() as sketch:
        Circle(diameter_circle / 2)
        Circle(diameter_circle / 2 - 4, mode=Mode.SUBTRACT)
        # height adjustment screw
        with Locations(Rot(Z=-28)): # perform a rotation coplanar with `Plane.XY
            length = height_adjustment_radius + slot_offset
            SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
            with Locations((length-5, 0)):
                Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        # three hole arms:
        with PolarLocations(0, 3, start_angle=34.5):
            length = three_hole_radius + slot_offset
            with Locations((0, 0)):
                SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
            with Locations((three_hole_radius, 0)):
                Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        # two hole arms:
        with PolarLocations(0, 2, start_angle=26):
            length = two_hole_radius + slot_offset
            with Locations((0, 0)):
                SlotOverall(length, width, align=(Align.MIN, Align.CENTER))
            with Locations((two_hole_radius, 0)):
                Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        # center hole outer circle:
        with Locations((0, 0)):
            Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        # center hole inner circle:
        with Locations((-2, 0)):
            Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

show_all()
