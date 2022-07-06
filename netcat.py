import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


class NetCat:
    def __init__(self, args, buffer=None):  # Инициализация с помощью командной строки буфера
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создание объекта сокета
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()  # если нам нужно подготовить слушателя
        else:
            self.send()  # если слушателя подготавливать не придется

    def send(self):
        self.socket.connect((self.args.target, self.args.port))  # подключаемся к серверу с заданным портом
        if self.buffer:                                          # с передачей буфера
            self.socket.send(self.buffer)

        try:  # используем этот блок чтобы соединение можно было закрыть Ctrl+C
            while True:  # цикл для получения данных от целевого сервера
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break  # если данных больше нет выходим из цикла
                    if response:
                        print(response)                          # в противном случае выводим ответ
                        buffer_input = input('>')                # останавливаемся, чтобы получить интерактивный ввод
                        buffer_input += '\n'                     # отправляем его и продолжаем цикл
                        self.socket.send(buffer_input.encode())  #
        except KeyboardInterrupt:  # цикл будет работать пока не произойдет исключение (Ctrl+C)
            print('User terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle,
                args=(client_socket,)
            )
            client_thread.start()

              
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(
        shlex.split(cmd),  # исполнение команды в локальной операционной системе
        stderr=subprocess.STDOUT  # предоставление аргументов для загрузки файлов
    )                             # выполнение команд или запуска командной оболчки
    return output.decode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(  # создание интерфейса командной строки
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # справка о применении, которая выведется при запуске с командой --help
        # |-с| подготавливает интерактивную командную оболочку
        # |-е| выполняет отдельно взятую команду
        # |-l| говорит о том что нужно подготовить слушателя
        # |-p| позволяет указать порт на котором будет происходить взаимодействие
        # |-t| задает IP адрес
        # |-u| определяет имя файла который нужно загрузить
        epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -1 -c #командная оболочка
        netcat.py -t 192.168.1.108 -p 5555 -1 -u=mytest.txt 
        # загружаем файл
        netcat.py -t 192.168.1.108 -p 5555 -1 -e=\"cat /etc/passwd\"
        # выполняем команду 
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135
        # шлем текст на порт сервера 135
        netcat.py -t 192.168.1.108 -p 5555 # соединяемся с сервером  
        '''))
    parser.add_argument(
        '-c',
        '--command',
        action='command shell'
    )
    parser.add_argument(
        '-e',
        '--execute',
        help='execute specified command'
    )
    parser.add_argument(
        '-l',
        '--listen',
        action='store_true',
        help='listen'
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=5555,
        help='specified port'
    )
    parser.add_argument(
        '-t',
        '--target',
        default='192.168.1.203',
        help='specified IP'
    )
    parser.add_argument(
        '-u',
        '--upload',
        help='upload file'
    )
    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())  # если программа используется в качестве слушателя
    nc.run()
