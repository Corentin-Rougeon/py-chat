import flask
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

connected_players = {}
player_names = []

chat_log = []


def check_username(username):
    check = False
    tempName = username
    n = 0

    while not check:
        if tempName not in connected_players.values():
            check = True
        else:
            n += 1
        print(n)
        if n > 0:
            tempName = f"{username}({n})"


    return tempName

@app.route("/")
def hello_world():
    return flask.render_template("index.html")

@socketio.on("connect")
def connect():
    emit("users_update", list(connected_players.values()))
    emit("chat_update", chat_log)


@socketio.on('disconnect')
def disconnect():
    sid = vars(request)["sid"]

    chat_log.append({"user": "system", "message": f"'{connected_players[sid]}' has left"})
    del connected_players[sid]
    emit("chat_update", chat_log, broadcast=True)


    emit("users_update", list(connected_players.values()), broadcast=True)



@socketio.on("send_message")
def send_message(data):
    sid = vars(request)["sid"]

    chat_log.append({"user":connected_players[sid],"message":data["message"]})
    emit("chat_update", chat_log,broadcast=True)

@socketio.on('connect_user')
def handle_my_custom_event(json):
    sid = vars(request)["sid"]

    if sid not in connected_players.keys():
        connected_players[sid] = check_username(json["name"])
        emit("connected", connected_players[sid])
        emit("users_update", list(connected_players.values()), broadcast=True)
        chat_log.append({"user":"system","message":f"'{connected_players[sid]}' has joined"})
        emit("chat_update",chat_log,broadcast=True)
    else:
        emit("already_connected",connected_players[sid])

    return "test"

if __name__ == '__main__':
    socketio.run(app,allow_unsafe_werkzeug=True,host="0.0.0.0",port=80)

