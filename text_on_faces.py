from ocp_vscode import show_clear,show, show_all, Camera
from build123d import *

r_len = 50
r_width = 10
r_height = 30


def vertical_text_on_left_wall():
    org_x = 20
    org_y = 10
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations((org_x, org_y)):
                    Rectangle(r_width, r_len, align=(Align.MIN, Align.MIN))
        extrude(amount=r_height)

        text_face = faces().filter_by(Plane.YZ).sort_by(Axis.X)[0]
        c = text_face.center()
        print(f'{c=}')
        # orig = c +  (0, r_len / 2, r_height / 2)
        orig = c + (0, text_face.length / 2, text_face.width / 2)
        print(f'{orig=}')
        text_plane = Plane(origin=orig, x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
        with BuildSketch(text_plane):
                Text("Hello", font_size=5, align=(Align.MIN, Align.MAX))
        extrude(amount=+0.6, mode=Mode.ADD)
    return builder.part

def horizontal_text_on_bottom_wall():
    org_x = 40
    org_y = 30
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations((org_x, org_y)):
                    Rectangle(r_len, r_width, align=(Align.MIN, Align.MIN))
        extrude(amount=r_height)

        text_face = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0]
        c = text_face.center()
        print(f'{c=}')
        # orig = c +  (-r_len / 2, 0, r_height / 2)
        orig = c +  (-text_face.length / 2, 0, text_face.width / 2)
        print(f'{orig=}')
        text_plane = Plane(origin=orig, x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        with BuildSketch(text_plane):
            Text("Hello", font_size=5, align=(Align.MIN, Align.MAX))
        extrude(amount=+0.6, mode=Mode.SUBTRACT)
    return builder.part, text_plane # displaying the plane gives orientation of plane

boxv = vertical_text_on_left_wall()
boxh, tf2 = horizontal_text_on_bottom_wall()

show_clear()
show_all()

