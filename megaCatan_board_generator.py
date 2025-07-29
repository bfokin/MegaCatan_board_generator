import sys

# ====== Graphical library imports ==============================================
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QSlider, QLabel, QLineEdit, QPushButton, QSplitter)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# ====== Imports from local files  ==============================================
from globals import LAND_RESOURCES, LAND_RESOURCE_RATIOS
from landscape import HexagonGridWidget

# ====== MainWindow(QMainWindow)   ==============================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MegaCatan Hexagon Grid Generator")
        self._is_updating_fields = False
        
        self.hexagon_grid = HexagonGridWidget()
        controls_widget = QWidget()
        controls_layout = QGridLayout(controls_widget)
        
        # Resourse imput
        self.resource_edits = {}
        for i, resource in enumerate(LAND_RESOURCES):
            self.resource_edits[resource] = QLineEdit()
            self.resource_edits[resource].textChanged.connect(lambda text, res=resource: self.update_resource_ratios(res))
            controls_layout.addWidget(QLabel(f"{resource.title()}:"), i, 0)
            controls_layout.addWidget(self.resource_edits[resource], i, 1)

        # gets from globals.py
        current_row = len(LAND_RESOURCES)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 100)
        self.size_edit = QLineEdit()
        self.size_edit.setFixedWidth(50)
        controls_layout.addWidget(QLabel("Hex Size:"), current_row, 0)
        controls_layout.addWidget(self.size_slider, current_row, 1)
        controls_layout.addWidget(self.size_edit, current_row, 2)
        current_row += 1

        self.generate_button = QPushButton("Generate Board")
        controls_layout.addWidget(self.generate_button, current_row, 0, 1, 3)
        current_row += 1

        self.grid_dims_label = QLabel()
        self.grid_dims_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        controls_layout.addWidget(self.grid_dims_label, current_row, 0, 1, 3, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        current_row += 1

        controls_layout.setRowStretch(current_row, 1)
        controls_layout.setColumnStretch(3, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.hexagon_grid)
        splitter.addWidget(controls_widget)
        splitter.setSizes([800, 350]) 
        self.setCentralWidget(splitter)
        
        self.generate_button.clicked.connect(self.handle_generate_button)
        self.size_slider.valueChanged.connect(self.update_hex_size_from_slider)
        self.size_edit.editingFinished.connect(self.update_from_text_hex_size)

        self.size_slider.setValue(self.hexagon_grid.hex_size)
        self.size_edit.setText(str(self.hexagon_grid.hex_size))
        self.resource_edits["desert"].setText("1")
        self.handle_generate_button()

    def update_resource_ratios(self, changed_resource):
        if self._is_updating_fields: return
        self._is_updating_fields = True
        sender_edit = self.resource_edits[changed_resource]
        try: new_value = int(sender_edit.text())
        except (ValueError, TypeError):
            self._is_updating_fields = False
            return
        base_ratio = LAND_RESOURCE_RATIOS.get(changed_resource)
        if base_ratio is None or base_ratio == 0:
            self._is_updating_fields = False
            return
        new_desert_count = round(new_value / base_ratio)
        for resource, edit_widget in self.resource_edits.items():
            if resource != changed_resource:
                ratio = LAND_RESOURCE_RATIOS[resource]
                edit_widget.setText(str(round(new_desert_count * ratio)))
        self._is_updating_fields = False

    def handle_generate_button(self):
        resource_counts = {res: int(edit.text()) if edit.text().isdigit() else 0 for res, edit in self.resource_edits.items()}
        self.hexagon_grid.set_hex_size(self.size_slider.value())
        self.hexagon_grid.generate_grid(resource_counts)
        
        total_land_tiles = sum(resource_counts.values())
        total_harbors = sum(self.hexagon_grid.harbor_counts.values())
        total_grid_tiles = len(self.hexagon_grid.tiles)
        total_water_tiles = total_grid_tiles - total_land_tiles
        
        shape_info = f"Shape: {self.hexagon_grid.board_shape}"
        if self.hexagon_grid.board_shape == "Rectangular":
            shape_info = f"Grid: {self.hexagon_grid.core_rows} x {self.hexagon_grid.core_cols}"

        self.grid_dims_label.setText(
            f"Land Tiles: {total_land_tiles}\n"
            f"Water Tiles: {total_water_tiles}\n"
            f"Harbors: {total_harbors}\n"
            f"{shape_info}"
        )

    def update_hex_size_from_slider(self, value): self.size_edit.setText(str(value))
    def update_from_text_hex_size(self):
        try:
            value = int(self.size_edit.text())
            self.size_slider.setValue(max(self.size_slider.minimum(), min(value, self.size_slider.maximum())))
        except ValueError: self.size_edit.setText(str(self.size_slider.value()))


# Generates a full screen w/boarder window
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
