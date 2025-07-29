import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPolygonF, QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QPointF

from globals import (RESOURCE_COLORS, NUMBER_RATIOS, 
                     RED_NUMBERS, HARBOR_SYMBOLS, LAND_RESOURCE_RATIOS, HARBOR_RATIOS)

# ====== Tile class                ==============================================
class Tile:
    """
    Defines a tile both graphically and under the hood.
    Tile can be a:
    - Resource - (i.e sheep, ore) which utilizes the number token and resource type,
    - Water - could be a harbor which will track its harbor type.
    or water, which .
    All tiles carry geometric information where the hexagon can be "pointy" (axial) or "flat" (row/col)
    """
    def __init__(self, polygon, r, c, resource_type="desert", number=None, harbor_type=None, harbor_orientation=None):
        self.polygon = polygon
        self.r, self.c = r, c
        self.resource_type = resource_type
        self.number = number
        self.harbor_type = harbor_type
        self.harbor_orientation = harbor_orientation

# ====== HexagonGridWidget(QWidget) =============================================
class HexagonGridWidget(QWidget):
    """
    Will generate a hexagon grid based on resource count.
    When the number of resource tiles is less than 100, the generator will try to
    utilize the classic hexagonal shape of the catan board
    When the resource tile count is greater than 100, the generator will utilize a more
    rectangular structure.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.core_rows, self.core_cols = 0, 0
        self.hex_size = 30
        self.tiles = []
        self.board_shape = ""
        self.harbor_counts = {}
        self.setMinimumSize(400, 400)

    def generate_hexagonal_board(self, resource_pool):
        """
        For when the resourse tiles are less than 100, the classic hexagonal shape will be generated
        Will use axial coordinates 
        """
        self.board_shape = "Hexagonal"
        num_land_tiles = len(resource_pool)
        
        n = 2
        while (3 * n * n - 3 * n + 1) < num_land_tiles:
            n += 1

        self.core_rows = self.core_cols = 2 * n - 1

        grid_map = {}
        for q in range(-n + 1, n):
            r1 = max(-n + 1, -q - n + 1)
            r2 = min(n - 1, -q + n - 1)
            for r in range(r1, r2 + 1):
                if not resource_pool: break
                res = resource_pool.pop()
                # Number is assigned later
                grid_map[(q, r)] = (res, None)
        
        return self.build_final_grid(grid_map, 'pointy')

    def generate_rectangular_board(self, resource_pool):
        """When resource tiles are more than 100, will result in a more rectangular shape board"""
        self.board_shape = "Rectangular"
        num_land_tiles = len(resource_pool)
        
        start_point = int(math.sqrt(num_land_tiles))
        rows, cols = 1, num_land_tiles
        for i in range(start_point, 0, -1):
            if num_land_tiles % i == 0:
                rows, cols = i, num_land_tiles // i
                break
        self.core_rows, self.core_cols = rows, cols
        
        grid_map = {}
        # use col/row layout
        for r in range(self.core_rows):
            for c in range(self.core_cols):
                if not resource_pool: break
                res = resource_pool.pop()
                grid_map[(r, c)] = (res, None) # Number is assigned later
        
        return self.build_final_grid(grid_map, 'flat')

    def build_final_grid(self, land_tile_map, orientation):
        """
        Build the grid of landscapes and surround it with water tiles
        """
        grid_map = {}
        
        water_coords = set()
        for r_coord, c_coord in land_tile_map.keys():
            for neighbor_coord in self.get_neighbors(r_coord, c_coord, orientation):
                if neighbor_coord not in land_tile_map:
                    water_coords.add(neighbor_coord)
        
        for r, c in water_coords:
            grid_map[(r, c)] = Tile(None, r, c, "water")
            
        for (r, c), (res, num) in land_tile_map.items():
            grid_map[(r, c)] = Tile(None, r, c, res, num)

        all_coords = list(grid_map.keys())
        pixel_centers = []
        for r, c in all_coords:
            if orientation == 'flat':
                vert_dist = self.hex_size * math.sqrt(3)
                horiz_dist = self.hex_size * 1.5
                offset = vert_dist / 2 if c % 2 else 0
                x = c * horiz_dist
                y = r * vert_dist + offset
            else:
                x = self.hex_size * math.sqrt(3) * (c + r / 2.0)
                y = self.hex_size * 1.5 * r
            pixel_centers.append(QPointF(x,y))
        
        min_x = min(p.x() for p in pixel_centers) if pixel_centers else 0
        min_y = min(p.y() for p in pixel_centers) if pixel_centers else 0

        offset_x = self.hex_size - min_x
        offset_y = self.hex_size - min_y

        for (r, c), tile in grid_map.items():
            if orientation == 'flat':
                vert_dist = self.hex_size * math.sqrt(3)
                horiz_dist = self.hex_size * 1.5
                offset = vert_dist / 2 if c % 2 else 0
                center_x = c * horiz_dist + offset_x
                center_y = r * vert_dist + offset + offset_y
                angle_offset = 0
            else:
                center_x = self.hex_size * math.sqrt(3) * (c + r / 2.0) + offset_x
                center_y = self.hex_size * 1.5 * r + offset_y
                angle_offset = 30

            hexagon = QPolygonF([QPointF(center_x + self.hex_size * math.cos(math.pi/180 * (i + angle_offset)),
                                         center_y + self.hex_size * math.sin(math.pi/180 * (i + angle_offset)))
                                 for i in range(0, 360, 60)])
            tile.polygon = hexagon
            
        return grid_map
    
    def get_clump_score(self, tile, grid_map, orientation):
        """Calculates how many neighbors of a tile have the same resource type."""
        if not tile or tile.resource_type in ['water', 'desert']:
            return 0
        score = 0
        neighbors = [grid_map.get(n) for n in self.get_neighbors(tile.r, tile.c, orientation) if grid_map.get(n)]
        for neighbor in neighbors:
            if neighbor.resource_type == tile.resource_type:
                score += 1
        return score

    def separate_resources(self, grid_map, orientation):
        """
        Iteratively swaps resource tiles to break up clusters of the same type
        by reducing the overall "clump score" of the board.
        """
        land_tiles = [tile for tile in grid_map.values() if tile.resource_type not in ['water', 'desert']]
        if not land_tiles:
            return

        # Do several passes to improve distribution
        for _ in range(5):
            swapped_in_pass = False
            for tile1 in land_tiles:
                score1_before = self.get_clump_score(tile1, grid_map, orientation)
                
                # If the tile is not clumped dnt swap it
                if score1_before == 0:
                    continue

                # Swap with another resource type
                for tile2 in land_tiles:
                    if tile1 == tile2 or tile1.resource_type == tile2.resource_type:
                        continue

                    score2_before = self.get_clump_score(tile2, grid_map, orientation)

                    tile1.resource_type, tile2.resource_type = tile2.resource_type, tile1.resource_type
                    
                    score1_after = self.get_clump_score(tile1, grid_map, orientation)
                    score2_after = self.get_clump_score(tile2, grid_map, orientation)

                    # Did it reduce clump?
                    if (score1_after + score2_after) < (score1_before + score2_before):
                        swapped_in_pass = True
                        break
                    else:
                        # undo if it didn't work
                        tile1.resource_type, tile2.resource_type = tile2.resource_type, tile1.resource_type
            
            # if it searched and didn't need to swap, we are good
            if not swapped_in_pass:
                break

    def generate_grid(self, resource_counts):
        """The main grid generation orchestrator."""
        num_land_tiles = sum(resource_counts.values())
        if num_land_tiles <= 0:
            self.core_rows, self.core_cols, self.tiles = 0, 0, []
            self.update()
            return

        resource_pool = [res for res, count in resource_counts.items() for _ in range(count)]
        random.shuffle(resource_pool)

        orientation = 'pointy' if num_land_tiles < 100 else 'flat'
        if orientation == 'pointy':
            grid_map = self.generate_hexagonal_board(resource_pool)
        else:
            grid_map = self.generate_rectangular_board(resource_pool)
        
        # tries to separate clumps of resources
        self.separate_resources(grid_map, orientation)

        # Assign numbers after resources are finalized
        productive_land_tiles = [tile for tile in grid_map.values() if tile.resource_type not in ['water', 'desert']]
        random.shuffle(productive_land_tiles)
        
        num_productive_tiles = len(productive_land_tiles)
        total_prop_parts = sum(NUMBER_RATIOS.values())
        number_pool = []
        if num_productive_tiles > 0 and total_prop_parts > 0:
            number_pool = [num for num, parts in NUMBER_RATIOS.items() for _ in range(round(num_productive_tiles * (parts / total_prop_parts)))]
        while len(number_pool) < num_productive_tiles: number_pool.append(random.choice(list(NUMBER_RATIOS.keys())))
        while len(number_pool) > num_productive_tiles: number_pool.pop()
        random.shuffle(number_pool)
        
        for tile in productive_land_tiles:
            if number_pool:
                tile.number = number_pool.pop()

        # harbor placement. TODO ensure that generic harbor gets utilized first based on ratio
        coastal_water_tiles = [tile for tile in grid_map.values() if tile.resource_type == 'water' and any(grid_map.get(n) and grid_map.get(n).resource_type != 'water' for n in self.get_neighbors(tile.r, tile.c, orientation))]
        
        harbor_slots, used_and_neighbor_coords = [], set()
        for tile in sorted(coastal_water_tiles, key=lambda t: (t.r, t.c)):
            if (tile.r, tile.c) not in used_and_neighbor_coords:
                harbor_slots.append(tile)
                used_and_neighbor_coords.add((tile.r, tile.c))
                for neighbor_coord in self.get_neighbors(tile.r, tile.c, orientation): used_and_neighbor_coords.add(neighbor_coord)
        
        num_harbor_slots = len(harbor_slots)
        num_base_game_sets = num_land_tiles / sum(LAND_RESOURCE_RATIOS.values())
        
        self.harbor_counts = {}
        total_ratio_harbors = 0
        for harbor_type, ratio in HARBOR_RATIOS.items():
            count = round(ratio * num_base_game_sets)
            self.harbor_counts[harbor_type] = count
            total_ratio_harbors += count
        
        if num_harbor_slots > total_ratio_harbors:
            self.harbor_counts['generic'] = self.harbor_counts.get('generic', 0) + (num_harbor_slots - total_ratio_harbors)

        harbor_pool = [harbor for harbor, count in self.harbor_counts.items() for _ in range(count)]
        random.shuffle(harbor_pool)

        for slot in harbor_slots:
            if not harbor_pool: break
            land_neighbor = [n for n in self.get_neighbors(slot.r, slot.c, orientation) if grid_map.get(n) and grid_map.get(n).resource_type != 'water'][0]
            dr, dc = land_neighbor[0] - slot.r, land_neighbor[1] - slot.c
            
            if orientation == 'flat':
                if slot.c % 2 == 0: orientation_map = {(-1,-1):5,(-1,0):4,(-1,1):3,(0,1):2,(1,0):1,(0,-1):0}
                else: orientation_map = {(0,-1):5,(-1,0):4,(0,1):3,(1,1):2,(1,0):1,(1,-1):0}
            else:
                orientation_map = {(0,1):2,(1,0):3, (1,-1):4, (0,-1):5, (-1,0):0, (-1,1):1}
            slot.harbor_type, slot.harbor_orientation = harbor_pool.pop(), orientation_map.get((dr, dc))
        
        self.tiles = list(grid_map.values())
        self.update()

    def get_neighbors(self, r, c, orientation):
        if orientation == 'flat':
            if c % 2 == 0: offsets = [(-1,0),(-1,1),(0,1),(1,0),(0,-1),(-1,-1)]
            else: offsets = [(-1,0),(0,1),(1,1),(1,0),(1,-1),(-1,-1)]
            return [(r + dr, c + dc) for dr, dc in offsets]
        else:
            q, r_ax = r, c
            axial_offsets = [(0,1),(1,0),(1,-1),(0,-1),(-1,0),(-1,1)]
            return [(q + dq, r_ax + dr) for dq, dr in axial_offsets]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for tile in self.tiles:
            if not tile.polygon: continue
            painter.setPen(QPen(QColor(0,0,0), 2))
            painter.setBrush(QBrush(RESOURCE_COLORS.get(tile.resource_type, QColor("gray"))))
            painter.drawPolygon(tile.polygon)
            if tile.number is not None:
                font = QFont("Arial", int(self.hex_size*0.5), QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QColor("red") if tile.number in RED_NUMBERS else QColor("black"))
                painter.drawText(tile.polygon.boundingRect(), Qt.AlignmentFlag.AlignCenter, str(tile.number))
            if tile.harbor_type is not None:
                font = QFont("Arial", int(self.hex_size*0.3), QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QColor("black"))
                painter.drawText(tile.polygon.boundingRect(), Qt.AlignmentFlag.AlignCenter, HARBOR_SYMBOLS.get(tile.harbor_type))

    def set_hex_size(self, size): self.hex_size = size
