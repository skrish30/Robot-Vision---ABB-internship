import socket
import time

class socket_comm:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.path = None
        self.message = []

    def format_path(self, oldpath):
        # format of path[(0, 0), (1, 1), (2, 2), (2, 3), (3, 4), (4, 4)]
        path = []

        for i, p in enumerate(oldpath, start=1):
            path.append([p[0], p[1]])
            if i % 8 == 0:
                path = str(path)
                self.message.append(path)
                path = []
        if path == []:
            return self.message
        pathLength = len(path)
        path = str(path)
        path = path[slice(1, -1)]
        path = path + ("," + str([0, 0])) * (8 - pathLength)
        path = '[' + path + ']'
        self.message.append(path)
        return self.message

    def send_path(self, Path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, self.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                data = conn.recv(1024)
                print(f'client:{data}')
                conn.sendall(b'Connected')
                print('Connected')
                time.sleep(3)
                conn.sendall(b's')
                print('start')

                while True:
                    data = conn.recv(1024)
                    print(f'client: {data}')
                    if data == b's':
                        break

                #Test sending path to Robot using socket
                # Path = [[0,0],[1,0],[2,0],[3,0],[3,1],[3,2],[4,3],[5,4]]
                # Path = [[0, 0], [1, 1], [2, 1], [3, 1], [4, 2], [4, 3], [4, 4]]
                self.format_path(Path)
                conn.sendall(bytes(self.message[0], 'utf8'))
                print(f'message1: {self.message[0]}')
                print(f'message length:{len(self.message)}')
                if len(self.message) > 1:
                    conn.sendall(bytes(self.message[1], 'utf8'))
                    print(f'message2: {self.message[1]}')
                else:
                    val = str([[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
                    conn.sendall(bytes(val, 'utf8'))
                    print(f'message2: {val}')
                print('sent Path')


