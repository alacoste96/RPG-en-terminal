import getopt
import socket
from threading import Thread
import os
import protocols as p
import game as g
import signal

id = 1
games = {}
clients = []


class ClientThread(Thread):
    DIRECTORY = "games"

    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.name = ""
        self.stop = False
        self.player = None
        self.game = None

    @staticmethod
    def menu():
        msg = ''
        msg += 'Welcome to the server. Choose  one of this options:' + '\n'
        msg += '1._ Create game' + '\n'
        msg += '2._ Join game' + '\n'
        msg += '3._ Load game' + '\n'
        msg += '4._ Exit' + '\n'
        return msg

    @staticmethod
    def list_of_availables():   #lista de partidas disponibles
        global games
        games_availables = []
        for game in games.values():
            if len(game.client_sockets) != game.PLAYERS:
                games_availables.append(game.id)
        return games_availables

    @staticmethod
    def list_games():    #lista de partidas disponibles
        global games
        games_availables = ClientThread.list_of_availables()
        msg = ''
        if not games_availables:    #si no hay partidas disponibles
            msg += "There aren't available games currently."
        else:                       #si las hay, preparo el mensaje del cual el cliente elegirá la partida a la que quiere unirse
            msg += '---------------------------------------------' + "\n"
            msg += 'Available games' + "\n"
            msg += '---------------------------------------------' + "\n"
            for game in games.values():
                if len(game.client_sockets) < 2:
                    msg += f'{game.id}._Creator: {game.creator}. Players: {len(game.client_sockets)}/2' + "\n"
            msg += '---------------------------------------------' + "\n"
            msg += 'Choose one game to join: ' + "\n"
        return msg, games_availables

    @staticmethod
    def send_server_message_to_one(text, to):   #enviar un mensaje a un cliente
        message = {'header': p.MSG_SERVER_MSS, 'message': text}
        p.send_one_message(to, message)

    @staticmethod
    def send_server_message_to_all(message, players):   #enviar un mensaje a todos los jugadores de una partida
        for player in players:
            ClientThread.send_server_message_to_one(message, player)

    def send_welcome(self, accepted):    #envía al cliente si puede o no unirse al servidor y el menu de characters en caso afirmativo
        message = {'header': p.MSG_WELCOME, 'menu': ClientThread.menu(), 'accepted': accepted,
                   'options_range': [1, 2, 3, 4]}
        p.send_one_message(self.client_socket, message)

    def manage_welcome(self, message):    #el servidor comprueba si el cliente que solocita unirse puede hacerlo
        self.name = message['name']       #comprobando si su nombre está en la lista de clientes
        global clients
        accepted = True
        if self.name in clients:
            accepted = False
        if accepted:
            print(f'(WELCOME) {self.name} joined the server.')
        else:
            print(f'(Access denied) {self.name} is already playing.')
        self.send_welcome(accepted)

    def create_saved_game(self, message):
        global id, games, clients
        file = os.path.join(ClientThread.DIRECTORY, message['filename'])
        self.game = g.Game(file, None, None, id)
        id += 1
        games[self.game.id] = self.game
        self.game.read_file()
        self.game.players_info[0]["name"] = self.name
        self.game.creator = self.name
        clients.append(self.name)
        self.game.client_sockets.append(self.client_socket)
        ClientThread.send_server_message_to_one('Waiting for more players...', self.client_socket)
        print(f'(LOAD) {self.name} loaded a game')

    def create_new_game(self, message):
        global id, games
        print(f'(CREATE) {self.name} created a game')
        self.game = g.Game(None, message['stages'], self.name, id)
        id += 1
        games[self.game.id] = self.game

    def manage_server_option(self, message):
        option = message['option']
        if option == 1:      #se crea una nueva partida
            self.create_new_game(message)
            message = {'header': p.MSG_CHARACTER_MENU, 'menu': g.Game.display_characters(message['stages']),
                       'options_range': [1, 2, 3, 4]}
            p.send_one_message(self.client_socket, message)
        elif option == 2:     #el cliente se quiere unir a una partida
            mss, options_range = self.list_games()
            message = {'header': p.MSG_LIST_GAMES, 'message': mss, 'options_range': options_range}
            p.send_one_message(self.client_socket, message)
        elif option == 3:     #el cliente quiere cargar una partida
            self.create_saved_game(message)
        else:
            print(f'(EXIT) {self.name} has disconnected.')
            message = {'header': p.MSG_DC_SERVER,
                       'reason': "Disconnected from the server"}
            p.send_one_message(self.client_socket, message)

    def send_player_turn(self):
        msg = f'{self.game.players_info[self.game.turn]["character_name"]} ({self.game.players_info[self.game.turn]["name"]}).'
        message = {'header': p.MSG_YOUR_TURN, 'message': msg, 'options_range': ['a', 's']}
        p.send_one_message(self.game.client_sockets[self.game.turn], message)

    def add_new_player(self, option):
        global id, clients
        if not self.game.file:
            self.game.current_characters.append(self.game.AVAILABLE_CHARACTERS[option - 1]())
            clients.append(self.name)
            self.game.client_sockets.append(self.client_socket)
            self.game.players_info.append({'name': self.name,
                                            'character_name': self.game.current_characters[-1].__class__.__name__,
                                            'alive': True})
        else:
            self.game.players_info[1]["name"] = self.name
            self.game.client_sockets.append(self.client_socket)
            clients.append(self.name)
            ClientThread.send_server_message_to_all(f'The loaded game has a total of {self.game.stages} stages.',
                                                    self.game.client_sockets)
            ClientThread.send_server_message_to_all(self.game.print_current_scenario(), self.game.client_sockets)

    def manage_character_chosen(self, message):
        global id, clients
        option = message['option']
        if len(self.game.current_characters) < self.game.PLAYERS:
            self.add_new_player(option)
            if len(self.game.current_characters) == 1:
                ClientThread.send_server_message_to_one('Waiting for more players...', self.client_socket)
            else:
                print(f"(JOIN) {self.name} joined {self.game.creator}'s game")
                ClientThread.send_server_message_to_all(self.game.print_chosen_ones(), self.game.client_sockets)
                ClientThread.send_server_message_to_all(self.game.print_current_scenario(), self.game.client_sockets)
                self.send_player_turn()
        else:
            print(f'(DC) {self.name} was disconnected.')
            message = {'header': p.MSG_DC_SERVER, 'reason': "Someone has chosen a character faster than you and "
                                                            "the game has started already. Disconnecting."}
            p.send_one_message(self.client_socket, message)

    def manage_new_join(self, message):
        global games, clients
        self.game = games[message['option']]
        if self.game.file:
            self.add_new_player(None)
            print(f"(JOIN) {self.name} joined {self.game.creator}'s game")
            ClientThread.send_server_message_to_all(self.game.print_chosen_ones(), self.game.client_sockets)
            self.send_player_turn()
        else:
            message = {'header': p.MSG_CHARACTER_MENU, 'menu': self.game.display_characters(self.game.stages),
                       'options_range': [1, 2, 3, 4]}
            p.send_one_message(self.client_socket, message)

    def manage_win(self, win, msg):
        message = {'header': p.MSG_END_GAME, 'win': win, 'message': msg}
        for player in self.game.client_sockets:
            p.send_one_message(player, message)
        if win:
            print(f"(GAMEEND) {self.game.players_info[0]['name']}, {self.game.players_info[1]['name']} "
                  f"game ended. They won.")
        else:
            print(f"(GAMEEND) {self.game.players_info[0]['name']}, {self.game.players_info[1]['name']} "
                  f"game ended. They lost.")
        self.delete_game()

    def delete_game(self):
        global clients, games
        if self.game:
            for player in self.game.players_info:
                clients.remove(player['name'])
            del games[self.game.id]

    def save_game(self, message):
        file = os.path.join(ClientThread.DIRECTORY, message['filename'])
        self.game.save_file(file)
        msg = f'{self.name} has saved the game.'
        ClientThread.send_server_message_to_all(msg, self.game.client_sockets)

    def manage_command(self, message):
        if message['action'] == 'a':
            msg, win = self.game.attack_action()
            if win is None:
                ClientThread.send_server_message_to_all(msg, self.game.client_sockets)
                self.send_player_turn()
            else:
                self.manage_win(win, msg)
        else:
            self.save_game(message)
            self.send_player_turn()

    def manage_exit(self):
        global clients, games
        if self.name in clients:
            if not self.game.client_sockets:
                clients.remove(self.name)
            else:
                for index, player in enumerate(self.game.players_info):
                    if self.name != player['name']:
                        message = {'header': p.MSG_DC_SERVER, 'reason': f'{self.name} has disconnected. Game finished'}
                        p.send_one_message(self.game.client_sockets[index], message)
                        print(f'(DC) {player["name"]} was disconnected.')
        self.delete_game()

    def manage_message(self, message):
        header = message['header']
        if header == p.MSG_JOIN:   #un cliente quiere unirse al server
            self.manage_welcome(message)
        elif header == p.MSG_SEND_OPTION:   #tras ser aceptado se le envía las opciones que puede tomar
            self.manage_server_option(message)
        elif header == p.MSG_SEND_CHARACTER:   #se le envía al cliente los caracteres disponibles para que elija
            self.manage_character_chosen(message)
        elif header == p.MSG_SEND_GAME:       #el cliente envía la partida a la que quiere unirse
            self.manage_new_join(message)
        elif header == p.MSG_DC_ME:           #el cliente quiere desconectarse del servidor
            print(f'(EXIT) {self.name} has disconnected.')
            self.manage_exit()
        elif header == p.MSG_SEND_COMMAND:   #el cliente envía un comando, ya sea atacar o guardar partida
            self.manage_command(message)

    def run(self):
        while not self.stop:
            try:
                message = p.recv_one_message(self.client_socket)
                self.manage_message(message)
            except p.ConnectionClosed:
                self.stop = True
            except OSError:
                pass
        self.client_socket.close()


class Server(Thread):
    IP = "127.0.0.1"

    def __init__(self, port):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((Server.IP, port))
        self.socket.listen()

    def run(self):
        ip, port = self.socket.getsockname()
        print(f'Server listening on ({ip}, {port})...')
        while True:
            client_socket, client_address = self.socket.accept()
            print(f'Client from {client_address}')
            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()


def parse_args():
    import sys
    opts, args = getopt.getopt(sys.argv[1:], "p:", ["port="])
    port = 7123
    for o, a in opts:
        if o in ("-p", "--port"):
            port = a
    return port


def check_args(port):
    port_ok = True
    try:
        number = int(port)
        if number <= 1024:
            raise ValueError
    except ValueError:
        port_ok = False
    return port_ok


pid = os.getpid()
try:
    port = parse_args()
    port_ok = check_args(port)
    if port_ok:
        server = Server(int(port))
        server.start()
        stop = False
        while not stop:
            exit = input()
            if exit == '' \
                       '':
                raise KeyboardInterrupt
                stop = True
    else:
        print("The format of the chosen port is incorrect. "
              "You must prive an integer number bigger than 1024")
except getopt.GetoptError:
    print("Invalid arguments")
except KeyboardInterrupt:
    print("Server off. All games have been closed.")
except OSError:
    print("Server off. All games have been closed.")
os.kill(pid, signal.SIGTERM)


