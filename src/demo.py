import sys
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from topologicpy.Plotly import Plotly
from topologicpy.Vertex import Vertex
from topologicpy.Edge import Edge
import plotly.offline as ofl
import plotly.graph_objs as go
from topologicpy.Wire import Wire
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




class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Topologicpy Demo")
        # Create UI elements
        self.select_button = QPushButton("Select file")
        self.plot_button = QPushButton("Plot")
        self.graph_widget = QWebEngineView()
        self.setGeometry(800, 500, 1700, 1100)

        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.plot_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.graph_widget)

        self.setLayout(main_layout)

        # Connect signals and slots
        self.select_button.clicked.connect(self.select_file)
        self.plot_button.clicked.connect(self.plot_graph)

        self.data = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "Excel files (*.xlsx);;All files (*.*)")
        if file_path:
            self.data = pd.read_excel(file_path, header=0)

    def plot_graph(self):
        if self.data is not None:
            r = None

            for index, row in self.data.iterrows():
                x1, y1, z1, x2, y2, z2 = row.SX, row.SY, row.SZ, row.EX, row.EY, row.EZ
                p1 = Vertex.ByCoordinates(x1, y1, z1)
                p2 = Vertex.ByCoordinates(x2, y2, z2)
                e = Edge.ByVertices([p1, p2])

                if r is None:
                    r = e
                else:
                    r = r.Merge(e)

            plotly_data = Plotly.DataByTopology(r)
            plotly_figure = Plotly.FigureByData(plotly_data,width=1600, height=1000)

            fig = go.Figure(data=plotly_figure)

            # Render the graph
            html = ofl.plot(fig, include_plotlyjs='cdn', output_type='div')
            self.graph_widget.setHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())