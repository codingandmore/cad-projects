from build123d import *
from ocp_vscode import show_clear,show, show_all

def bar_and_hole2():
    length = 50
    height = 20
    thickness = 2
    angle = 45  # 45
    radius = 1
    hole_diameter = 2

    with BuildPart() as part:
        bar_location = Location((10, 10, 0), (0, 0, angle))
        with BuildSketch(bar_location) as sketch:
            with BuildLine() as profile:
                line = PolarLine((0, 0), length, 0)
                offset(amount=thickness, side=Side.BOTH)
            f = make_face()
        extrude(amount=thickness)

        face = part.faces().sort_by(Axis.Z)[0]

        # This locates the face, and could use rotated coordinates.
        # The * operation means applying location in the local coordinate system
        face_loc = face.center_location
        # The default orientation of face center is (-X, Y, -Z)
        # needs to be updated
        # loc = face_loc * Location((15, 0, 0))
        face_loc.orientation = bar_location.orientation
        loc = face_loc * Location((15, 0, 0))

        with Locations(loc):
            Hole(hole_diameter / 2)
    show(part)

def jerns_solution():
    length = 50
    height = 20
    thickness = 2
    angle = 45
    radius = 1
    hole_diameter = 2

    with BuildPart() as part:
        with BuildSketch() as sketch:
            with Locations(Rot(Z=45)): # perform a rotation coplanar with `Plane.XY               
                SlotOverall(length, 2 * thickness)
                with Locations((15, 0)):
                    Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness)

def with_polar_locations():
    length = 50
    hole_diameter = 2
    thickness = 2

    with BuildPart() as part:
        with BuildSketch():
            with PolarLocations(0, 3):
                with Locations((length / 2, 0)):
                    SlotCenterToCenter(length, 5)
                with Locations((45, 0)):
                    Circle(hole_diameter / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness)
    return part


# bar_and_hole2()
# jerns_solution()
part = with_polar_locations()
show(part)
