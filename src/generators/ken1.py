import cv2
import numpy as np
import random
import time

from utils import generate_box, show_array


def get_adjacent_coords(coord):
    return [
        [coord[0] - 1, coord[1]],
        [coord[0] + 1, coord[1]],
        [coord[0], coord[1] - 1],
        [coord[0], coord[1] + 1]
    ]


def find_available_coords(adjacencies: np.ndarray, maze: np.ndarray, ep: np.ndarray, finish: np.ndarray, pc: int, connected: bool) -> list[np.ndarray]:
    adjacent = adjacencies[ep[0], ep[1]]
    available_coords = []
    
    for adj in adjacent:
        # if it already touches the finish, we are done
        if (adj == finish).all():
            return [adj]
        # an adjacent coordinate (adj) is not available if ...
        # it borders the edge of the picture
        if adj[0] <= 0 or adj[0] >= maze.shape[0] - 1:
            continue
        elif adj[1] <= 0 or adj[1] >= maze.shape[1] - 1:
            continue
        # or if any of adj's adjacent coords are already a path
        # (don't join 2 paths)
        for adj_adj in adjacencies[adj[0], adj[1]]:
            # ignore current path endpoint and finish
            if (adj_adj == ep).all():
                continue
            elif maze[adj_adj[0], adj_adj[1]] == pc:
                if (adj_adj == finish).all():
                    if connected:
                        continue
                    return [adj]
                break
        
        else: # if we didn't break a rule (didn't break of out of the loop)
            available_coords.append(adj)

    return available_coords

def gen_maze(w: int, h: int, wc: int = 0, pc: int = 1):
    # create window
    cv2.namedWindow('Maze Generator', cv2.WINDOW_NORMAL)
    # scale up 4 ez viewing
    cv2.resizeWindow('Maze Generator', 900, 900) 

    maze = generate_box(w, h, wc, wc)
    # adjacencies holds all adjacent coordinate for each coordinate
    adjacencies = np.array([[get_adjacent_coords([y, x]) for x in range(w)] for y in range(h)])
    maze[1, 0], maze[h-2, w-1] = pc, pc # start and end
    finish = np.array([h-2, w-1])

    path_endpoints = [np.array([1, 0])]
    connected = False
    times = [] # holds time taken to execute each iteration
    while not connected:
        # If no end points remain, choose a random path point
        if not path_endpoints:
            path_coords = np.argwhere(maze[:h-1, :w-1] == 1)
            coord_idx = np.random.randint(len(path_coords))
            coord = path_coords[coord_idx]
            path_endpoints.append(coord)

        # while there are paths that haven't terminated
        while path_endpoints:
            t = time.time()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): # press q on the window to stop
                connected = True # just to make the program stop
                break
            # get the first endpoint and remove from list
            ep = path_endpoints.pop(0)
            # get adjacent, available coords to extend path
            available_coords = find_available_coords(adjacencies, maze, ep, finish, pc, connected)
            if not available_coords:
                continue
            # it must go to at least 1 available coord
            n_branches = 1
            # 5% chance for each additional branch
            while n_branches < len(available_coords) and random.random() < 0.05:
                n_branches += 1
            # randomly select n_branches of the total available coords
            next_coords = random.sample(available_coords, n_branches)

            for coord in next_coords:
                if (coord == finish).all():
                    connected = True
                # add the new coord back to the list of endpoints
                path_endpoints.append(coord)
                # color the coord to be a path
                maze[coord[0], coord[1]] = pc
            cv2.imshow('Maze Generator', maze)
            times.append(time.time() - t)

    print(sum(times) / len(times))
    maze = (maze * 255).astype(np.uint8) 
    return maze

cv2.imwrite('output.png', gen_maze(300, 300))