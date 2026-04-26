import sys
from PIL import Image
import copy
import queue as Queue
import math
import os
# import matplotlib.pyplot as plt

'''
These variables are determined at runtime and should not be changed or mutated by you
'''
start = (0, 0)  # a single (x,y) tuple, representing the start position of the search algorithm
end = (0, 0)  # a single (x,y) tuple, representing the end position of the search algorithm
difficulty = ""  # a string reference to the original import file
G = 0
E = 0
e_list = []
'''
These variables determine display coler, and can be changed by you, I guess
'''
NEON_GREEN = (0, 255, 0)
PURPLE = (85, 26, 139)
LIGHT_GRAY = (50, 50, 50)
DARK_GRAY = (100, 100, 100)

'''
These variables are determined and filled algorithmically, and are expected (and required) be mutated by you
'''
path = []  # an ordered list of (x,y) tuples, representing the path to traverse from start-->goal
expanded = {}  # a dictionary of (x,y) tuples, representing nodes that have been expanded
frontier = {}  # a dictionary of (x,y) tuples, representing nodes to expand to in the future

open = Queue.PriorityQueue()
came_from = {}
cost_so_far = {}

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def search(map, width, height):
    """
    This function is meant to use the global variables [start, end, path, expanded, frontier] to search through the
    provided map.
    :param map: A '1-concept' PIL PixelAccess object to be searched. (basically a 2d boolean array)
    """

    # Movement directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while not open.empty(): # Search until the priority queue is empty
        current_priority, current = open.get()  # Get lowest cost node

        # Skip if we've already expanded this node
        if current in expanded:
            continue

        # Mark as expanded
        expanded[current] = True

        # Stop if we reached the goal
        if current == end:
            break

        # Explore neighboring nodes
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)   # Define neighbor coordinates

            # Ignore neighbor if it is out of bounds
            if neighbor[0] < 0 or neighbor[0] >= width or neighbor[1] < 0 or neighbor[1] >= height:
                continue

            # Ignore neighbor if it is a wall
            if map[neighbor[0], neighbor[1]] == 0:
                continue
            
            new_cost = cost_so_far[current] + 1  # Find cost to reach this neighbor

            # If neighbor is unexplored or cheaper
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost    # Update cost to reach
                priority = new_cost + heuristic(neighbor, end) # Update priority using heuristic

                open.put((priority, neighbor))  # Add neighbor to the queue for consideration
                came_from[neighbor] = current   # Record how the neighbor was reached

                # Add neighbor to frontier if not already expanded
                if neighbor not in expanded and neighbor not in frontier:
                    frontier[neighbor] = True  


                # Remove current node from frontier if it's there
                if current in frontier:
                    del frontier[current]

    # Reconstruct path from end to start
    current = end
    while current is not None:
        path.append(current)    # Add node to path
        current = came_from.get(current)    # Move to previous node

    path.reverse()  # Reverse reversed path to get path

    print("Final path cost:", cost_so_far.get(end, "No path found"))    # Output final cost
   



def visualize_search(save_file="do_not_save.png"):
    """
    :param save_file: (optional) filename to save image to (no filename given means no save file)
    """
    im = Image.open(difficulty_path).convert("RGB")
    pixel_access = im.load()

    # draw start and end pixels
    pixel_access[start[0], start[1]] = NEON_GREEN
    pixel_access[end[0], end[1]] = NEON_GREEN

    # draw expanded pixels
    for pixel in expanded.keys():
        pixel_access[pixel[0], pixel[1]] = DARK_GRAY

    # draw frontier pixels
    for pixel in frontier.keys():
        pixel_access[pixel[0], pixel[1]] = LIGHT_GRAY

    # draw path pixels
    for pixel in path:
        pixel_access[pixel[0], pixel[1]] = PURPLE


    # display and (maybe) save results
    im.show()
    if (save_file != "do_not_save.png"):
        im.save(save_file)

    im.close()

if __name__ == "__main__":
    # Throw Errors && Such
    # global difficulty, start, end
    # assert sys.version_info[0] == 2  # require python 2 (instead of python 3)
    # assert len(sys.argv) == 2, "Incorrect Number of arguments"  # require difficulty input

    # Parse input arguments
    function_name = str(sys.argv[0])
    difficulty_path = str(sys.argv[1])
    difficulty = os.path.basename(difficulty_path)
    print("running " + function_name + " with " + difficulty + " difficulty.")

    # Hard code start and end positions of search for each difficulty level
    if difficulty == "trivial.gif":
        start = (8, 1)
        end = (20, 1)
    elif difficulty == "medium.gif":
        start = (8, 201)
        end = (110, 1)
    elif difficulty == "hard.gif":
        start = (10, 1)
        end = (401, 220)
    elif difficulty == "very_hard.gif":
        start = (1, 324)
        end = (580, 1)
    elif difficulty == "my_maze.gif":
        start = (0, 0)
        end = (500, 205)
    elif difficulty == "my_maze2.gif":
        start = (0, 0)
        end = (599, 350)
    else:
        assert False, "Incorrect difficulty level provided"
    G = 1000000000000000000
    E = 1000000000000000000
    open.put((heuristic(start, end), start))
    came_from[start] = None
    cost_so_far[start] = 0
    # Perform search on given image
    im = Image.open(difficulty_path)
    im = im.convert('1')
    
    pixel_map = im.load()
    width, height = im.size
    search(im.load(), width, height)
    visualize_search("solution.png")