from keras.datasets import mnist
from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout


def learn_MNIST():
    # MNISTを読み込み
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    # 前処理

    # データセットを入力次元784、計60,000個分のベクトルに変換
    x_train = x_train.reshape(60000, 784)
    x_test = x_test.reshape(10000, 784)

    # 画素値を[0, 1]に正規化
    x_train = x_train.astype('float32') / 255
    x_test = x_test.astype('float32') / 255

    # 教師信号をone-hot-encoding
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)

    # ネットワーク生成
    model = Sequential()  # Sequential なモデル
    model.add(Dense(512, activation='relu', input_shape=(784,)))
    model.add(Dropout(0.2))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(10, activation='softmax'))

    model.compile(optimizer='adam',  # 最適化手法
                  loss='categorical_crossentropy',  # 目的(誤差, 損失)関数
                  metrics=['accuracy'])  # 計測は識別率で

    # 学習
    model.fit(x_train, y_train,
              batch_size=100,  # バッチサイズ
              epochs=10,  # 学習回数
              verbose=1)

    loss, accuracy = model.evaluate(x_test, y_test)
    print('Test Accuracy : ', accuracy)

    return model