import math
import ezdxf
import numpy as np
from math import sqrt
from shapely.geometry import Point, LineString
from collections import defaultdict
from topologicpy.Vertex import Vertex
from topologicpy.Edge import Edge
from topologicpy.Wire import Wire
from topologicpy.Face import Face
from topologicpy.Cell import Cell
from topologicpy.Cluster import Cluster
from topologicpy.Plotly import Plotly
from topologicpy.Topology import Topology
import plotly.offline as ofl


def importdxf(src):
    # 导入dxf文件
    doc = ezdxf.readfile(src)
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


def group_segments_by_direction(edges):
    groups = defaultdict(list)
    for edge in edges:
        start_vertex = edge.StartVertex()
        end_vertex = edge.EndVertex()
        if round(start_vertex.X()) == round(end_vertex.X()):  # 线段垂直
            slope = float('inf')
            intercept = round(start_vertex.X())
        else:
            slope = round((end_vertex.Y() - start_vertex.Y()) / (end_vertex.X() - start_vertex.X()))
            intercept = round(start_vertex.Y() - slope * start_vertex.X())
        groups[(slope, intercept)].append(edge)
    return list(groups.values())


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
    if data is None:
        print("..........传入None，无法显示..........")
        exit()
    elif type(data) == list:
        if data == []:
            print("..........传入空值，无法显示..........")
            exit()
        else:
            data = flatten(data)
            temp = None
            for topo in data:
                if temp == None:
                    temp = topo
                else:
                    temp = temp.Merge(topo)
    else:
        temp = data

    plotly_data = Plotly.DataByTopology(temp)
    plotly_figure = Plotly.FigureByData(plotly_data)
    ofl.plot(plotly_figure)
    print("...............显示成功...............")
    print(data)


def allvertex(edges):  # 输入edge列表 返回所有顶点
    vlist = []
    for e in edges:
        v = Edge.Vertices(e)
        vlist.append(v[0])
        vlist.append(v[1])
    return vlist


def find_points_with_distance(vertices, distance=300):  # 输入点的列表，把相互之间距离为distance的点分成一组
    result = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            d = round(Vertex.Distance(vertices[i], vertices[j]))
            if d == distance:
                result.append([vertices[i], vertices[j]])
    return result


def add_short_edge(elist, distance=300):  # 输入排序好的线列表（在同一直线方向），如果线之间距离为distance，补全短线加入到原列表中
    for edges in elist:
        allv = allvertex(edges)
        allv = find_points_with_distance(allv, distance=distance)
        for vs in allv:
            shortedge = Edge.ByStartVertexEndVertex(vs[0], vs[1])
            edges.append(shortedge)
    return elist


def find_connected_edges(edges, start_edge, visited, stack):
    # 初始化当前连通分量
    connected_edges = [start_edge]
    visited.add(start_edge)
    stack.append(start_edge)

    # 遍历与 start_edge 相邻的所有边
    for edge in edges:
        if edge not in visited and round(distance_between_edges(start_edge, edge)) == 0:
            connected_edges += find_connected_edges(edges, edge, visited, stack)

    # 弹出已访问的线段，恢复之前的遍历路径
    stack.pop()

    return connected_edges


def group_edges(elist):
    result = []
    for edges in elist:
        groups = []
        visited = set()

        # 遍历所有线段，找到每个连通分量
        for edge in edges:
            if edge not in visited:
                stack = []
                connected_edges = find_connected_edges(edges, edge, visited, stack)
                groups.append(connected_edges)
        result.append(groups)
    return result


def find_extreme_vertices(vlist):
    # 使用sorted()按x坐标排序，如果相同，则按y坐标排序
    sorted_vlist = sorted(vlist, key=lambda v: (round(v.X()), round(v.Y())))

    # 找到最大和最小的两个点
    min_x = sorted_vlist[0]
    max_x = sorted_vlist[-1]

    # 如果最大和最小x坐标相同，则按y坐标排序并返回最大和最小的两个点
    if round(min_x.X()) == round(max_x.X()):
        sorted_vlist = sorted(vlist, key=lambda v: round(v.Y()))
        min_y = sorted_vlist[0]
        max_y = sorted_vlist[-1]
        return min_y, max_y

    return min_x, max_x


def newedge(groups):  # 对分组后的edge合并，寻找最两侧的点，创建新的edge
    result = []
    for group in groups:
        for edges in group:
            vlist = allvertex(edges)
            extreme_points = find_extreme_vertices(vlist)
            line = Edge.ByStartVertexEndVertex(extreme_points[0], extreme_points[1])
            result.append(line)
    return result


def group_parallel_edges(edges):
    groups = []
    for i, edge in enumerate(edges):
        parallel_group_found = False
        for group in groups:
            if Edge.IsParallel(edge, group[0]):
                group.append(edge)
                parallel_group_found = True
                break
        if not parallel_group_found:
            groups.append([edge])
    return groups


def find_lines_within_range(elist):
    result = []
    for edges in elist:
        for i in range(len(edges)):
            for j in range(i + 1, len(edges)):
                dist = round(distance_between_edges(edges[i], edges[j]))
                # print("...................................")
                # print(dist)
                if 150 <= dist <= 301:
                    result.append([edges[i], edges[j]])
    return result


def distance_between_edges(edge1, edge2):  # 等作者更新
    # 访问第一条线段的起点和终点
    start1 = (edge1.StartVertex().X(), edge1.StartVertex().Y(), edge1.StartVertex().Z())
    end1 = (edge1.EndVertex().X(), edge1.EndVertex().Y(), edge1.EndVertex().Z())
    # 访问第二条线段的起点和终点
    start2 = (edge2.StartVertex().X(), edge2.StartVertex().Y(), edge2.StartVertex().Z())
    end2 = (edge2.EndVertex().X(), edge2.EndVertex().Y(), edge2.EndVertex().Z())
    # 创建两条直线
    line1 = LineString([start1, end1])
    line2 = LineString([start2, end2])
    # 计算两条直线之间的距离
    distance = line1.distance(line2)
    return distance


def midline(elist):
    result = []
    for edges in elist:
        x1, y1, z1 = Vertex.X(Edge.StartVertex(edges[0])), Vertex.Y(Edge.StartVertex(edges[0])), Vertex.Z(
            Edge.StartVertex(edges[0]))
        x2, y2, z2 = Vertex.X(Edge.EndVertex(edges[0])), Vertex.Y(Edge.EndVertex(edges[0])), Vertex.Z(
            Edge.EndVertex(edges[0]))
        x3, y3, z3 = Vertex.X(Edge.StartVertex(edges[1])), Vertex.Y(Edge.StartVertex(edges[1])), Vertex.Z(
            Edge.StartVertex(edges[1]))
        x4, y4, z4 = Vertex.X(Edge.EndVertex(edges[1])), Vertex.Y(Edge.EndVertex(edges[1])), Vertex.Z(
            Edge.EndVertex(edges[1]))
        v1 = Vertex.ByCoordinates((x1 + x3) * 0.5, (y1 + y3) * 0.5, (z1 + z3) * 0.5)
        v2 = Vertex.ByCoordinates((x2 + x4) * 0.5, (y2 + y4) * 0.5, (z2 + z4) * 0.5)
        e = Edge.ByStartVertexEndVertex(v1, v2)
        result.append(e)
    return result


# def extend_lines(lines):
def extend_edges(edges):
    """
    Extends edges that are close enough to intersect.
    """
    for i in range(len(edges)):
        for j in range(len(edges)):     # n*n
            if i == j:
                continue
            # calculate distance between start vertices
            dist1 = round(Vertex.Distance(edges[i].StartVertex(), edges[j]))
            if 10 < dist1 <= 151:
                new_i = Edge.Extend(edges[i], distance=150, bothSides=False, reverse=True)
                edges[i] = new_i
            # calculate distance between end vertices
            dist2 = round(Vertex.Distance(edges[i].EndVertex(), edges[j]))
            if 10 < dist2 <= 151:
                new_i = Edge.Extend(edges[i], distance=150, bothSides=False, reverse=False)
                edges[i] = new_i
    return edges

def drawMidline(src):
    # src = r'D:\Desktop\Topo\data\test0825.dxf'
    dxfdata = importdxf(src)
    elist = dxflines(dxfdata)  # edge的列表
    print(len(elist))
    a = group_segments_by_direction(elist)  # 把线段按照截距和斜率相同的原则分组
    print("...............a...............")
    print(a)
    print(len(a))

    b = add_short_edge(a)  # 为分组后的子列表中补全短线
    print("...............b...............")
    print(b)
    print(len(b))

    c = group_edges(b)  # 按照彼此相邻的原则排序
    print("...............c...............")
    print(c)
    print(len(c))

    d = newedge(c)
    print("...............d...............")
    print(d)
    print(len(d))

    e = group_parallel_edges(d)
    print("...............e...............")
    print(e)
    print(len(e))

    f = find_lines_within_range(e)
    print("...............f...............")
    print(f)
    print(len(f))

    g = midline(f)
    print("...............g...............")
    print(g)
    print(len(g))

    h = extend_edges(g)
    print("...............h...............")
    print(h)
    print(len(h))

    h = Cluster.ByTopologies(h)

    return h

def drawOriginalLine(src):
    dxfdata = importdxf(src)
    elist = dxflines(dxfdata)  # edge的列表
    elist = Cluster.ByTopologies(elist)

    return elist


if __name__ == "__main__":
    # 在这里写的东西，别的包导入的时候不会被自动执行
    dxfdata = importdxf()
    elist = dxflines(dxfdata)  # edge的列表
    print(len(elist))

    a = group_segments_by_direction(elist)  # 把线段按照截距和斜率相同的原则分组
    print("...............a...............")
    print(a)
    print(len(a))

    b = add_short_edge(a)  # 为分组后的子列表中补全短线
    print("...............b...............")
    print(b)
    print(len(b))

    c = group_edges(b)  # 按照彼此相邻的原则排序
    print("...............c...............")
    print(c)
    print(len(c))

    d = newedge(c)
    print("...............d...............")
    print(d)
    print(len(d))

    e = group_parallel_edges(d)
    print("...............e...............")
    print(e)
    print(len(e))

    f = find_lines_within_range(e)
    print("...............f...............")
    print(f)
    print(len(f))

    g = midline(f)
    print("...............g...............")
    print(g)
    print(len(g))

    h = extend_edges(g)
    print("...............h...............")
    print(h)
    print(len(h))


    showdata(h)

# plotly_data = Plotly.DataByTopology(n)
# plotly_figure = Plotly.FigureByData(plotly_data)
# ofl.plot(plotly_figure)
