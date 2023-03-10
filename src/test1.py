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

v1 = Vertex.ByCoordinates(0, 0, 0)
v2 = Vertex.ByCoordinates(1, 0, 0)
v3 = Vertex.ByCoordinates(0, 1, 0)
v4 = Vertex.ByCoordinates(1, -1, 0)


e1 = Edge.ByStartVertexEndVertex(v1, v2)
e2 = Edge.ByStartVertexEndVertex(v3, v4)

a = Edge.Intersect2D(e1,e2)

print(a)
# v3 = Vertex.ByCoordinates(3, 1, 0)
# d = Vertex.Distance(v3,e)

# d = Edge.ByVertices([v1, v2, v3, v4])



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

# showdata(c)












def split_edges(edges):
    result = []
    for i in range(len(edges)):
        e1 = edges[i]
        intersections = []
        start_intersects = False
        end_intersects = False
        for j in range(len(edges)):
            if i == j:
                continue
            e2 = edges[j]
            intersection = Edge.Intersect2D(e1,e2)
            if intersection is not None:
                intersections.append(intersection)
                if intersection == e1.StartVertex() or intersection == e1.EndVertex():
                    start_intersects = True
                if intersection == e2.StartVertex() or intersection == e2.EndVertex():
                    end_intersects = True
        if intersections:
            intersections.sort(key=lambda v: (v.X(), v.Y(), v.Z()))
            start_vertex = e1.StartVertex()
            for intersection in intersections:
                result.append(Edge.ByStartVertexEndVertex(start_vertex, intersection))
                start_vertex = intersection
            result.append(Edge.ByStartVertexEndVertex(start_vertex, e1.EndVertex()))
        elif start_intersects and end_intersects
            result.append(e1)
    return result
