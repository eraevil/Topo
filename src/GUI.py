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


from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
import midline
from PyQt5.QtWidgets import QMessageBox



class MainWindow(QWidget):
    filepath = ""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Topologicpy Demo")
        # Create UI elements
        self.select_button = QPushButton("选择文件")
        self.plot_button = QPushButton("绘制导入图形")
        self.midline_button = QPushButton("绘制中线")
        self.graph_widget = QWebEngineView()
        self.setGeometry(400, 200, 1700, 1100)

        # Create layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.plot_button)
        button_layout.addWidget(self.midline_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.graph_widget)

        self.setLayout(main_layout)

        # Connect signals and slots
        self.select_button.clicked.connect(self.select_file)
        self.plot_button.clicked.connect(self.drawOriginalLine)
        self.midline_button.clicked.connect(self.drawMidline)

        self.data = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "DXF files (*.dxf)")
        # if file_path:
        #     self.data = pd.read_excel(file_path, header=0)
        # print(file_path)
        self.filepath = file_path

    def msgWarning(self,text):
        msg = QMessageBox()
        msg.setWindowTitle("警告")
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


    def drawOriginalLine(self):
        print(self.filepath)
        if self.filepath != "":
            elist = midline.drawOriginalLine(self.filepath)
            plotly_data = Plotly.DataByTopology(elist)
            plotly_figure = Plotly.FigureByData(plotly_data, width=1600, height=1000)

            fig = go.Figure(data=plotly_figure)

            # Render the graph
            html = ofl.plot(fig, include_plotlyjs='cdn', output_type='div')
            self.graph_widget.setHtml(html)
        else:
            self.msgWarning("请选择一个DXF文件！")



    def drawMidline(self):
        print(self.filepath)
        if self.filepath != "":
            h = midline.drawMidline(self.filepath)

            plotly_data = Plotly.DataByTopology(h)
            plotly_figure = Plotly.FigureByData(plotly_data, width=1600, height=1000)

            fig = go.Figure(data=plotly_figure)
            # Render the graph
            html = ofl.plot(fig, include_plotlyjs='cdn', output_type='div')
            self.graph_widget.setHtml(html)
        else:
            self.msgWarning("请选择一个DXF文件！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())