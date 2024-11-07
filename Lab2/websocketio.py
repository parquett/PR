import json
from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["https://piehost.com"])

rooms = {}


def parse_data(data):
    # convert data from string to a dictionary
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print("Failed to parse JSON data")
            return None
    return data


@socketio.on('join')
def handle_join(data):
    data = parse_data(data)
    if data is None:
        return

    username = data.get('username')
    room = data.get('room')

    # Prevent the same user from joining the room multiple times
    if room not in rooms:
        rooms[room] = []
    if username in rooms[room]:
        send(f"{username} is already in the room {room}.", to=room)
        return

    join_room(room)
    rooms[room].append(username)

    send(f"{username} has joined the room {room}.", to=room)



@socketio.on('leave')
def handle_leave(data):
    data = parse_data(data)
    if data is None:
        return

    username = data.get('username')
    room = data.get('room')

    # Only proceed if the user is in the room
    if room in rooms and username in rooms[room]:
        send(f"{username} has left the room {room}.", to=room)
        rooms[room].remove(username)
        leave_room(room)
    else:
        send(f"{username} is not in the room {room}.", to=request.sid)

@socketio.on('message')
def handle_message(data):
    data = parse_data(data)
    if data is None:
        return

    room = data.get('room')
    msg = data.get('message')
    username = data.get('username')

    send(f"{username}: {msg}", to=room)


# Run the server
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)

# Event: join, Payload: { "username": "Alice", "room": "general" }
# Event: message, Payload: { "username": "Alice", "room": "general", "message": "Hello everyone!" }
# Event: leave, Payload: { "username": "Alice", "room": "general" }


