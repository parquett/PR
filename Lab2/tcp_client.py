import socket

def connect_to_server(command):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send(command.encode('utf-8'))
    response = client.recv(1024).decode('utf-8')
    print("Server response:", response)
    client.close()

connect_to_server('write Hello, this is a test message!')
connect_to_server('read')
