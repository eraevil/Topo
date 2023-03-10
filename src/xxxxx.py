import plotly.offline as ofl
import plotly.graph_objs as go
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
import plotly.graph_objs as go

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import sys

def openxxx():
    from topologicpy.Plotly import Plotly
    from topologicpy.Vertex import Vertex
    from topologicpy.Edge import Edge
    import plotly.offline as ofl
    import pandas as pd
    from topologicpy.Wire import Wire

    data = pd.read_excel(r'D:\Desktop\Topo\data\11.xlsx', header=0)
    print(data)

    r = None

    for index, row in data.iterrows():  # 遍历线的数据集
        x1, y1, z1, x2, y2, z2 = row.SX, row.SY, row.SZ, row.EX, row.EY, row.EZ
        p1 = Vertex.ByCoordinates(x1, y1, z1)
        p2 = Vertex.ByCoordinates(x2, y2, z2)
        e = Edge.ByVertices([p1, p2])

        if r == None:
            r = e
        else:
            r = r.Merge(e)

    plotly_data = Plotly.DataByTopology(r)
    plotly_figure = Plotly.FigureByData(plotly_data)
    print(plotly_figure)
    fig = go.Figure(data = plotly_figure)
    # return fig.to_html(include_plotlyjs='cdn')

    return plotly_figure

class PlotlyWidget(QWidget):
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.setGeometry(100, 100, 800, 600)
        self.graphWidget = QWebEngineView(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.graphWidget)
        self._render()

    def _render(self):
        html = ofl.plot(self.figure, include_plotlyjs='cdn', output_type='div')
        self.graphWidget.setHtml(html)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        ...

        # 添加菜单栏和文件选择器
        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.triggered.connect(self.showFileDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.show()

    def showFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select file", "",
                                                  "Excel Files (*.xlsx);;All Files (*)", options=options)
        if fileName:
            figure = openxxx(fileName)
            widget = PlotlyWidget(figure)
            widget.show()


if __name__ == "__main__":




    app = QApplication(sys.argv)
    figure = openxxx()

    # figure = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
    print(figure)
    widget = PlotlyWidget(figure)
    widget.show()
    sys.exit(app.exec_())