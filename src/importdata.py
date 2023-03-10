import ezdxf
from topologicpy.Plotly import Plotly
from topologicpy.Topology import Topology
from topologicpy.Vertex import Vertex
from topologicpy.Edge import Edge
from topologicpy.Face import Face
from topologicpy.Cell import Cell
from topologicpy.Cluster import Cluster
import plotly.offline as ofl
from topologicpy.Wire import Wire
import numpy as np


def importdxf():
    # 导入dxf文件
    doc = ezdxf.readfile(r'D:\Desktop\Topo\data\test0825.dxf')
    return doc


def dxflines(doc):
    # 输入dxf文件 返回其所有线列表 以edge输出
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
    elist = []
    for x1, y1, z1, x2, y2, z2 in zip(dxfsx, dxfsy, dxfsz, dxfex, dxfey, dxfez):
        p1 = Vertex.ByCoordinates(x1, y1, z1)
        p2 = Vertex.ByCoordinates(x2, y2, z2)
        e = Edge.ByVertices([p1, p2])
        elist.append(e)
    return elist


def flatten(nested_list):
    """
    将嵌套列表拍平为一维列表的函数。

    参数：
    nested_list -- 嵌套列表

    返回值：
    一维列表
    """
    flat_list = []
    for sublist in nested_list:
        if isinstance(sublist, list):
            flat_list.extend(flatten(sublist))
        else:
            flat_list.append(sublist)
    return flat_list


def showdata(data):
    # 输入拓扑 完成显示 转成Cluster 可视化
    # data = Cluster.ByTopologies(data)
    if type(data) == list:
        data = flatten(data)
        r = None
        for topo in data:
            if r == None:
                r = topo
            else:
                r = r.Merge(topo)
    else:
        r = data
    plotly_data = Plotly.DataByTopology(r)
    plotly_figure = Plotly.FigureByData(plotly_data)
    ofl.plot(plotly_figure)


# def group_by_collinear_11111111(edges):  # 按照共线的原则对edge分组
#     groups = []
#     for e in edges:
#         added_to_group = False  # 是否有和它共线的标记，默认为无
#         if groups == []:
#             groups.append([e])  # 第一条边作为第一组
#             added_to_group = True
#             continue
#         else:
#             for group in groups:  # [[],[],[]]
#                 for item in group:  # [..., ..., ..., ...]
#                     print(Edge.IsCollinear(e, item))
#                     if Edge.IsCollinear(e, item):  # 发生了共线事件，退出本次循环，并将该线加入这一组
#                         added_to_group = True
#                         # break
#                 if added_to_group:
#                     group.append(e)
#                     break
#         if not added_to_group:  # 没有共线的，加入新的组
#             groups.append([e])
#     return groups
#
#
# def group_by_collinear(edges):  # 按照共线的原则对edge分组
#     groupflag = [0] * len(edges)
#     groupnum = 0
#     for i in range(0, len(edges)):
#         for j in range(i, len(edges)):  # 和除自己外的每一条线判断是否共线
#             if i != j:
#                 if Edge.IsCollinear(edges[i], edges[j]):  # 发生共线，则修改那一条线的flag,且与这条线共线的所有线的flag
#                     groupflag[j] = groupflag[i]
#                     groupflag = update_flag(groupflag, groupflag[j], groupflag[i])
#                 else:
#                     groupflag[j] = groupnum
#                     groupnum += 1
#     print(groupflag)
#
#     r = []
#     groupSet = set(groupflag)
#     print(groupSet)
#     for groupf in groupSet:
#         eds = []
#         for i in range(0, len(groupflag)):
#             if groupflag[i] == groupf:
#                 eds.append(edges[i])
#         r.append(eds)
#     return r


def group_by_parallel(edges):  # 按平行分组
    groups = []
    for e in edges:
        added_to_group = False
        for group in groups:
            for item in group:
                if Edge.IsParallel(e, item):
                    group.append(e)
                    added_to_group = True
                    break
            if added_to_group:
                break
        if not added_to_group:
            groups.append([e])
    return groups


def distofedges(edgeA, edgeB):  # 求两边的真实距离
    svA = Edge.StartVertex(edgeA)
    evA = Edge.EndVertex(edgeA)
    svB = Edge.StartVertex(edgeB)
    evB = Edge.EndVertex(edgeB)
    d1 = Vertex.Distance(svA, svB)
    d2 = Vertex.Distance(svA, evB)
    d3 = Vertex.Distance(evA, svB)
    d4 = Vertex.Distance(evA, evB)
    return min(d1, d2, d3, d4)


def find_connected_edges(edges, start_edge, visited, stack):
    # 初始化当前连通分量
    connected_edges = [start_edge]
    visited.add(start_edge)
    stack.append(start_edge)

    # 遍历与 start_edge 相邻的所有边
    for edge in edges:
        if edge not in visited and distofedges(start_edge, edge) == 0:
            connected_edges += find_connected_edges(edges, edge, visited, stack)

    # 弹出已访问的线段，恢复之前的遍历路径
    stack.pop()

    return connected_edges


def group_edges(edges):
    groups = []
    visited = set()

    # 遍历所有线段，找到每个连通分量
    for edge in edges:
        if edge not in visited:
            stack = []
            connected_edges = find_connected_edges(edges, edge, visited, stack)
            groups.append(connected_edges)

    return groups


#
# def update_flag(arr, target, value):
#     newarr = []
#     for item in arr:
#         if target != 0 & item == target:
#             newarr.append(value)
#         else:
#             newarr.append(item)
#
#     return newarr


def find_extreme_vertices(vlist):
    # 使用sorted()按x坐标排序，如果相同，则按y坐标排序
    sorted_vlist = sorted(vlist, key=lambda v: (round(v.X(), 3), round(v.Y(), 3)))

    # 找到最大和最小的两个点
    min_x = sorted_vlist[0]
    max_x = sorted_vlist[-1]

    # 如果最大和最小x坐标相同，则按y坐标排序并返回最大和最小的两个点
    if round(min_x.X(), 3) == round(max_x.X(), 3):
        sorted_vlist = sorted(vlist, key=lambda v: round(v.Y(), 3))
        min_y = sorted_vlist[0]
        max_y = sorted_vlist[-1]
        return min_y, max_y

    return min_x, max_x


def allvertex(edges):  # 输入edge列表 返回所有顶点
    vlist = []
    for e in edges:
        v = Edge.Vertices(e)
        vlist.append(v[0])
        vlist.append(v[1])
    return vlist


def newedge(groups):  # 对分组后的edge合并，寻找最两侧的点，创建新的edge
    result = []
    for group in groups:
        vlist = allvertex(group)
        extreme_points = find_extreme_vertices(vlist)
        line = Edge.ByStartVertexEndVertex(extreme_points[0], extreme_points[1])
        result.append(line)
    return result


def tooneline(elist):
    r = []
    result = []
    for edges in elist:
        t = group_edges(edges)
        print(t)
        r.append(t)
    print("排序完成")
    for i in r:
        result.append(newedge(i))
    return result


dxfdata = importdxf()
elist = dxflines(dxfdata)  # edge的列表
paralist = group_by_parallel(elist)  # 按照平行分组 只有横竖线时分为2组
print(len(paralist))


def find_points_with_distance(vertices, distance=300):
    result = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            d = round(Vertex.Distance(vertices[i], vertices[j]))
            if d == distance:
                result.append([vertices[i], vertices[j]])
    return result


def addshortedge(elist):  # 补全共线但距离为distance的线段
    shortedge = []
    for edges in elist:
        allv = allvertex(edges)
        allv = find_points_with_distance(allv)
        print(allv)
        for vs in allv:
            tempedge = Edge.ByStartVertexEndVertex(vs[0], vs[1])
            if Edge.IsParallel(tempedge, edges[0]):
                shortedge.append(tempedge)
        edges.append(shortedge)
    return elist


m = addshortedge(paralist)
showdata(m[0])

# # print(paralist)
#
# print("..................................................")
#
#
#
# t = tooneline(paralist)
# print(len(t))
#
# showdata(t)
#


# h = group_edges(elist)
# print(h)
#
# print(".............................")
# r = []
# for i in h:
#
#     q = Wire.ByEdges(i)
#     r.append(q)
# print(r)
# u = Wire.Interpolate(r,n=9)
# print(u)
#

#
# showdata(u)
# allvertex(elist)
# q = group_by_neigh(elist)
#

# print(q)


# print(len(h))
# o = group_by_neigh(h)
# print(o)


# h = group_by_collinear(elist)  # 按照共线分组
# print(h)
# print(len(h))
# print(Edge.IsCollinear(h[0][1], h[1][0]))
# n = newedge(o)
# print(n)

# import pprint
# pprint.pprint(len(h))
# pprint.pprint(h)

# g = newedge(h)
# print(g)


#
# print(elist)
# print(len(elist))
# print(Edge.IsParallel(elist[0],elist[1]))
# print(Edge.IsCollinear(elist[0],elist[1]))
#
#
# a = group_collinear_edges(elist)
# print(a)
# print(len(a))
# e = Wire.ByEdges(elist)
# print(e)


#
# f = Face.ByEdges(elist)
# g = Cell.ByThickenedFace(f,100.0)
#
# h = Cell.Wires(g)
# print(h)


# plotly_data = Plotly.DataByTopology(n)
# plotly_figure = Plotly.FigureByData(plotly_data)
# ofl.plot(plotly_figure)
