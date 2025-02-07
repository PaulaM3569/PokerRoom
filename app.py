from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
cards = {}
revealed = False
histories = []
current_story = ""
registered_users = set()

def reset_round():
    global cards, revealed
    cards = {player: "🂠" for player in players}
    revealed = False
    socketio.emit('reset_round', {'players': players, 'cards': cards})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_player', methods=['POST'])
def add_player():
    global players, registered_users
    name = request.json.get('name', '').strip()
    user_id = request.json.get('user_id', '').strip()
    
    if not name or name in players:
        return jsonify(success=False, error="Nombre inválido o duplicado")
    
    if user_id in registered_users:
        return jsonify(success=False, error="Cada usuario solo puede agregar un jugador")
    
    players[name] = "?"
    cards[name] = "🂠"
    registered_users.add(user_id)
    socketio.emit('update_players', {'players': players, 'cards': cards})
    socketio.emit('show_game')
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
    global revealed, current_story, histories
    revealed = True
    story = request.json.get('classification', '')
    histories.append({"story": story, "cards": players.copy()})
    current_story = story
    socketio.emit('reveal_cards', {'classification': story, 'cards': players})
    return jsonify(success=True)

@app.route('/add_story', methods=['POST'])
def add_story():
    global current_story
    story = request.json.get('story', '').strip()
    if story:
        current_story = story
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/reset_round', methods=['POST'])
def reset():
    reset_round()
    return jsonify(success=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
