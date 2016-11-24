from qlearning4k.games.game import Game
from qlearning4k.agent import Agent
import numpy as np

class DotGame(Game):

    def __init__(self, board):
        self._board = board
        self._board.reset()

        self._actions = ['', 'left', 'right', 'up', 'down']

    @property
    def name(self):
    	return "Game"

    @property
    def nb_actions(self):
    	return 5

    def reset(self):
    	self._board.reset()

    def play(self, action):
        ctrls = [{'name': 0, 'direction': self._actions[action]}]
        self._board.update(ctrls)

    def get_state(self):
        state = self._board.state
        x = np.zeros((21,2))
        points = state['circles'] + state['dots'] + state['triangles']
        for i, p in enumerate(points):
            x[i, 0] = p['x']
            x[i, 1] = p['y']
        return x / 600.

    def get_score(self):
        if self._board.scored:
            return 1.0
        else:
            return 0.0

    def is_over(self):
    	return not self._board.state['alive']

    def get_possible_actions(self):
    	return range(self.nb_actions)

    def is_won(self):
        return self._board.won

class DotAgent(Agent):

    def train(self, game, nb_epoch=1000, batch_size=50, gamma=0.9, epsilon=[1., .1], epsilon_rate=0.5, reset_memory=False, observe=0, checkpoint=None):

        f = None
        if hasattr(self, 'log_file'):
            f = open(self.log_file, "w")

        self.check_game_compatibility(game)
        if type(epsilon)  in {tuple, list}:
            delta =  ((epsilon[0] - epsilon[1]) / (nb_epoch * epsilon_rate))
            final_epsilon = epsilon[1]
            epsilon = epsilon[0]
        else:
            final_epsilon = epsilon
        model = self.model
        nb_actions = model.output_shape[-1]
        win_count = 0
        scores = []
        for epoch in range(nb_epoch):
            loss = 0.
            game.reset()
            self.clear_frames()
            if reset_memory:
                self.reset_memory()
            game_over = False
            S = self.get_game_data(game)
            while not game_over:
                if np.random.random() < epsilon or epoch < observe:
                    a = int(np.random.randint(game.nb_actions))
                else:
                    q = model.predict(S)
                    a = int(np.argmax(q[0]))
                    #print a
                game.play(a)
                r = game.get_score()
                S_prime = self.get_game_data(game)
                game_over = game.is_over()
                if game_over:
                    scores.append(game._board.score)
                transition = [S, a, r, S_prime, game_over]
                self.memory.remember(*transition)
                S = S_prime
                if epoch >= observe:
                    batch = self.memory.get_batch(model=model, batch_size=batch_size, gamma=gamma)
                    if batch:
                        inputs, targets = batch
                        # print targets[0, :]
                        loss += float(model.train_on_batch(inputs, targets))
                if checkpoint and ((epoch + 1 - observe) % checkpoint == 0 or epoch + 1 == nb_epoch):
                    model.save_weights('weights.dat')
            if game.is_won():
                win_count += 1
            if epsilon > final_epsilon and epoch >= observe:
                epsilon -= delta
            if (epoch + 1) % 50 == 0:
                status = "Epoch {:03d}/{:03d} | Loss {:.4f} | Epsilon {:.2f} | Win count {}".format(epoch + 1, nb_epoch, loss, epsilon, win_count)
                status += "\n"
                status += "\tScores -- Mean: %i Median: %i Min: %i Max: %i"  % (int(np.mean(scores)), int(np.median(scores)), int(np.min(scores)), int(np.max(scores)))
                status += "\n"
                if f is not None:
                    f.write(status)
                else:
                    print status
                scores = []
