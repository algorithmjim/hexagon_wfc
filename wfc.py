import numpy as np
from utility import get_neighbor_transform


class WaveFunctionCollapse:
    def __init__(self, tile_map, ruleset) -> None:
        self.tile_map = tile_map
        self.width = len(tile_map[0])
        self.height = len(tile_map)
        self.ruleset = ruleset
        self.total_tiles = self.width * self.height
        self.completed = 0
        self.has_started = False


    def fill_tile(self, x, y, force_choice=None):
        # weights
        weights = []
        for val in self.tile_map[y][x].possible_values:
            weights.append(self.ruleset[str(val)]["rarity"])
        # random choice
        choice = np.random.choice(self.tile_map[y][x].possible_values, p=weights/np.sum(weights))
        if force_choice is not None:
            choice = force_choice
        self.tile_map[y][x].assign_terrian_type(choice, y)


    def initialize(self):
        random_x = np.random.randint(0, len(self.tile_map[0]))
        random_y = np.random.randint(0, len(self.tile_map))
        self.fill_tile(random_x, random_y, force_choice=0)
        self.completed += 1
        self.propagate(random_x, random_y)


    def step(self):
        if self.completed % 100 == 0:
            print(f"{self.completed/self.total_tiles:.2f}% tiles completed")
        if not self.has_started:
            self.has_started = True
            self.initialize()
            return

        # find the tile with the fewest possible values
        min_x = None
        min_y = None
        min_len = None
        is_done = True
        possible_points = []
        for y in range(self.height):
            for x in range(self.width):
                if self.tile_map[y][x].tile_img_idx == -1:
                    possible_points.append((x, y))
                    if min_len is None or len(self.tile_map[y][x].possible_values) < min_len:
                        min_len = len(self.tile_map[y][x].possible_values)
                        min_x = x
                        min_y = y
                        is_done = False

        # # choose random point
        # r_idx = np.random.randint(0, len(possible_points))
        # min_x, min_y = possible_points[r_idx]

        if is_done:
            return True
        self.fill_tile(min_x, min_y)
        self.completed += 1
        self.propagate(min_x, min_y)


    def get_parallax_coords(self, x, y):
        edge_x = x
        edge_y = y
        if edge_x < 0:
            edge_x += self.width
        elif edge_x >= self.width:
            edge_x -= self.width

        if edge_y < 0:
            edge_y += self.height
        elif edge_y >= self.height:
            edge_y -= self.height
        
        return edge_x, edge_y
    

    def propagate(self, x, y):
        total_tiles_to_propagate = self.width * self.height
        tiles_propagated = []
        tiles_to_propagate = []
        total_propagated = 0
        n_tf = get_neighbor_transform(y)
        for tf in n_tf:
            edge_x, edge_y = self.get_parallax_coords(x + tf[0], y + tf[1])
            if self.tile_map[edge_y][edge_x].tile_img_idx == -1:
                tiles_to_propagate.append((edge_x, edge_y))

        while total_propagated < total_tiles_to_propagate:
            back_idx = -1
            while len(tiles_to_propagate) == 0 and -back_idx <= len(tiles_propagated):
                last_tile = tiles_propagated[back_idx]
                n_tf = get_neighbor_transform(last_tile[1])
                for tf in n_tf:
                    edge_x, edge_y = self.get_parallax_coords(last_tile[0] + tf[0], last_tile[1] + tf[1])
                    if self.tile_map[edge_y][edge_x].tile_img_idx == -1 and (edge_x, edge_y) not in tiles_propagated:
                        tiles_to_propagate.append((edge_x, edge_y))
                back_idx -= 1
                if -back_idx > len(tiles_propagated):
                    break


            if len(tiles_to_propagate) == 0:
                for y in range(self.height):
                    for x in range(self.width):
                        if self.tile_map[y][x].tile_img_idx == -1 and (x, y) not in tiles_propagated:
                            tiles_to_propagate.append((x, y))
            
            if len(tiles_to_propagate) == 0:
                break

            curr_tile = tiles_to_propagate.pop(0)
            if curr_tile in tiles_propagated:
                continue
            if self.tile_map[curr_tile[1]][curr_tile[0]].tile_img_idx != -1:
                total_propagated += 1
                tiles_propagated.append(curr_tile)
                continue
            n_tf = get_neighbor_transform(curr_tile[1])
            neighbors_possible_neighbors = []
            force_water = False
            for tf in n_tf:
                edge_x, edge_y = self.get_parallax_coords(curr_tile[0] + tf[0], curr_tile[1] + tf[1])
                if (edge_x, edge_y) in tiles_propagated:
                    continue
                else:
                    tiles_to_propagate.append((edge_x, edge_y))
                
                if self.tile_map[edge_y][edge_x].tile_img_idx != -1:
                    neighbors_possible_neighbors.append(self.ruleset[str(self.tile_map[edge_y][edge_x].tile_img_idx)]["possible_neighbors"])
                    if "must_touch" in self.ruleset[str(self.tile_map[edge_y][edge_x].tile_img_idx)].keys():
                        # check surrounding tiles edge and see if their conditions are met
                        sub_tf = get_neighbor_transform(edge_y)
                        num_uninit_neighbors = 0
                        has_water = False
                        for sub_tf in sub_tf:
                            sub_edge_x, sub_edge_y = self.get_parallax_coords(edge_x + sub_tf[0], edge_y + sub_tf[1])
                            if self.tile_map[sub_edge_y][sub_edge_x].tile_img_idx == -1:
                                num_uninit_neighbors += 1
                            else:
                                if self.tile_map[sub_edge_y][sub_edge_x].tile_img_idx in self.ruleset[str(self.tile_map[edge_y][edge_x].tile_img_idx)]["must_touch"]:
                                    has_water = True
                                    break
                        if not has_water and num_uninit_neighbors == 1:
                            force_water = True                    
                else:
                    possible_neighbors = []
                    for val in self.tile_map[edge_y][edge_x].possible_values:
                        possible_neighbors = list(set(self.ruleset[str(val)]["possible_neighbors"] + possible_neighbors))
                    neighbors_possible_neighbors.append(possible_neighbors)
            
            new_possible_values = []
            if force_water:
                neighbors_possible_neighbors = [[6]]
            for val in [int(key) for key in self.ruleset.keys()]:
                in_all = True
                for neighbor_possible_neighbors in neighbors_possible_neighbors:
                    if val not in neighbor_possible_neighbors:
                        in_all = False
                        break
                if in_all:
                    new_possible_values.append(val)
            self.tile_map[curr_tile[1]][curr_tile[0]].possible_values = new_possible_values
            


            total_propagated += 1
            tiles_propagated.append(curr_tile)
        
            

