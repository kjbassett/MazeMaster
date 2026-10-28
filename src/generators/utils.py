import numpy as np
import cv2    

def generate_box(w: int, h: int, wc: int = 0, pc: int = 1) -> np.ndarray:
    """Generates empty box with an outer wall

    Args:
        w (int): width
        h (int): height
        wc (int, optional): wall color. Defaults to 0.
        pc (int, optional): path color. Defaults to 1.

    Returns:
        np.ndarray: 2d array, empty box with an outer wall
    """
    maze = np.ones((h, w)) * pc
    maze[0,:] = wc
    maze[h-1,:] = wc
    maze[:,0] = wc
    maze[:,w-1] = wc
    return maze

def show_array(array: np.ndarray):
    """Displays a numpy array until you click q

    Args:
        array (np.ndarray): the array to be shown
    """
    cv2.namedWindow('Maze Generator', cv2.WINDOW_NORMAL)
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        cv2.imshow('Maze Generator', array)


def check_start_finish(w, h, start, finish):
    corners = [(0, 0), (0, w-1), (h-1, 0), (h-1, h-1)]
    if start in corners:
        raise ValueError("start cannot be in a corner")
    if finish in corners:
        raise ValueError("finish cannot be in a corner")
    if not any([start[0] == 0, start[0] == h-1, start[1] == 0, start[1] == w-1]):
        raise ValueError("start must lie on the perimeter of the maze")
    if not any([finish[0] == 0, finish[0] == h-1, finish[1] == 0, finish[1] == w-1]):
        raise ValueError('finish must lie on the perimeter of the maze')
    if abs(finish[0] - start[0]) + abs(finish[0] - start[0]) <= 1:
        raise ValueError('start and finish must be at least 2 units away from each other')