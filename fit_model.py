from keras.models import Sequential
from keras.layers import Dense, Flatten, Input, Reshape, Convolution1D
from keras.optimizers import sgd
from qlearning4k.games import Catch
from qlearning4k import Agent
from deep_game.game import DotGame, DotAgent
from deep_game.models import Board
from multiprocessing import Pool
from contextlib import closing

def fit_model(data):

    i, gamma, log_file = data

    board = Board()

    game = DotGame(board)

    nb_frame = 3
    hidden_size = 100

    model = Sequential()
    model.add(Flatten(input_shape=(nb_frame,21,2)))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(5, activation="linear"))

    model.compile(optimizer="Adagrad", loss="mae")

    agent = DotAgent(model)
    agent.log_file = log_file

    for j in range(10):
        agent.train(game, nb_epoch=1000, gamma=0.99, batch_size=200)
        model.save("./data/model_%i_%i.h5" % (i,j))


if __name__ == "__main__":
    f = ((1, 0.9, "log1"), (2, 0.99, "log2"), (3, 0.999, "log3"))
    map(fit_model, f)
