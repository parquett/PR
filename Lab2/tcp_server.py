import socket
import threading
from threading import Lock

FILE_PATH = 'shared_file.txt'
file_lock = Lock()

def handle_client(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        # Interpret message as a command
        command, *data = message.split()
        if command.lower() == 'write':
            data_to_write = ' '.join(data)
            with file_lock:  # Ensure safe write access to file
                with open(FILE_PATH, 'a') as file:
                    file.write(f'{data_to_write}\n')
                client_socket.send(f'Written to file: {data_to_write}\n'.encode('utf-8'))
        elif command.lower() == 'read':
            with file_lock:  # Ensure safe read access to file
                with open(FILE_PATH, 'r') as file:
                    content = file.read()
                client_socket.send(f'File content:\n{content}\n'.encode('utf-8'))
        else:
            client_socket.send(f'Unknown command: {command}\n'.encode('utf-8'))

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print('Server listening on port 12345...')

    while True:
        client_socket, addr = server.accept()
        print(f'Accepted connection from {addr}')

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start the server
if __name__ == '__main__':
    start_server()
