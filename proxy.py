import sys
import socket
import threading


HEX_FILTER = ''.join(  # строка с печатными символами ASCII если символ не печатный
    [len(repr(chr(i)) == 3) and chr(i) or '.' for i in range(256)]  # выводится точка (.)
)


# принимает ввод в виде байтов и выводит в консоль в виде 16-ичном формате
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()  # декодируем строку байтов
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])  # берем часть строки и присваиваем её переменной
        # подставление вместо каждой необработанной строки
        printable = word.translate(HEX_FILTER)  # его строковое представление
        hexa = '.'.join([f'{ord(c):02X}' for c in word])  # подставляем шест. представление целочисленного знач
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')  # массив из шестн. знач. слова индекса первого байта
        # шест. знач слова и его печчатное представление
    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    buffer = b''  # здесь будут накапливаться ответы полученные из сокета
    connection.settimeout(5)  # время ожидания
    try:
        while True:  # цикл для записи ответных данных
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer  # возврат байтовой строки


###
def request_handler(buffer):
    # модифицируем пакет
    return buffer
# Внутри этих функций можно изменять содержимое пакетов, заниматься
# фаззингом, отлаживать проблемы с аутентификацией — делать все, что вам
# угодно. Это может пригодиться, к примеру, если вы обнаружили передачу
# учетных данных в открытом виде и хотите попробовать повысить свои при-
# вилегии в ходе работы с приложением, передав ему admin вместо собственного
# имени пользователя.


def response_handler(buffer):
    # модифицируем пакет
    return buffer
###


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)

    if len(remote_buffer):
        print('[<==] Sending %d bytes to localhost.' % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = '[<==] Received %d bytes from local host.' % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print('[<==] Sent to remote')

        remote_buffer = receive_from(remote_socket)
###########################################
# Tomorrow