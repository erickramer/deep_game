from deep_game import app, board
from flask import render_template, jsonify, request

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/board/state')
def state():
    return jsonify(board.state)

@app.route('/board/update', methods=['POST'])
def update():
    name = int(request.form['name'])
    direction = request.form['direction']
    ctrls = [{'name':name, 'direction': direction}]
    board.update(ctrls)
    return jsonify(board.state)

@app.route('/board/dimensions')
def dim():
    return jsonify(board.dimensions)

@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route('/board/reset')
def reset():
    board.reset()
    return jsonify(board.state)
