from build123d import *
from ocp_vscode import show_clear,show, show_all

def construct():
    length = 150
    dm_absaug = 35
    with BuildPart() as part:
        with BuildSketch(Plane.YZ):
            t = Triangle(c=50, a=50, B=90, align=Align.MIN)
            hyp = t.edge_b
            
        extrude(amount=length)
        f = part.faces().sort_by(SortBy.AREA)[-1]     
        edge_x0 = part.edges().sort_by(Axis.Y).sort_by(Axis.Z)[0]
        with BuildSketch(f):
            Circle(dm_absaug / 2)
        
        extrude(amount=-f.distance(edge_x0), mode=Mode.SUBTRACT)
        
        with BuildSketch(Plane.XY.offset(10)) as x:
            with Locations((30, 25, 0)):
                r = Rectangle(20, 30)
        
        extrude(amount=t.a, mode=Mode.SUBTRACT)            

    show_all()

if __name__ == '__main__':
    show_clear()
    construct()
    
