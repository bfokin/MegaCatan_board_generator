# MegaCatan_board_generator


Wanna generate catan boards on the go? Why not, go for it.

Run ```megaCatan_board_generator.py```

# Requirements
- pyQt6


# Usage
 - This generator will start up as a base game generator.
    - All ratio of elements will be preserved
 - As the tiles increase in size, below 100 lanscape tiles, the form will attempt to stay in a hexagon-esque shape.
 - When landscape tiles go over 100 tiles, the generator will make a more rectagular shape.
 - Press the generate button to generate a new board
 - Use hex size to decrease the visual size of the board
 - Harbors place automatically but with certain number of tiles, the generation cannot place a harbor every other water tile. Use your best judgement.

# Tile description

### Ports come in the same form:
   - "3 : 1" are the 3 to 1 generic ports
   - "S" are sheep 2 to 1 ports
   - "W" are wood 2 to 1 ports
   - "Wh" are wheat 2 to 1 ports
   - "O" are ore or rock 2 to 1 ports
   - "B" are brick 2 to 1 ports

### Landscape tiles
   - Orange tiles are brick
   - Black tiles are desert
   - White tiles are sheep
   - Green Tiles are wood
   - Grey tiles are ore
   - Yellow tiles are wheat