# 导入dxf文件
import ezdxf
from topologicpy.Plotly import Plotly
from topologicpy.Topology import Topology
from topologicpy.Vertex import Vertex
from topologicpy.Edge import Edge
import plotly.offline as ofl
from topologicpy.Wire import Wire


def importdxf():
    doc = ezdxf.readfile(r'D:\Desktop\Topo\data\test0304.dxf')
    return doc

def lines(doc):
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
    print("------DXF读取成功------")
    edges = []
    for x1, y1, z1, x2, y2, z2 in zip(dxfsx, dxfsy, dxfsz, dxfex, dxfey, dxfez):
        p1 = Vertex.ByCoordinates(x1, y1, z1)
        p2 = Vertex.ByCoordinates(x2, y2, z2)
        e = Edge.ByVertices([p1, p2])
        edges.append(e)
    wire = Wire.ByEdges(edges)
    wire = MergeCollinearEdges(wire)
    return wire

def showdata(data):
    plotly_data = Plotly.DataByTopology(data)
    plotly_figure = Plotly.FigureByData(plotly_data)
    ofl.plot(plotly_figure)


def MergeCollinearEdges(wire, tol=1e-6):
    """
    Merges collinear edges in the input wire.

    Parameters
    ----------
    wire : topologic.Wire
        The input wire.
    tol : float, optional
        The angular tolerance in radians. The default is 1e-6.

    Returns
    -------
    topologic.Wire
        The wire with collinear edges merged into one.

    """
    vertices = []
    edges = []
    _ = wire.Vertices(None, vertices)
    _ = wire.Edges(None, edges)
    edges_to_remove = []
    for i in range(len(edges) - 1):
        curr_edge = edges[i]
        next_edge = edges[i + 1]
        if Edge.IsCollinear(curr_edge, next_edge, int(tol)):  # 修改这里
            start_vertex = curr_edge.StartVertex()
            end_vertex = next_edge.EndVertex()
            new_edge = Edge.ByStartVertexEndVertex(start_vertex, end_vertex)
            edges_to_remove.extend([curr_edge, next_edge])
            edges.append(new_edge)

    edges = [edge for edge in edges if edge not in edges_to_remove]
    if len(edges) == 1:
        return Wire.ByEdges(edges)
    elif len(edges) > 1:
        return Wire.ByEdges(edges)
    else:
        return None

dxfdata = importdxf()
alllines = lines(dxfdata)
showdata(alllines)
