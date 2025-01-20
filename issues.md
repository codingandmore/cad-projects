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
