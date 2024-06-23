import getopt
import protocols as p
import socket


class Client:

    def __init__(self, stages, name, server_ip, server_port):
        self.stages = stages
        self.name = name
        self.server_ip = server_ip
        self.server_port = server_port
        self.stop = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, int(server_port)))

    @staticmethod
    def choose_one_option(message):
        exit = False
        while not exit:
            try:
                option = int(input('Your option: '))
                if option in message['options_range']:
                    exit = True
                else:
                    raise ValueError
            except ValueError:
                print(f'Try again. 1 Integer number of these: {message["options_range"]}')
        return option

    @staticmethod
    def ask_filename_for_loading():
        valid = False
        while not valid:
                filename = input('Enter the name of the file: ')
                if not filename.endswith('.json') and not filename.endswith('.txt'):
                    print('Format incorrect. The filename must end with .txt or .json')
                else:
                    valid = True
        return filename

    @staticmethod
    def ask_filename_for_saving(filename, cancel):
        valid = False
        while not valid:
            filename = input("Enter a name for the file: ")
            if not filename.endswith('.json') and not filename.endswith('.txt'):
                if filename == 'cancel':
                    cancel = True
                    valid = True
                    print('The game was not saved')
                else:
                    print('Format incorrect. The filename must end with .txt or .json')
            else:
                valid = True
        return filename, cancel

    def manage_welcome(self, message):
        if message['accepted']:
            print(message['menu'])
            option = self.choose_one_option(message)
            if option == 3:
                filename = Client.ask_filename_for_loading()
                message = {'header': p.MSG_SEND_OPTION, 'option': option, 'filename': filename}
                p.send_one_message(self.client_socket, message)
            else:
                message = {'header': p.MSG_SEND_OPTION, 'option': option, 'stages': self.stages}
                p.send_one_message(self.client_socket, message)
        else:
            print(f'Access denied. There is someone called {self.name} playing.')
            self.stop = True

    def choose_character(self, message, client_socket):
        print(message['menu'])
        option = self.choose_one_option(message)
        message = {'header': p.MSG_SEND_CHARACTER, 'option': option}
        p.send_one_message(client_socket, message)

    def send_join(self):
        message = {'header': p.MSG_JOIN, 'name': self.name}
        p.send_one_message(self.client_socket, message)

    def command(self):
        valid = False
        cancel_save = False
        filename = None
        while not valid:
            option = input('What do you want to do? ')
            if option == 'a':
                valid = True
            elif option == 's':
                filename, cancel_save = Client.ask_filename_for_saving(filename, cancel_save)
                if not cancel_save:
                    valid = True
            else:
                print('Invalid command. Try again (a or s)')
        message = {'header': p.MSG_SEND_COMMAND, 'action': option, 'filename': filename}
        p.send_one_message(self.client_socket, message)

    def manage_end_game(self, message):
        print(message['message'])
        if message['win']:
            print('Congratulations, You won the game!')
        else:
            print('You lost the game. Try again')
        self.stop = True

    def manage_choose_game(self, message):
        print(message['message'])
        if message['options_range']:
            option = self.choose_one_option(message)
            message = {'header': p.MSG_SEND_GAME, 'option': option}
            p.send_one_message(self.client_socket, message)
        else:
            message = {'header': p.MSG_DC_ME}
            p.send_one_message(self.client_socket, message)
            self.stop = True

    def manage_message(self, message):
        header = message['header']
        if header == p.MSG_WELCOME:
            self.manage_welcome(message)
        elif header == p.MSG_CHARACTER_MENU:
            self.choose_character(message, self.client_socket)
        elif header == p.MSG_SERVER_MSS:
            print(message['message'])
        elif header == p.MSG_LIST_GAMES:
            self.manage_choose_game(message)
        elif header == p.MSG_YOUR_TURN:
            print(message['message'], end=' ')
            self.command()
        elif header == p.MSG_DC_SERVER:
            print(message['reason'])
            self.stop = True
        elif header == p.MSG_END_GAME:
            self.manage_end_game(message)

    def start(self):
        try:
            self.send_join()
            while not self.stop:
                message = p.recv_one_message(self.client_socket)
                self.manage_message(message)
            self.client_socket.close()
        except KeyboardInterrupt:
            print('Disconnection success.')
            message = {'header': p.MSG_DC_ME }
            p.send_one_message(self.client_socket, message)
        except p.ConnectionClosed as e:
            print(e)


def parse_args():
    import sys
    opts, args = getopt.getopt(sys.argv[1:], "s:n:i:p:", ["stages=", "name=", "ip=", "port="])
    name = None
    stages = 1
    ip = '127.0.0.1'
    port = 7123
    for o, a in opts:
        if o in ("-n", "--name"):
            name = a
        elif o in ("-s", "--stages"):
            stages = a
        elif o in ("-i", "--ip"):
            ip = a
        elif o in ("-p", "--port"):
            port = a
    return name, stages, ip, port


def check_args(stages, port, name):
    stages_ok = True
    port_ok = True
    name_ok = False
    try:
        number = int(port)
        if number <= 1024:
            raise ValueError
    except ValueError:
            port_ok = False
    try:
        number = int(stages)
        if number < 1 or number > 10:
            raise ValueError
    except ValueError:
        stages_ok = False
    if name is not None or "":
        name_ok =True
    return stages_ok, port_ok, name_ok


try:
    name, stages, ip, port = parse_args()
    stages_ok, port_ok, name_ok = check_args(stages, port, name)
    if stages_ok and port_ok and name_ok:
        client = Client(int(stages), name, ip, int(port))
        client.start()
    else:
        if not stages_ok:
            print('Access Denied. Argument Stages(-s) must be an integer between 1-10.')
        if not port_ok:
            print('Access Denied. Argument Port(-p) must be an integer bigger than 1024.')
        if not name_ok:
            print("Access Denied. You must provide a Name(-n), it can't be None")
except TimeoutError:
    print('Invalid IP')
except OSError:
    print('The server is closed')
except getopt.GetoptError:
    print("Invalid arguments")
except BrokenPipeError:
    print('The server is closed')
