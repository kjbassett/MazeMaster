import argparse
import random
from typing import Callable

import cv2
import numpy as np
from PIL import Image

from utils import generate_box, show_array


def gen_maze(
    w: int,
    h: int,
    wc: int = 0,
    pc: int = 1,
    seed: int | None = None,
    on_step: Callable[[np.ndarray, tuple[int, int]], None] | None = None,
) -> np.ndarray:
    """Generates a maze where every path runs straight and turns at right angles

    Paths sit on odd rows/columns and walls on even ones, so every corridor is
    1 pixel wide and every wall pixel is joined to its neighbors by an edge.
    A depth-first search (recursive backtracker) carves the paths, so there is
    exactly one route between any two points.

    Args:
        w (int): width in pixels, at least 5
        h (int): height in pixels, at least 5
        wc (int, optional): wall value. Defaults to 0.
        pc (int, optional): path value. Defaults to 1.
        seed (int, optional): random seed, for repeatable mazes. Defaults to None.
        on_step (callable, optional): called as on_step(maze, (y, x)) after every
            carve and backtrack, with the pixel the search is currently on.
            Used to animate generation. Defaults to None.

    Returns:
        np.ndarray: 2d array of wc and pc values
    """
    if w < 5 or h < 5:
        raise ValueError('width and height must be at least 5')
    rng = random.Random(seed)

    # an even dimension leaves a spare line of wall on the bottom/right edge
    rows = (h - 1) // 2
    cols = (w - 1) // 2

    maze = generate_box(w, h, wc, wc).astype(np.uint8)
    visited = np.zeros((rows, cols), dtype=bool)

    # depth-first search over cells, using a stack instead of recursion
    # so large mazes don't hit Python's recursion limit
    stack = [(0, 0)]
    visited[0, 0] = True
    maze[1, 1] = pc
    while stack:
        r, c = stack[-1]
        neighbors = [
            (r + dr, c + dc)
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if 0 <= r + dr < rows and 0 <= c + dc < cols and not visited[r + dr, c + dc]
        ]
        if not neighbors:
            stack.pop()
            if on_step and stack:
                on_step(maze, (2 * stack[-1][0] + 1, 2 * stack[-1][1] + 1))
            continue
        nr, nc = rng.choice(neighbors)
        visited[nr, nc] = True
        # carve the cell and the wall between it and the current cell
        maze[2 * nr + 1, 2 * nc + 1] = pc
        maze[r + nr + 1, c + nc + 1] = pc
        stack.append((nr, nc))
        if on_step:
            on_step(maze, (2 * nr + 1, 2 * nc + 1))

    # openings: top edge above the first cell, bottom edge below the last cell
    maze[0, 1] = pc
    maze[2 * rows, 2 * cols - 1] = pc
    if 2 * rows < h - 1:
        # even height: extend through the spare wall line to the perimeter
        maze[h - 1, 2 * cols - 1] = pc
    return maze


class Animator:
    """Draws the maze in a window as gen_maze carves it; pass as on_step

    Press q in the window to skip to the finished maze.
    """

    def __init__(
        self,
        w: int,
        h: int,
        wall_rgb: tuple[int, int, int],
        path_rgb: tuple[int, int, int],
        head_rgb: tuple[int, int, int] = (255, 0, 0),
        steps_per_frame: int = 1,
        delay_ms: int = 1,
    ):
        # opencv wants bgr
        self.palette = np.array([wall_rgb[::-1], path_rgb[::-1]], dtype=np.uint8)
        self.head_bgr = head_rgb[::-1]
        self.steps_per_frame = max(1, steps_per_frame)
        self.delay_ms = max(1, delay_ms)
        self.step = 0
        self.skip = False

        cv2.namedWindow('Maze Generator', cv2.WINDOW_NORMAL)
        # scale up 4 ez viewing
        window_w, window_h = w, h
        while window_w < 500 and window_h < 500:
            window_w, window_h = window_w * 2, window_h * 2
        cv2.resizeWindow('Maze Generator', window_w, window_h)

    def __call__(self, maze: np.ndarray, head: tuple[int, int]):
        self.step += 1
        if self.skip or self.step % self.steps_per_frame:
            return
        frame = self.palette[maze]
        frame[head] = self.head_bgr
        cv2.imshow('Maze Generator', frame)
        if cv2.waitKey(self.delay_ms) & 0xFF == ord('q'):
            self.skip = True


def save_indexed_png(maze: np.ndarray, path: str, wall_rgb: tuple[int, int, int], path_rgb: tuple[int, int, int]):
    """Saves a maze of 0 (wall) and 1 (path) values as a palette png

    Args:
        maze (np.ndarray): 2d array of 0s and 1s
        path (str): file to write
        wall_rgb (tuple[int, int, int]): color for index 0
        path_rgb (tuple[int, int, int]): color for index 1
    """
    img = Image.fromarray(maze.astype(np.uint8), mode='P')
    img.putpalette([*wall_rgb, *path_rgb])
    img.save(path)


def parse_rgb(value: str) -> tuple[int, int, int]:
    """Parses 'r,g,b' (e.g. '0,0,0') into a color tuple"""
    rgb = tuple(int(v) for v in value.split(','))
    if len(rgb) != 3 or not all(0 <= v <= 255 for v in rgb):
        raise argparse.ArgumentTypeError('color must be r,g,b with values 0-255')
    return rgb


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a maze with right-angle paths')
    parser.add_argument('width', type=int, help='maze width in pixels (odd works best)')
    parser.add_argument('height', type=int, help='maze height in pixels (odd works best)')
    parser.add_argument('-o', '--output', default='output.png', help='png file to write')
    parser.add_argument('--wall-color', type=parse_rgb, default=(0, 0, 0), help='r,g,b')
    parser.add_argument('--path-color', type=parse_rgb, default=(255, 255, 255), help='r,g,b')
    parser.add_argument('--seed', type=int, help='random seed for a repeatable maze')
    parser.add_argument('--show', action='store_true', help='show the maze in a window (press q to close)')
    parser.add_argument('--animate', action='store_true', help='watch the maze being built (press q to skip ahead)')
    parser.add_argument('--steps-per-frame', type=int, default=1, help='carving steps drawn per frame when animating')
    parser.add_argument('--delay', type=int, default=1, help='milliseconds to wait between frames when animating')
    args = parser.parse_args()

    animator = None
    if args.animate:
        animator = Animator(
            args.width, args.height, args.wall_color, args.path_color,
            steps_per_frame=args.steps_per_frame, delay_ms=args.delay,
        )
    maze = gen_maze(args.width, args.height, seed=args.seed, on_step=animator)
    save_indexed_png(maze, args.output, args.wall_color, args.path_color)
    print(f'saved {args.width}x{args.height} maze to {args.output}')
    if args.show:
        show_array(maze.astype(np.float32))
