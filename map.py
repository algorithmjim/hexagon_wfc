import sys
import numpy as np
import random
from random import shuffle
from utility import load_tileset_rules, load_tileset, distance, get_neighbor_transform
from constants import *
from collections import defaultdict
from wfc import WaveFunctionCollapse

class MapTile:
    def __init__(self, x, y=None, idx_x=None, idx_y=None):
        self.tiles = load_tileset()
        if type(self) == type(x):
            self.x = x.x
            self.y = x.y
            self.idx_x = x.idx_x
            self.idx_y = x.idx_y
        else:
            self.x = x
            self.y = y
            self.idx_x = idx_x
            self.idx_y = idx_y
        self.tile_img = None
        self.tile_img_idx = -1
        self.ruleset = load_tileset_rules()
        self.possible_values = [int(key) for key in self.ruleset.keys()]
        
        self.possible_neighbors = [int(key) for key in self.ruleset.keys()]
        self.neighbor_weights = [1.0 for key in self.ruleset.keys()]
        self.tile_name = None
        self.layer_lvl = None
        self.terrian_cost = None

        self.render = True

    
    def assign_terrian_type(self, tile_img_idx, layer_lvl):
        self.tile_img = self.tiles[tile_img_idx]
        self.tile_img_idx = tile_img_idx
        self.layer_lvl = layer_lvl
        #ruleset = load_tileset_rules()
        if tile_img_idx == -1:
            self.possible_neighbors = [key for key in self.ruleset.keys()]
            self.name = "void"
            self.neighbor_weights = [1.0 for _ in self.ruleset.keys()]
        else:
            self.possible_neighbors = self.ruleset[str(self.tile_img_idx)]["possible_neighbors"]
            self.tile_name = self.ruleset[str(self.tile_img_idx)]["name"]
        #    self.neighbor_weights = ruleset[str(self.tile_img_idx)]["neighbor_weights"]
            self.terrian_cost = self.ruleset[str(self.tile_img_idx)]["terrian_cost"]



class MapGenerater:
    def __init__(self):
        self.ruleset = load_tileset_rules()
        self.tiles = load_tileset()
        self.tile_map = []
        self.tile_map_width = None
        self.tile_map_height = None
        self.generate_blank_map()
        self.create_unique_map()
        #self.populate_map()

    '''
    Adds NUM_PLAYERS number of towns to the map
    '''
    def populate_map(self):
        # loop through the map clockwise and add towns evenly spaced
        
        # get the number of tiles per player
        tiles_per_player_x = self.tile_map_width // NUM_PLAYERS
        tiles_per_player_y = self.tile_map_height // NUM_PLAYERS

        for i in range(NUM_PLAYERS):
            # get x, y coordinates of the tile to place the town on
            x = i * tiles_per_player_x
            y = i * tiles_per_player_y
            self.make_town(x, y)


    def make_town(self, x, y):
        self.tile_map[y][x].assign_terrian_type(self.tiles[8], 8, y)


    def get_tile_by_id(self, layer_lvl):
        return_val = None
        num_val = 0
        for y in range(self.tile_map_height):
            for x in range(self.tile_map_width):
                if self.tile_map[y][x].layer_lvl == layer_lvl:
                    return_val = self.tile_map[y][x]
                    num_val += 1
        assert num_val == 1
        return return_val

    def update_visibility(self, camera, x, y, canvas):
        neighbor_transform = get_neighbor_transform(camera.y)
        
        canvas.update_obj_visibility(self.tile_map[camera.y][camera.x].layer_lvl,UPDATE_VISIBILITY)
        for tf in neighbor_transform:
            edge_x = camera.x + tf[0]
            edge_y = camera.y + tf[1]
                    # if edge_x < 0 or edge_x >= w:
                    #     continue
                    # if edge_y < 0 or edge_y >= h:
                    #     continue
            if edge_x < 0:
                edge_x += self.tile_map_width
            elif edge_x >= self.tile_map_width:
                edge_x -= self.tile_map_width

            if edge_y < 0:
                edge_y += self.tile_map_height
            elif edge_y >= self.tile_map_height:
                edge_y -= self.tile_map_height
            canvas.update_obj_visibility(self.tile_map[edge_y][edge_x].layer_lvl,UPDATE_VISIBILITY)
        
        neighbor_transform = get_neighbor_transform(y)

        canvas.update_obj_visibility(self.tile_map[y][x].layer_lvl, 1)
        for tf in neighbor_transform:
            edge_x = x + tf[0]
            edge_y = y + tf[1]
                    # if edge_x < 0 or edge_x >= w:
                    #     continue
                    # if edge_y < 0 or edge_y >= h:
                    #     continue
            if edge_x < 0:
                edge_x += self.tile_map_width
            elif edge_x >= self.tile_map_width:
                edge_x -= self.tile_map_width

            if edge_y < 0:
                edge_y += self.tile_map_height
            elif edge_y >= self.tile_map_height:
                edge_y -= self.tile_map_height
            canvas.update_obj_visibility(self.tile_map[edge_y][edge_x].layer_lvl, 1)


    def generate_blank_map(self):
        self.tile_map_width = np.random.randint(MIN_MAP_WIDTH / 2, MAX_MAP_WIDTH / 2) * 2
        self.tile_map_height = np.random.randint(MIN_MAP_HEIGHT / 2, MAX_MAP_HEIGHT / 2) * 2

        curr_x = 0
        curr_y = 0

        sep_x = 1.5 * TILE_WIDTH
        sep_y = 0.47 * TILE_WIDTH

        for y in range(self.tile_map_height):
            new_row = []
            if y % 2 == 0:
                curr_x += 0.75 * TILE_WIDTH
            for x in range(self.tile_map_width):
                map_tile = MapTile(int(curr_x), int(curr_y), x, y)
                #map_tile.assign_terrian_type(self.tiles[0], 0)
                new_row.append(map_tile)
                curr_x += sep_x

            self.tile_map.append(new_row)
            curr_x = 0
            curr_y += sep_y

    # how do you spell parallax
    def get_parallax_coords(self, x, y):
        edge_x = x
        edge_y = y
        if edge_x < 0:
            edge_x += self.tile_map_width - 2
        elif edge_x >= self.tile_map_width:
            edge_x -= self.tile_map_width

        if edge_y < 0:
            edge_y += self.tile_map_height - 2
        elif edge_y >= self.tile_map_height:
            edge_y -= self.tile_map_height
        
        return edge_x, edge_y


    def create_unique_map(self, method="wave_function_collapse"):
        if method == "random":
            tiles_for_generation = []
            counter = 0
            for y in range(self.tile_map_height):
                for x in range(self.tile_map_width):
                    tiles_for_generation.append([x, y, counter])
                    counter += 1

            shuffle(tiles_for_generation)
            #tiles_for_generation.sort(key=lambda x: np.sqrt((x[0] + int(self.tile_map_width / 2)) ** 2 + (x[1] + int(self.tile_map_height / 2)) ** 2), reverse=False)
            for pair in tiles_for_generation:
                y = pair[1]
                x = pair[0]
                if self.tile_map[y][x].tile_name is None:
                    self.choose_terrian_type(x, y, pair[2])
        elif method == "wave_function_collapse":
            wfc = WaveFunctionCollapse(self.tile_map, self.ruleset)
            while True:
                done = wfc.step()
                if done:
                    break


    def choose_terrian_type(self, x, y, counter):
        neighbor_transform = get_neighbor_transform(y)
        #possible_neighbors = []
        possible_terrian_types = {}
        for key in self.ruleset.keys():
            possible_terrian_types[int(key)] = 0.0
        
        total_possible_terrians = [int(key) for key in self.ruleset.keys()]

        for transform in neighbor_transform:
            neighbor_x = x + transform[0]
            neighbor_y = y + transform[1]
            if neighbor_x < 0 or neighbor_x >= self.tile_map_width:
                continue
            elif neighbor_y < 0 or neighbor_y >= self.tile_map_height:
                continue
            
            total_possible_terrians = [key for key in total_possible_terrians if key in self.tile_map[neighbor_y][neighbor_x].possible_neighbors]
            for key, weight in zip(self.tile_map[neighbor_y][neighbor_x].possible_neighbors, self.tile_map[neighbor_y][neighbor_x].neighbor_weights):
                if key in total_possible_terrians:
                    possible_terrian_types[key] += weight

            # if self.tile_map[neighbor_y][neighbor_x].tile_img_idx != -1:
            #     possible_terrian_types[self.tile_map[neighbor_y][neighbor_x].tile_img_idx] += 1.0
        
        total_weight = sum([value for _, value in possible_terrian_types.items()])
        weight_matrix = {}
        for key, value in possible_terrian_types.items():
            if value != 0:
                weight_matrix[key] = value / total_weight
            else:
                weight_matrix[key] = None

        choices = [key for key, value in weight_matrix.items() if not value is None]
        weights = [value for key, value in weight_matrix.items() if not value is None]
        randomList = random.choices(choices, weights=weights, k=1)
        self.tile_map[y][x].assign_terrian_type(self.tiles[int(randomList[0])], randomList[0], counter)

    def get_camera_pixel_pos(self, camera):
        curr_x = 0
        curr_y = 0

        sep_x = 1.5 * TILE_WIDTH
        sep_y = 0.47 * TILE_WIDTH

        for y in range(self.tile_map_height):
            if y % 2 == 0:
                curr_x += 0.75 * TILE_WIDTH
            for x in range(self.tile_map_width):
                if x == camera.x and y == camera.y:
                    return int(curr_x), int(curr_y), self.tile_map[y][x]
                curr_x += sep_x
            curr_x = 0
            curr_y += sep_y

    
    def move_camera_to_selected(self, camera, object):
        curr_x = 0
        curr_y = 0

        sep_x = 1.5 * TILE_WIDTH
        sep_y = 0.47 * TILE_WIDTH

        obj_x = object.x
        obj_y = object.y
        if obj_x < 0:
            obj_x += self.tile_map_width * sep_x
        elif obj_x >= self.tile_map_width * sep_x:
            obj_x -= self.tile_map_width * sep_x
        if obj_y < 0:
            #print(object.y)
            obj_y += self.tile_map_height * sep_y
            #print(object.y)
        elif obj_y >= self.tile_map_height * sep_y:
            obj_y -= self.tile_map_height * sep_y

        min_d = None
        min_idx = None
        for y in range(self.tile_map_height):
            if y % 2 == 0:
                curr_x += 0.75 * TILE_WIDTH
            for x in range(self.tile_map_width):
                d = distance(curr_x, curr_y, obj_x, obj_y)
                if min_d is None or d < min_d:
                    min_d = d
                    min_idx = [x, y]
                curr_x += sep_x
            curr_x = 0
            curr_y += sep_y
        # camera.x = min_idx[0]
        # camera.y = min_idx[1]
        # print(self.tile_map[min_idx[1]][min_idx[0]].y)
        return camera, self.tile_map[min_idx[1]][min_idx[0]]


class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.weights = {}
    
    def add_edge(self, from_node, to_node, weight):
        self.edges[from_node].append(to_node)
        self.weights[(from_node, to_node)] = weight


def dijsktra(graph, initial, end):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    
    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
    
    # Work back through destinations in shortest path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Reverse path
    path = path[::-1]
    return path


class MapNavigator:
    def __init__(self, tile_map, w, h, camera, source_id, dest_id):
        self.graph = Graph()
        self.build_graph(tile_map, w, h, camera)
        self.path = dijsktra(self.graph, source_id, dest_id)
        # print(f"{camera.x, camera.y}")
        # print(f"{self.graph.edges[(camera.x, camera.y)]}")
        # for thing in self.path:
        #     print(thing)
        #     print(f"{self.graph.edges[thing]}")

    def get_path(self):
        return self.path

    # Function to build the graph
    def build_graph(self, tile_map, w, h, camera):
        for y in range(h):
            for x in range(w):
                if y % 2 == 0:
                    neighbor_transform = [[0, -1],
                                        [0, 1],
                                        [0, -2],
                                        [0, 2],
                                        [1, 1],
                                        [1, -1]]
                else:
                    neighbor_transform = [[0, -1],
                                        [0, 1],
                                        [0, -2],
                                        [0, 2],
                                        [-1, 1],
                                        [-1, -1]]
                
                for tf in neighbor_transform:
                    edge_x = x + tf[0]
                    edge_y = y + tf[1]
                    # if edge_x < 0 or edge_x >= w:
                    #     continue
                    # if edge_y < 0 or edge_y >= h:
                    #     continue
                    if edge_x < 0:
                        edge_x += w
                    elif edge_x >= w:
                        edge_x -= w

                    if edge_y < 0:
                        edge_y += h
                    elif edge_y >= h:
                        edge_y -= h
                    self.graph.add_edge((x, y), (edge_x, edge_y), tile_map[edge_y][edge_x].terrian_cost + tile_map[y][x].terrian_cost)
                    #self.graph.add_edge((x + tf[0], y + tf[1]), (x, y), tile_map[y + tf[1]][x + tf[0]].terrian_cost + tile_map[y][x].terrian_cost)