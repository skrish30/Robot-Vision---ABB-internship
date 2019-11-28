import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

import cv2
import tkinter


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


class Search_path():
    def __init__(self, start, end, row, col):
        self.start = start
        self.end = end
        self.row = row
        self.col = col
        self.maze = None

    def setup_grid(self):
        col = self.col
        row = self.row

        self.maze = [0] * row
        for i in range(col):
            self.maze[i] = [0] * col

    def gen_wall(self, tl, br):
        for j in range(tl[1], br[1] + 1):
            for i in range(tl[0], br[0] + 1):
                self.maze[j][i] = 1

    def shape(self):
        return len(self.maze), len(self.maze[0])

    def move_position(self, current, move):
        i = move[0]
        j = move[1]
        new_position = (current[0] + i, current[1] + j)
        if new_position[0] < 0 or new_position[0] >= len(self.maze) or new_position[1] < 0 or new_position[1] >= len(self.maze):
            return None
        else:
            return new_position

    def display(self, path = None):
        row = self.row
        col = self.col
        maze = self.maze
        fig, ax = plt.subplots(1)
        ax.set_xlim(-0.5, col)
        ax.set_ylim(row, -0.5)
        for i in range(col):
            for j in range(row):
                if maze[i][j] == 1:
                    ax.scatter(i,j, c="red", marker="o")
                else:
                    ax.scatter(i, j, c="green", marker="o")
        if path is not None:
            for i in range(len(path)):
                p = path[i]
                ax.scatter(p[0], p[1], c="blue", marker="*")

            x = []
            y = []

            for p in path:
                x.append(p[0])
                y.append(p[1])
            ax.plot(x, y)

        # Show the major grid lines with dark grey lines
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.show()

    def display_plot(self, path=None):
        root = tkinter.Tk()
        root.wm_title("Path finder using A*")
        row = self.row
        col = self.col
        maze = self.maze

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.set_xlim(-0.5, col)
        ax1.set_ylim(row, -0.5)
        for i in range(col):
            for j in range(row):
                if maze[i][j] == 1:
                    ax1.scatter(i, j, c="red", marker="o")
                else:
                    ax1.scatter(i, j, c="green", marker="o")
        if path is not None:
            for i in range(len(path)):
                p = path[i]
                ax1.scatter(p[0], p[1], c="blue", marker="*")

            x = []
            y = []

            for p in path:
                x.append(p[0])
                y.append(p[1])
            ax1.plot(x, y)

        # # Show the major grid lines with dark grey lines
        # plt.grid(b=True, which='major', color='#666666', linestyle='-')
        # plt.grid(b=True, which='major', color='#666666', linestyle='-')

        canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        def on_key_press(event):
            print("you pressed {}".format(event.key))
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect("key_press_event", on_key_press)

        def _quit():
            root.quit()  # stops mainloop
            root.destroy()  # this is necessary on Windows to prevent
            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        button = tkinter.Button(master=root, text="Next", command=_quit)
        button.pack(side=tkinter.BOTTOM)
        print("plot window")
        tkinter.mainloop()
        # If you put root.destroy() here, it will cause an error if the window is
        # closed with the window manager.

    def astar(self):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""
        start = self.start
        end = self.end
        maze = self.maze

        # Create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)
        # Loop until you find the end
        while len(open_list) > 0:

            # Get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1] # Return reversed path

            LURDMoves = [
                [-1, 0],
                [0, -1],
                [1, 0],
                [0, 1]
            ]

            DiagonalMoves = [
                [-1, -1],
                [1, -1],
                [1, 1],
                [-1, 1]
            ]

            DiagonalBlockers = [
                [0, 1],
                [1, 2],
                [2, 3],
                [3, 0]
            ]
            children = []

            for move in LURDMoves:
                node_position = self.move_position(current_node.position, move)
                if node_position is not None:
                    # Make sure walkable terrain
                    if maze[node_position[0]][node_position[1]] != 0:
                        continue
                    new_node = Node(current_node, node_position)
                    children.append(new_node)

            for num, move in enumerate(DiagonalMoves):
                node_position = self.move_position(current_node.position, move)
                if node_position is not None:
                    # Make sure walkable terrain
                    if maze[node_position[0]][node_position[1]] == 1:
                        continue
                    border = DiagonalBlockers[num]
                    m1 = border[0]
                    m2 = border[1]
                    block1 = self.move_position(current_node.position, LURDMoves[m1])
                    block2 = self.move_position(current_node.position, LURDMoves[m2])
                    if not(maze[block1[0]][block1[1]] == 1 or maze[block2[0]][block1[1]]):
                        new_node = Node(current_node, node_position)
                        children.append(new_node)
            # Loop through children
            for child in children:
                # Child is on the closed list
                for closed_child in closed_list:
                    if child == closed_child:
                        break
                else:
                    # Create the f, g, and h values
                    child.g = current_node.g + 1
                    # H: Manhattan distance to end point
                    child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
                    child.f = child.g + child.h
                    # Child is already in the open list
                    for open_node in open_list:
                        # check if the new path to children is worst or equal
                        # than one already in the open_list (by measuring g)
                        if child == open_node and child.g >= open_node.g:
                            break
                    else:
                        # Add the child to the open list
                        open_list.append(child)


