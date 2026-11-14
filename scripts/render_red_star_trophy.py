from pathlib import Path
import math
from PIL import Image,ImageDraw
S=640
faces=[]
def face(pts,color):
    n=len(pts)
    a=[pts[1][i]-pts[0][i] for i in range(3)]
    b=[pts[2][i]-pts[0][i] for i in range(3)]
    normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    mag=math.sqrt(sum(x*x for x in normal)) or 1
    light=.61+.34*abs(sum(x*y for x,y in zip(normal,(-.37,.69,.62)))/mag)
    highlight=max(0,abs(normal[2])/mag-.76)*.7
    rgb=tuple(min(255,int(c*light+highlight*210)) for c in color)
    faces.append((sum(z+.23*x+.18*y for x,y,z in pts)/n,pts,rgb))
def lathe(profile,color,cx=0,cz=0,n=72):
    for (y,r),(Y,R) in zip(profile,profile[1:]):
        for i in range(n):
            angles=[2*math.pi*j/n for j in (i,i+1)]
            (c,d),(C,D)=[(math.cos(a),math.sin(a)) for a in angles]
            face([(cx+r*c,y,cz+r*d),(cx+r*C,y,cz+r*D),(cx+R*C,Y,cz+R*D),(cx+R*c,Y,cz+R*d)],color)
gold=(255,178,81)
red=(218,62,37)
lathe([(0,0),(0,.46),(.045,.51),(.1,.49),(.12,.45)],gold)
lathe([(.12,.44),(.33,.44),(.36,.48),(.39,.48)],red)
lathe([(.37,.49),(.39,.52),(.44,.52),(.46,.46),(.46,0)],gold)
lathe([(.45,.31),(.49,.31),(.56,.29),(.64,.21),(.73,.15),(.78,.15),(.81,.22)],gold)
lathe([(.8,.21),(.85,.25),(.94,.31),(1.1,.39),(1.34,.49),(1.56,.54),(1.72,.55)],red)
lathe([(1.65,.55),(1.68,.575),(1.76,.57),(1.79,.53),(1.78,.49),(1.68,.49)],gold)
lathe([(1.68,.49),(1.5,.46),(1.42,.33),(1.4,0)],(83,30,20))
for i in range(10):
    a=i*math.tau/10
    lathe([(1.76,.065),(1.81,.065),(2.05+(.13 if i%2 else 0),0)],gold,.51*math.cos(a),.51*math.sin(a),7)
for sign in (-1,1):
    center=[(.41,1.53),(.59,1.66),(.77,1.61),(.85,1.48),(.82,1.34),(.7,1.2),(.58,1.08),(.62,1.0),(.72,1.01)]
    for (x,y),(X,Y) in zip(center,center[1:]):
        for k in range(16):
            a,b=[i*math.tau/16 for i in (k,k+1)]
            r=.063
            face([(sign*x,y+r*math.cos(a),r*math.sin(a)),(sign*X,Y+r*math.cos(a),r*math.sin(a)),(sign*X,Y+r*math.cos(b),r*math.sin(b)),(sign*x,y+r*math.cos(b),r*math.sin(b))],gold)
def star(x,y,z,r):
    p=[(x+math.sin(i*math.pi/5)*r*(1 if i%2==0 else .46),y+math.cos(i*math.pi/5)*r*(1 if i%2==0 else .46),z) for i in range(10)]
    for i,a in enumerate(p):
        b=p[(i+1)%10]
        face([a,b,(x,y,z+.115)], ((255,92,60) if i%2==0 else (153,18,28)))
star(.08,1.34,.565,.32)
star(.05,.245,.455,.12)
out=Image.new("RGBA",(S,S))
draw=ImageDraw.Draw(out)
def project(p):
    x,y,z=p
    return (S*(.5+.34*(x-.24*z)),S*(.88-.34*(.96*y-.20*z)))
for _,pts,rgb in sorted(faces,key=lambda f:f[0]):
    draw.polygon([project(p) for p in pts],fill=rgb+(255,))
out=out.crop(out.getbbox())
out.thumbnail((448,448),Image.Resampling.LANCZOS)
out.save("static/red_star_trophy.webp",lossless=True)
