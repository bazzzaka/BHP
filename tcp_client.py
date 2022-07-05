import socket


target_host = 'www.google.com'
target_port = 80

# создаем объект сокета
                        # IPv4              # TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# подключаем клиент
client.connect((target_host, target_port))

# отправляем какие-нибудь данные
client.send(b'GET / HTTP/1.1\r\nHost: google.com \r\n\r\n')

# принимаем какие-нибудь данные
response = client.recv(4096)

print(response.decode())
client.close()
