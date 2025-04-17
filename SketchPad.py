import sys
from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem, QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QToolBar, QColorDialog, QGraphicsItem
from PySide6.QtGui import QPen, QPolygonF, QAction
from PySide6.QtCore import QEvent, Qt


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setSceneRect(0, 0, 1012, 756)

        self.current_color = Qt.black
        self.current_mode = 'freehand'

        self.temp_item = None
        self.selected_item = None
        self.clipboard_item = None

        self.start_point = None
        self.select_point = None
        self.target_point = None
        self.offset_point = None
        self.polygon_points = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = self.mapToScene(event.pos())

            if self.current_mode == 'select':
                self.select_point = self.mapToScene(event.pos())
                items = self.scene().items(self.start_point)
                if items:
                    self.selected_item = items[0]
                    self.selected_item.setFlag(QGraphicsItem.ItemIsMovable, True)
                else:
                    self.selected_item = None

            else:
                if self.selected_item:
                    self.selected_item.setFlag(QGraphicsItem.ItemIsMovable, False)
                    self.selected_item = None

            if self.current_mode == 'target':
                self.target_point = self.mapToScene(event.pos())

            elif self.current_mode == 'polygon':
                current_point = self.mapToScene(event.pos())
                if not self.polygon_points:
                    self.polygon_points.append(current_point)

                else:
                    # Check if clicked close to the starting point or if it's a double-click
                    new_poly_point = self.offset_point
                    if (current_point - self.polygon_points[0]).manhattanLength() < 20 or event.type() == QEvent.MouseButtonDblClick:
                        self.polygon_points.append(new_poly_point)
                        self.polygon_points.append(self.polygon_points[0])
                        self.scene().addPolygon(QPolygonF(self.polygon_points), QPen(self.current_color))
                        self.polygon_points.clear()

                    else:
                        self.polygon_points.append(new_poly_point)

    def mouseMoveEvent(self, event):
        if self.start_point:
            current_point = self.mapToScene(event.pos())

            if self.current_mode == 'freehand':
                self.scene().addLine(self.start_point.x(), self.start_point.y(), current_point.x(), current_point.y(),
                                     QPen(self.current_color))
                self.start_point = current_point

            elif self.current_mode in ['line', 'rectangle', 'square', 'ellipse', 'circle', 'polygon']:
                if self.temp_item:
                    self.scene().removeItem(self.temp_item)

                if self.current_mode == 'line':
                    self.temp_item = self.scene().addLine(self.start_point.x(), self.start_point.y(), current_point.x(), current_point.y(), QPen(self.current_color))

                elif self.current_mode == 'rectangle':
                    x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                    x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                    self.temp_item = self.scene().addRect(x1, y1, x2 - x1, y2 - y1, QPen(self.current_color))

                elif self.current_mode == 'square':
                    x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                    x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                    side = max(x2 - x1, y2 - y1)
                    self.temp_item = self.scene().addRect(x1, y1, side, side, QPen(self.current_color))

                elif self.current_mode == 'ellipse':
                    x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                    x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                    self.temp_item = self.scene().addEllipse(x1, y1, x2 - x1, y2 - y1, QPen(self.current_color))

                elif self.current_mode == 'circle':
                    x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                    x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                    side = max(x2 - x1, y2 - y1)
                    self.temp_item = self.scene().addEllipse(x1, y1, side, side, QPen(self.current_color))

                elif self.current_mode == 'polygon' and self.polygon_points:
                    temp_points = self.polygon_points + [current_point]
                    self.temp_item = self.scene().addPolygon(QPolygonF(temp_points), QPen(self.current_color))

    def mouseReleaseEvent(self, event):
        if self.current_mode in ['line', 'rectangle', 'square', 'ellipse', 'circle', 'polygon']:
            current_point = self.mapToScene(event.pos())
            self.offset_point = current_point

            if self.temp_item:
                self.scene().removeItem(self.temp_item)
                self.temp_item = None

            if self.current_mode == 'line':
                self.scene().addLine(self.start_point.x(), self.start_point.y(), current_point.x(), current_point.y(), QPen(self.current_color))

            elif self.current_mode == 'rectangle':
                x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                self.scene().addRect(x1, y1, x2 - x1, y2 - y1, QPen(self.current_color))

            elif self.current_mode == 'square':
                x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                side = max(x2 - x1, y2 - y1)
                self.scene().addRect(x1, y1, side, side, QPen(self.current_color))

            elif self.current_mode == 'ellipse':
                x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                self.scene().addEllipse(x1, y1, x2 - x1, y2 - y1, QPen(self.current_color))

            elif self.current_mode == 'circle':
                x1, y1 = min(self.start_point.x(), current_point.x()), min(self.start_point.y(), current_point.y())
                x2, y2 = max(self.start_point.x(), current_point.x()), max(self.start_point.y(), current_point.y())
                side = max(x2 - x1, y2 - y1)
                self.scene().addEllipse(x1, y1, side, side, QPen(self.current_color))

            elif self.current_mode == 'polygon' and self.polygon_points:
                temp_points = self.polygon_points + [current_point]
                self.temp_item = self.scene().addPolygon(QPolygonF(temp_points), QPen(self.current_color))

        self.start_point = None

    def copyItem(self):
        if self.selected_item:
            self.current_mode = 'target'
            print(str(self.current_mode))
            self.clipboard_item = self.selected_item
            self.selected_item = None

    def cutItem(self):
        if self.selected_item:
            self.current_mode = 'target'
            print(str(self.current_mode))
            self.scene().removeItem(self.selected_item)
            self.clipboard_item = self.selected_item
            self.selected_item = None

    def cloneItem(self, item):
        if isinstance(item, QGraphicsRectItem):
            return QGraphicsRectItem(item.rect())

        elif isinstance(item, QGraphicsLineItem):
            return QGraphicsLineItem(item.line())

        elif isinstance(item, QGraphicsEllipseItem):
            return QGraphicsEllipseItem(item.rect())

        elif isinstance(item, QGraphicsPolygonItem):
            return QGraphicsPolygonItem(item.polygon())

        return None

    def pasteItem(self):
        if self.clipboard_item:
            item_copy = self.cloneItem(self.clipboard_item)
            self.scene().addItem(item_copy)
            item_copy.setPos(self.target_point - self.select_point)
            self.selected_item = item_copy


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowTitle('SketchPad')

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFixedSize(1024, 768)
        self.setCentralWidget(self.view)

        self.initToolbar()

    def initToolbar(self):
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)

        freehand_action = QAction('Freehand', self)
        freehand_action.triggered.connect(lambda: self.setMode('freehand'))
        self.toolbar.addAction(freehand_action)

        line_action = QAction('Line', self)
        line_action.triggered.connect(lambda: self.setMode('line'))
        self.toolbar.addAction(line_action)

        rectangle_action = QAction('Rectangle', self)
        rectangle_action.triggered.connect(lambda: self.setMode('rectangle'))
        self.toolbar.addAction(rectangle_action)

        square_action = QAction('Square', self)
        square_action.triggered.connect(lambda: self.setMode('square'))
        self.toolbar.addAction(square_action)

        ellipse_action = QAction('Ellipse', self)
        ellipse_action.triggered.connect(lambda: self.setMode('ellipse'))
        self.toolbar.addAction(ellipse_action)

        circle_action = QAction('Circle', self)
        circle_action.triggered.connect(lambda: self.setMode('circle'))
        self.toolbar.addAction(circle_action)

        polygon_action = QAction('Polygon', self)
        polygon_action.triggered.connect(lambda: self.setMode('polygon'))
        self.toolbar.addAction(polygon_action)

        select_action = QAction('Select', self)
        select_action.triggered.connect(lambda: self.setMode('select'))
        self.toolbar.addAction(select_action)

        copy_action = QAction('Copy', self)
        copy_action.triggered.connect(self.view.copyItem)
        self.toolbar.addAction(copy_action)

        cut_action = QAction('Cut', self)
        cut_action.triggered.connect(self.view.cutItem)
        self.toolbar.addAction(cut_action)

        paste_action = QAction('Paste', self)
        paste_action.triggered.connect(self.view.pasteItem)
        self.toolbar.addAction(paste_action)

        color_action = QAction('Choose Color', self)
        color_action.triggered.connect(self.chooseColor)
        self.toolbar.addAction(color_action)

    def setMode(self, mode):
        self.view.current_mode = mode
        print(str(self.view.current_mode))

    def chooseColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.view.current_color = color


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())
