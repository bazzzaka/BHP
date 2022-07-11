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
    remote_socket.connect((remote_host, remote_port))  # подключение к удаленному узлу

    if receive_first:  # Проверка, что не нужно инициировать соединение
        remote_buffer = receive_from(remote_socket)  # прием соединенного сокета
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
        if len(remote_buffer):
            print('[<==] Received %d bytes from remote.' % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print('[<==] Sent to local host.')
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*] No more data. Closing connections.')
            break


def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    try:                                       # привязываем его к локальному адресу
        server.bind((local_host, local_port))  # начинаем его прослушивать
    except Exception as e:
        print('problem on bind: %r' % e)

        print('[!!] Failed ti listen on %s:%d' % (local_host, local_port))
        print('[!!] Check for other listening socket or '
              'correct permissions')
        sys.exit()
    print('[*] Listening on %s:%d' % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # выводим информацию о локальном соединении
        line = '> Received incoming connection from %s:%d' % (addr[0], addr[1])
        print(line)
        # создаем поток для взаимодействий с удаленным сервером
        proxy_thread = threading.Thread(  # когда приходит запрос
            target=proxy_handler,         # передаём его в новом потоке
            args=(                        # происходит отправка и прием байтов
                client_socket,
                remote_host,
                remote_port,
                receive_first
            )
        )
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print('Usage: ./proxy.py [localhost] [localport]', end='')
        print('[remotehost] [remoteport] [receive_first]')
        print('Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True')
        sys.exit()
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(
        local_host=local_host,
        local_port=local_port,
        remote_host=remote_host,
        remote_port=remote_port,
        receive_first=receive_first
    )


if __name__ == '__main__':
    main()