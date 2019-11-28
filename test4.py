import tkinter as tk

class radio():
    def __init__(self, i, root, GRID_SIZE, START_ROW):
        self.var = tk.IntVar(value=0)
        self.label = tk.Label(root)
        self.label.grid(row=GRID_SIZE + 1 + START_ROW, column=i)
        self.selection = None

    def func(self):
        self.selection = str(self.var.get())
        self.label.config(text=self.selection)

class radio_button():
    def __init__(self, GRID_SIZE):
        self.root = tk.Tk()
        self.GRID_SIZE = GRID_SIZE
        self.ROW= GRID_SIZE
        self.COL = 2
        self.START_ROW = 2
        self.radio_group = []
        self.btn_send = tk.Button(self.root, text="Send")
        self.draw()

    def draw(self):
        start = tk.Label(self.root, text ="Start")
        sx = tk.Label(self.root, text ="x")
        sy = tk.Label(self.root, text ="y")
        start.grid(row=0, column=0, columnspan=3)
        sx.grid(row=1, column=1)
        sy.grid(row=1, column=2)

        end = tk.Label(self.root, text ="End")
        ex = tk.Label(self.root, text ="x")
        ey = tk.Label(self.root, text ="y")
        end.grid(row=0, column=3, columnspan=3)
        ex.grid(row=1, column=3)
        ey.grid(row=1, column=4)

        for c in range(1, 5):
            Radio = radio(c, self.root, self.GRID_SIZE, self.START_ROW)
            self.radio_group.append(Radio)
            for r in range(1, self.ROW+1):
                btn = tk.Radiobutton(self.root, text=str(r-1), variable=Radio.var, value=r-1, width=10, command=Radio.func)
                btn.grid(row=r + self.START_ROW, column=c)
        self.btn_send.grid(row=self.START_ROW+self.GRID_SIZE +2, column=1, columnspan=4)




