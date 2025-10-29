import sys
import math
import heapq
from typing import Dict, List, Optional, Tuple, Set, Generator, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QRadioButton, QGroupBox, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QFileDialog, QMessageBox, QStatusBar, QGraphicsItem
)
from PyQt5.QtGui import QColor, QPen, QBrush, QFont, QPainter
from PyQt5.QtCore import Qt, QRectF

class Node:
    def __init__(self, node_id: int, x: int, y: int):
        self.id: int = node_id
        self.x: int = x
        self.y: int = y
        self.neighbors: List['Node'] = []
        self.g: float = float('inf')
        self.h: float = 0.0
        self.f: float = float('inf')
        self.parent: Optional['Node'] = None
    
    def __lt__(self, other: 'Node') -> bool:
        return self.f < other.f
    
    def reset(self):
        self.g = float('inf')
        self.h = 0.0
        self.f = float('inf')
        self.parent = None

class Graph:
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
    
    def load_from_file(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            self.nodes.clear()
            n = int(lines[0].strip())
            
            if n == 0:
                return True

            for i in range(1, n + 1):
                x, y = map(int, lines[i].strip().split())
                self.nodes[i] = Node(i, x, y)
                
            neighbor_data = {}
            for i in range(n + 1, 2 * n + 1):
                parts = list(map(int, lines[i].strip().split()))
                node_id = i - n
                neighbor_data[node_id] = parts[1:]
            
            for node_id, neighbor_ids in neighbor_data.items():
                node = self.nodes[node_id]
                for neighbor_id in neighbor_ids:
                    if neighbor_id in self.nodes:
                        node.neighbors.append(self.nodes[neighbor_id])
                    else:
                        print(f"Ostrzeżenie: Węzeł {node_id} ma nieistniejącego sąsiada {neighbor_id}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Błąd wczytywania pliku", f"Nie można wczytać grafu:\n{e}")
            self.nodes.clear()
            return False

class MainWindow(QMainWindow):
    
    COLOR_DEFAULT = QColor("lightblue")
    COLOR_OPEN = QColor("orange")
    COLOR_CLOSED = QColor("lightgray")
    COLOR_CURRENT = QColor("yellow")
    COLOR_START = QColor("green")
    COLOR_GOAL = QColor("red")
    COLOR_PATH = QColor("purple")
    COLOR_EDGE = QColor("gray")
    COLOR_EDGE_PATH = QColor("purple")
    
    PEN_WIDTH_EDGE = 2.0
    PEN_WIDTH_NODE = 1.5
    PEN_WIDTH_PATH = 4.0
    
    NODE_RADIUS_SCENE = 0.3
    FONT_SCALE_SCENE = 0.03
    CANVAS_PADDING = 5

    def __init__(self):
        super().__init__()
        self.graph = Graph()
        self.search_generator: Optional[Generator[Dict[str, Any], None, None]] = None
        self.scene_items: Dict[int | Tuple[int, int], Dict[str, QGraphicsItem]] = {}

        self.pen_edge = QPen(self.COLOR_EDGE, self.PEN_WIDTH_EDGE)
        self.pen_edge.setCosmetic(True)
        
        self.pen_node = QPen(Qt.black, self.PEN_WIDTH_NODE)
        self.pen_node.setCosmetic(True)
        
        self.pen_path = QPen(self.COLOR_EDGE_PATH, self.PEN_WIDTH_PATH)
        self.pen_path.setCosmetic(True)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Wizualizator Wyszukiwania Ścieżki (PyQt5)")
        self.setGeometry(100, 100, 1000, 800)
        
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)

        load_box = QGroupBox("1. Graf")
        load_layout = QHBoxLayout()
        self.btn_load = QPushButton("Wczytaj graf...")
        self.btn_load.clicked.connect(self.load_graph)
        self.lbl_filename = QLabel("Nie wczytano pliku.")
        load_layout.addWidget(self.btn_load)
        load_layout.addWidget(self.lbl_filename)
        load_box.setLayout(load_layout)
        control_layout.addWidget(load_box)

        select_box = QGroupBox("2. Węzły")
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Start:"))
        self.cmb_start_node = QComboBox()
        select_layout.addWidget(self.cmb_start_node)
        select_layout.addWidget(QLabel("Cel:"))
        self.cmb_goal_node = QComboBox()
        select_layout.addWidget(self.cmb_goal_node)
        select_box.setLayout(select_layout)
        control_layout.addWidget(select_box)

        algo_box = QGroupBox("3. Algorytm")
        algo_layout = QVBoxLayout()
        self.algo_a_star = QRadioButton("A* (f=g+h)")
        self.algo_gbfs = QRadioButton("Zachłanny BFS (f=h)")
        self.algo_a_star.setChecked(True)
        algo_layout.addWidget(self.algo_a_star)
        algo_layout.addWidget(self.algo_gbfs)
        algo_box.setLayout(algo_layout)
        control_layout.addWidget(algo_box)

        run_box = QGroupBox("4. Sterowanie")
        run_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_search)
        run_layout.addWidget(self.btn_start)
        self.btn_next_step = QPushButton("Następny krok")
        self.btn_next_step.clicked.connect(self.next_step)
        run_layout.addWidget(self.btn_next_step)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_visualization)
        run_layout.addWidget(self.btn_reset)
        run_box.setLayout(run_layout)
        control_layout.addWidget(run_box)
        control_layout.addStretch(1)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(Qt.white))
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        main_layout.addWidget(self.view)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.lbl_status = QLabel("Wczytaj graf, aby rozpocząć.")
        self.lbl_cost = QLabel("Koszt ścieżki: N/A")
        self.statusBar.addWidget(self.lbl_status, 1)
        self.statusBar.addPermanentWidget(self.lbl_cost)
        
        self._set_controls_state(False)
        self.btn_load.setEnabled(True)

    def load_graph(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Wybierz plik grafu", "", "Pliki tekstowe (*.txt);;Wszystkie pliki (*.*)")
        if not filepath:
            return

        self.reset_visualization(full_reset=True)

        if self.graph.load_from_file(filepath):
            self.lbl_filename.setText(filepath.split('/')[-1])
            self.draw_graph()
            
            node_ids = sorted(self.graph.nodes.keys())
            str_node_ids = [str(nid) for nid in node_ids]
            self.cmb_start_node.addItems(str_node_ids)
            self.cmb_goal_node.addItems(str_node_ids)
            
            if node_ids:
                self.cmb_start_node.setCurrentIndex(0)
                self.cmb_goal_node.setCurrentIndex(len(node_ids) - 1)
                self._set_controls_state(True)
                self.lbl_status.setText("Graf wczytany.")

                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.view.scale(1, -1)
                self.lbl_status.setText("Wczytano pusty graf. Wczytaj inny plik.")

    def draw_graph(self):
        self.scene.clear()
        self.scene_items.clear()
        if not self.graph.nodes: return

        nodes = self.graph.nodes.values()
        min_x = min(n.x for n in nodes)
        max_x = max(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        max_y = max(n.y for n in nodes)
        
        graph_width = max(max_x - min_x, 1)
        graph_height = max(max_y - min_y, 1)

        scene_rect = QRectF(
            min_x - self.CANVAS_PADDING, min_y - self.CANVAS_PADDING, 
            graph_width + 2 * self.CANVAS_PADDING, 
            graph_height + 2 * self.CANVAS_PADDING
        )
        self.scene.setSceneRect(scene_rect)
        
        drawn_edges = set()
        for node in self.graph.nodes.values():
            for neighbor in node.neighbors:
                edge_key = tuple(sorted((node.id, neighbor.id)))
                if edge_key not in drawn_edges:
                    line = self.scene.addLine(node.x, node.y, neighbor.x, neighbor.y, self.pen_edge)
                    line.setZValue(-1)
                    self.scene_items[edge_key] = {'line': line}
                    drawn_edges.add(edge_key)

        r = self.NODE_RADIUS_SCENE
        
        for node_id, node in self.graph.nodes.items():
            oval = self.scene.addEllipse(node.x - r, node.y - r, r * 2, r * 2, 
                                          self.pen_node, QBrush(self.COLOR_DEFAULT))
            
            text = QGraphicsTextItem(str(node_id))
            text.setFont(QFont("Arial", 10))
            
            scale = self.FONT_SCALE_SCENE
            text.setTransform(text.transform().scale(scale, -scale))
            
            text_rect = text.boundingRect()
            text.setPos(
                node.x - (text_rect.width() * scale) / 2,
                node.y + (text_rect.height() * scale) / 2
            )
            
            self.scene.addItem(text)
            self.scene_items[node_id] = {'oval': oval, 'text': text}

    def start_search(self):
        start_text = self.cmb_start_node.currentText()
        goal_text = self.cmb_goal_node.currentText()
        
        if not start_text or not goal_text:
            QMessageBox.warning(self, "Błąd", "Nie wybrano węzła startowego lub docelowego.\nUpewnij się, że graf jest poprawnie wczytany.")
            return

        start_id = int(start_text)
        goal_id = int(goal_text)
        
        if start_id == goal_id:
            QMessageBox.warning(self, "Błąd", "Węzeł startowy i docelowy muszą być różne.")
            return

        self.reset_visualization(full_reset=False)
        algo_type = "A*" if self.algo_a_star.isChecked() else "GBFS"
        
        self._color_node(start_id, self.COLOR_START)
        self._color_node(goal_id, self.COLOR_GOAL)
        
        self._set_controls_state(False)
        self.btn_next_step.setEnabled(True)
        
        self.search_generator = self.search_algorithm(self.graph.nodes[start_id], self.graph.nodes[goal_id], algo_type)
        self.lbl_status.setText(f"Rozpoczynanie {algo_type}. Kliknij 'Następny krok'.")
        self.lbl_cost.setText("Koszt ścieżki: N/A")
        self.next_step()

    def next_step(self):
        if not self.search_generator: return
        try:
            state = next(self.search_generator)
            self.update_visualization(state)
        except StopIteration:
            self._end_search()

    def update_visualization(self, state: Dict[str, Any]):
        start_id = int(self.cmb_start_node.currentText())
        goal_id = int(self.cmb_goal_node.currentText())

        for node in state.get('open', []):
            if node.id not in [start_id, goal_id]: self._color_node(node.id, self.COLOR_OPEN)
        for node in state.get('closed', []):
            if node.id not in [start_id, goal_id]: self._color_node(node.id, self.COLOR_CLOSED)
                
        current = state.get('current')
        if current and current.id not in [start_id, goal_id]:
            self._color_node(current.id, self.COLOR_CURRENT)
            self.lbl_status.setText(f"Przetwarzanie węzła {current.id}...")

        if state.get('path_found', False):
            path = state.get('path', [])
            cost = state.get('cost', 0.0)
            self.lbl_status.setText(f"Znaleziono ścieżkę! Długość: {len(path)} węzłów.")
            self.lbl_cost.setText(f"Koszt ścieżki: {cost:.4f}")
            self._draw_path(path)
            self._end_search()
        elif state.get('no_path', False):
            self.lbl_status.setText("Nie znaleziono ścieżki.")
            self._end_search()
            
    def reset_visualization(self, full_reset: bool = True):
        self.search_generator = None
        if full_reset:
            self.scene.clear()
            self.scene_items.clear()
            self.graph = Graph()
            self.cmb_start_node.clear()
            self.cmb_goal_node.clear()
            self._set_controls_state(False)
            self.btn_load.setEnabled(True)
            self.lbl_filename.setText("Nie wczytano pliku.")
            self.lbl_status.setText("Wczytaj graf.")
            self.view.resetTransform()
        else:
            for item_key, item_dict in self.scene_items.items():
                if isinstance(item_key, int): 
                    self._color_node(item_key, self.COLOR_DEFAULT)
                elif isinstance(item_key, tuple) and 'line' in item_dict:
                    item_dict['line'].setPen(self.pen_edge)
            
            start_text = self.cmb_start_node.currentText()
            goal_text = self.cmb_goal_node.currentText()
            if start_text: self._color_node(int(start_text), self.COLOR_START)
            if goal_text: self._color_node(int(goal_text), self.COLOR_GOAL)

            self._set_controls_state(True)
            self.lbl_status.setText("Gotowy do nowego wyszukiwania.")

        self.lbl_cost.setText("Koszt ścieżki: N/A")

    def _set_controls_state(self, enabled: bool):
        self.btn_load.setEnabled(enabled)
        self.cmb_start_node.setEnabled(enabled)
        self.cmb_goal_node.setEnabled(enabled)
        self.algo_a_star.setEnabled(enabled)
        self.algo_gbfs.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        self.btn_next_step.setEnabled(False)
        
    def _end_search(self):
        self.search_generator = None
        self._set_controls_state(True)
        self.btn_next_step.setEnabled(False)

    def _color_node(self, node_id: int, color: QColor):
        if node_id in self.scene_items:
            self.scene_items[node_id]['oval'].setBrush(QBrush(color))

    def _draw_path(self, path: List[Node]):
        if len(path) < 2: return
        
        for i in range(len(path) - 1):
            if i > 0: self._color_node(path[i].id, self.COLOR_PATH)
            edge_key = tuple(sorted((path[i].id, path[i+1].id)))
            if edge_key in self.scene_items:
                self.scene_items[edge_key]['line'].setPen(self.pen_path)
                self.scene_items[edge_key]['line'].setZValue(0)
        self._color_node(path[0].id, self.COLOR_START)
        self._color_node(path[-1].id, self.COLOR_GOAL)

    @staticmethod
    def _calculate_distance(node1: Node, node2: Node) -> float:
        return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    @staticmethod
    def _reconstruct_path(current: Node) -> List[Node]:
        path = []
        while current:
            path.append(current)
            current = current.parent
        return path[::-1]

    def search_algorithm(self, start_node: Node, goal_node: Node, algorithm_type: str) -> Generator[Dict[str, Any], None, None]:
        for node in self.graph.nodes.values(): node.reset()

        open_set: List[Tuple[float, int, Node]] = []
        open_set_lookup: Set[Node] = set()
        closed_set: Set[Node] = set()
        
        start_node.g = 0.0
        start_node.h = self.calculate_distance(start_node, goal_node)
        start_node.f = start_node.h if algorithm_type == "GBFS" else (start_node.g + start_node.h)
        
        heapq.heappush(open_set, (start_node.f, start_node.id, start_node))
        open_set_lookup.add(start_node)
        
        yield {"open": list(open_set_lookup), "closed": set(closed_set), "current": None}

        while open_set:
            f_cost, _, current_node = heapq.heappop(open_set)
            open_set_lookup.remove(current_node)
            
            if current_node in closed_set: continue
            closed_set.add(current_node)

            yield {"open": list(open_set_lookup), "closed": set(closed_set), "current": current_node}

            if current_node == goal_node:
                path = self._reconstruct_path(current_node)
                yield {"path_found": True, "path": path, "cost": goal_node.g, "open": list(open_set_lookup), "closed": set(closed_set)}
                return

            for neighbor in current_node.neighbors:
                if neighbor in closed_set: continue
                
                tentative_g_score = current_node.g + self.calculate_distance(current_node, neighbor)
                
                if tentative_g_score < neighbor.g:
                    neighbor.parent = current_node
                    neighbor.g = tentative_g_score
                    neighbor.h = self.calculate_distance(neighbor, goal_node)
                    neighbor.f = neighbor.h if algorithm_type == "GBFS" else (neighbor.g + neighbor.h)
                    
                    if neighbor not in open_set_lookup:
                        heapq.heappush(open_set, (neighbor.f, neighbor.id, neighbor))
                        open_set_lookup.add(neighbor)
        
        yield {"no_path": True}
        return

    @classmethod
    def calculate_distance(cls, node1, node2):
        return cls._calculate_distance(node1, node2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())