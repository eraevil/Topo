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

src = r'D:\Desktop\Topo\data\test0308.dxf'


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


def allvertex(edges):  # 输入edge列表 返回所有顶点
    vlist = []
    for e in edges:
        v = Edge.Vertices(e)
        vlist.append(v[0])
        vlist.append(v[1])
    return vlist


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


def split_edges(edges):
    result = []
    for i in range(len(edges)):
        e1 = edges[i]
        intersections = []
        for j in range(i, len(edges)):
            if i == j:
                continue
            e2 = edges[j]
            intersection = Edge.Intersect2D(e1, e2)
            if intersection is not None:
                intersections.append(intersection)
        if intersections:
            intersections.sort(key=lambda v: (v.X(), v.Y(), v.Z()))
            start_vertex = e1.StartVertex()
            for intersection in intersections:
                edgetemp = Edge.ByStartVertexEndVertex(start_vertex, intersection)
                if edgetemp:
                    result.append(edgetemp)
                start_vertex = intersection
            edgetemp = Edge.ByStartVertexEndVertex(start_vertex, e1.EndVertex())
            if edgetemp:
                result.append(edgetemp)
        else:
            result.append(e1)
    return result


def is_same_point(v1, v2):
    if round(v1.X()) == round(v2.X()) and round(v1.Y()) == round(v2.Y()) and round(v1.Z()) == round(v2.Z()):
        return True
    else:
        return False


def remove_all_edges_with_isolated_vertices(edges):
    while True:
        new_edges = []
        for edge in edges:
            start = Edge.StartVertex(edge)
            end = Edge.EndVertex(edge)
            start_isolated = True
            end_isolated = True
            for other_edge in edges:
                if other_edge == edge:
                    continue
                other_start = Edge.StartVertex(other_edge)
                other_end = Edge.EndVertex(other_edge)
                if is_same_point(start, other_start) or is_same_point(start, other_end):
                    start_isolated = False
                if is_same_point(end, other_start) or is_same_point(end, other_end):
                    end_isolated = False
                if not start_isolated and not end_isolated:
                    break
            if not start_isolated and not end_isolated:
                new_edges.append(edge)
        if len(new_edges) == len(edges):
            break
        edges = new_edges
    return edges
# 传github去


dxfdata = importdxf(src)
elist = dxflines(dxfdata)  # edge的列表

a = group_segments_by_direction(elist)  # 把线段按照截距和斜率相同的原则分组
print("...............a...............")
print(a)
print(len(a))

b = group_edges(a)  # 按照彼此相邻的原则排序
print("...............b...............")
print(b)
print(len(b))

c = newedge(b)  # 重构图形,去除线上多点
print("...............c...............")
print(c)
print(len(c))

d = split_edges(c)  # 重构图形,在交点处断开,每条线段都是最小线段
print("...............d...............")
print(d)
print(len(d))

e = remove_all_edges_with_isolated_vertices(d)
print(e)


showdata(d)
