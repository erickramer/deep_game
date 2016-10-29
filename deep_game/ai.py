import keras
from keras.layers import *
from keras.models import *
from keras.utils.np_utils import to_categorical

class AI(object):

    def __init__(self, board, path=None, batch_size=20):
        self._board = board
        self._actions = ['', 'left', 'right', 'up', 'down']

        self._build_model(path)
        self._history = []
        self._final_scores = []

    def _build_model(self, path):

        if path is None:
            state = Input(shape=(3,21,2))
            action = Input(shape=(5,))

            x = Flatten()(state)
            x = Dense(100, activation="relu")(x)
            x = Dense(100, activation="relu")(x)
            x = Dropout(0.5)(x)
            q = Dense(1, activation="relu")(x)

            self._model = Model([state, action], q)
            self._model.compile(loss="mae", optimizer="SGD")
        else:
            self._model = keras.load_model(path)

    @property
    def state(self):
        state = self._board.state
        x = np.zeros((21,2))
        points = state['circles'] + state['dots'] + state['triangles']
        for i, p in enumerate(points):
            x[i, 0] = p['x']
            x[i, 1] = p['y']
        return x

    def max_q(self, state):
        actions = np.identity(5)
        state_dup = np.stack([state]*5) # replicate 5 times for 5 actions

        p = self._model.predict([state_dup, actions])
        return np.argmax(p), np.max(p)

    def take_action(self, action):
        old_score = self._board.state['score']
        ctrls = [{'name': 0, 'direction': self._actions[action]}]
        self._board.update(ctrls)
        return self._board.state['score'] - old_score

    def _train_minibatch(self):
        nb_states = len(self._history) - 1
        inds = np.random.choice(nb_states, 20)

        states = []
        actions = []
        max_qs = []
        for i in inds:
            state, action, reward, alive = self._history[i]
            states.append(state)
            actions.append(action)

            if alive:
                state_1 = self._history[i+1][0]
                _, q = self.max_q(state_1)
                max_qs.append(reward + 0.97*q)
            else:
                max_qs.append(reward)

        x = [np.stack(states), to_categorical(np.stack(actions), 5)]
        y = np.stack(max_qs)

        self._model.train_on_batch(x, y)




    def play_game(self, epsilon=0.1, train=True):
        self._board.reset()

        # initialize
        states = []
        states.append(self.state)
        self.take_action(0)
        states.append(self.state)
        self.take_action(0)
        states.append(self.state)

        count = 0
        while self._board.alive:
            count += 1
            action = None
            state = np.stack(states)
            # print state.shape
            if np.random.rand() < epsilon:
                action = np.random.choice(5)
            else:
                action, _ = self.max_q(state)

            reward = self.take_action(action)
            self._history.append((state, action, reward, self._board.alive))

            if train and count % 10 == 0:
                self._train_minibatch()

            # handle sliding window
            states.append(self.state)
            states = states[1:]

    def play_games(self, nb_games=1e4, flush=100):
        for i in range(int(nb_games)):
            self.play_game()
            self._final_scores.append(self._board.state['score'])

            if i % flush == 0 and i > 0:
                print "Mean score: ",
                print np.mean(self._final_scores[(i-100):i]),
                print "-- %i games completed" % i
                #self._history = []
