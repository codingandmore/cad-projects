rotation_angle does not change coordinate system, do not use it

2)
implicit state is problematic:

```py
with BuildPart() as part:
    with BuildSketch(Plane.XY):
        Rectangle(50, 80)

    extrude(amount=length)
    Hole(4)
    fillet(part.edges().filter_by(Axis.Z), 5)
```
works, but:

```py
with BuildPart() as part:
    with BuildSketch(Plane.XY):
        Rectangle(50, 80)

    box = extrude(amount=length)
    print(f"Box has {len(box.edges())}")
    Hole(4)
    fillet(part.edges().filter_by(Axis.Z), 5)
```
does not work

Builder patterns are a great way to create immutable objects that need to be mutable until they're used.
.part, .sketch, .line should be methods: build()

3)
Why is Hole a class but fillet a function?

4)
mesh is invalid when exporting
 two frequent causes:
    part not given to mesher but builder
    invalid object due to self intersection

5)
color lost during .3mf export

6) with context managers often work like iterators
e.g. with Locations(p1, p2, p3):

7)
find edges on a plane does not work as expected

```py
with BuildPart() as part:
    with BuildSketch(Plane.YZ):
        # Triangle(c=50, a=50, B=90, align=Align.MIN)
        Rectangle(width=50, height=30)

    body = extrude(amount=10)
    f = part.faces().sort_by(Axis.Z)[-1]
    pl = Plane(f)
    e = part.edges().filter_by(pl)

8) face not centered correctly

9) offset for plane works in the wrong direction on XZ plane
    with BuildPart() as part:
        with BuildSketch(Plane.XZ) as sk:
            with BuildLine(Plane.XZ):
                l1 = Line((10, 10), (10, 50))
                l2 = offset(amount=5, side=Side.LEFT)
            f = make_face()

10)to test:
pts = [
    (55, 30),
    (50, 35),
    (40, 30),
    (30, 20),
    (20, 25),
    (10, 20),
    (0, 20),
]

with BuildPart() as ex12:
    with BuildSketch() as ex12_sk:
        with BuildLine() as ex12_ln:
            l1 = Spline(pts)
            l2 = Line((55, 30), (60, 0))
            l3 = Line((60, 0), (0, 0))
            l4 = Line((0, 0), (0, 20))
        make_face()
    extrude(amount=10)

ex12 = ex12.part

#ex12.locate(Location(-ex12.bounding_box().center()))   # this works

# reset_show()
# show_object(ex12)

comp = ex12 + Location((0,40,0))*copy.deepcopy(ex12)

comp.locate(-comp.bounding_box().center())              # this doesn't
reset_show()
show_object(comp)

print(comp.show_topology())

-->Your problem is that locate takes a Location and you’ve provided a Vector.
https://www.reddit.com/r/build123d/comments/1gm3dlw/why_cant_i_locate_a_compound/

10) do not set orientation in a builder (oerient.py, v1())
11) properties can be set but have no impact
        right_face = ...
        c = right_face.center(center_of=CenterOf.BOUNDING_BOX)
        print(f'center-bounding-box: {c}')
        workplane = Plane(right_face)
+        print(f'wp center-location: {workplane.location}')
        workplane.location.position = c
        print(f'wp center-location: {workplane.location}')

        center-bounding-box: Vector(5, 25, 20)
wp center-location: Location: (position=(5.00, 20.00, 15.00), orientation=(-0.00, 90.00, -90.00))
wp center-location: Location: (position=(5.00, 20.00, 15.00), orientation=(-0.00, 90.00, -90.00))