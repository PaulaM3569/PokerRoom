from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
cards = {}
revealed = False
classification = ""
registered_users = set()  # Para rastrear quién ya ha agregado un jugador

def reset_game():
    global players, cards, revealed, classification, registered_users
    players.clear()
    cards.clear()
    revealed = False
    classification = ""
    registered_users.clear()
    socketio.emit('reset_game')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_player', methods=['POST'])
def add_player():
    global players, registered_users
    name = request.json.get('name', '').strip()
    user_id = request.json.get('user_id', '').strip()  # Se espera un identificador único del usuario
    
    if not name or name in players:
        return jsonify(success=False, error="Nombre inválido o duplicado")
    
    if user_id in registered_users:
        return jsonify(success=False, error="Cada usuario solo puede agregar un jugador")
    
    players[name] = "?"
    cards[name] = "🂠"
    registered_users.add(user_id)
    socketio.emit('update_players', {'players': players, 'cards': cards})
    socketio.emit('show_game')  # Emitir evento para mostrar el resto del juego
    return jsonify(success=True)

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

@app.route('/reset_game', methods=['POST'])
def reset():
    reset_game()
    return jsonify(success=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
