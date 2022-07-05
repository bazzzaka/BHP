import socket


target_host = '127.0.0.1'
target_port = 9997

# создаем объект сокета
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# отправляем какие-нибудь данные
client.sendto(b'Hello World', (target_host, target_port))

# принимаем данные
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
