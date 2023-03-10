import ezdxf

from topologicpy.Plotly import Plotly
from topologicpy.Topology import Topology
from topologicpy.Vertex import Vertex
from topologicpy.Edge import Edge
import plotly.offline as ofl
from topologicpy.Wire import Wire


# 加载 dxf 文件
doc = ezdxf.readfile(r'D:\Desktop\Topo\data\test0825.dxf')

# 获取模型空间
msp = doc.modelspace()

# 遍历模型空间中的实体


dxfsx = []
dxfsy = []
dxfsz = []
dxfex = []
dxfey = []
dxfez = []
for entity in msp:
    if entity.dxftype() == 'LINE':  # 只获取线类型的实体
        dxfsx.append(entity.dxf.start.x)
        dxfsy.append(entity.dxf.start.y)
        dxfsz.append(entity.dxf.start.z)
        dxfex.append(entity.dxf.end.x)
        dxfey.append(entity.dxf.end.y)
        dxfez.append(entity.dxf.end.z)
print(dxfsx)
r = None


for x1, y1, z1, x2, y2, z2 in zip(dxfsx, dxfsy, dxfsz, dxfex, dxfey, dxfez):

    #x1,y1,z1,x2,y2,z2 = row.SX,row.SY,row.SZ,row.EX,row.EY,row.EZ
    p1 = Vertex.ByCoordinates(x1, y1, z1)
    p2 = Vertex.ByCoordinates(x2, y2, z2)
    e = Edge.ByVertices([p1, p2])

    if r == None:
        r = e
    else:
        r = r.Merge(e)

plotly_data = Plotly.DataByTopology(r)
plotly_figure = Plotly.FigureByData(plotly_data,width=1100, height=650)
print(plotly_data[0])
ofl.plot(plotly_figure)
#Topology.Show(plotly_figure)