from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
cards = {}
revealed = False
classification = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_player', methods=['POST'])
def add_player():
    global players
    name = request.json.get('name', '').strip()
    if name and name not in players:
        players[name] = "?"
        cards[name] = "🂠"
        socketio.emit('update_players', {'players': players, 'cards': cards})
        return jsonify(success=True)
    return jsonify(success=False, error="Nombre inválido o duplicado")

@app.route('/set_card', methods=['POST'])
def set_card():
    global players, cards, revealed
    if not revealed:
        name = request.json.get('name')
        card = request.json.get('card')
        if name in players:
            players[name] = card
            cards[name] = "🂠"
            socketio.emit('update_cards', {'cards': cards})
            return jsonify(success=True)
    return jsonify(success=False)

@app.route('/reveal_cards', methods=['POST'])
def reveal_cards():
    global revealed, classification
    revealed = True
    classification = request.json.get('classification', '')
    socketio.emit('reveal_cards', {'classification': classification, 'cards': players})
    return jsonify(success=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
