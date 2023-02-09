import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # for removing unnecessary warnings
from absl import logging
logging._warn_preinit_stderr = 0
logging.warning('...')
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import itertools
from numpy import array
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv1D, MaxPooling1D, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import tensorflow as tf
from load_data_30_turn import load_data, load_test_data
import time
import joblib
import pickle

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    #print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


t11, f12, f13, f21, t22, f23, f31, f32, t33 = 0, 0, 0, 0, 0, 0, 0, 0, 0
acc = 0

# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
features = ['cog']
dim = len(features)
timesteps = 60 # number of sequences per batch
CLASSES = 2

data_normal, Y_data = load_data(timesteps, dim, features, CLASSES)


nr_iter = 1
train_time, test_time = 0, 0
    #print('dataset is labeled')
for val in range(nr_iter):
    np.random.seed(val)
    data_train, data_test, target_train, target_test = train_test_split(data_normal, Y_data, test_size=0.30)

    #cross_validate_data = data_test
    # # data pre-processing
    # scaler = MinMaxScaler(0, 1) #
    # # Fit only to the training data
    # scaler.fit(data_train)
    # # apply the transformations to the data:
    # data_train = scaler.transform(data_train)
    #
    # #scaler.fit(data_test) #test on real data without scaling
    # data_test = scaler.transform(data_test)

    data_train.shape = (data_train.shape[0], timesteps, dim)
    data_test.shape = (data_test.shape[0], timesteps , dim)
    # target_train.shape = (target_train.shape[0],timesteps, dim)
    start_time = time.time()

    # define model
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=dim, activation='relu', input_shape=(timesteps, dim)))
    #model.add(Conv1D(filters=64, kernel_size=dim, activation='relu'))
    model.add(Dropout(0.5))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(dim, activation='softmax'))
    model.compile(optimizer='adam', loss='mse')
    # Fit the data
    model.fit(data_train, target_train, epochs=200, verbose=2)
    _, accuracy = model.evaluate(data_train, target_train,  verbose=2)
    print("training accuracy= ", accuracy)
    train_time += (time.time() - start_time) * 1000 / data_train.shape[0]

    start_time = time.time()
    # Predict the response

    pred = model.predict(data_test)
    test_time += (time.time() - start_time) * 1000 / data_test.shape[0]
    # pred2 = clf.predict_proba(data_test[0:1,:])

 #   acc += accuracy_score(target_test, pred)

    # print('total number of validated anomaly samples is ', sum(target_test==[0, 0, 1])[2])
    # print('total number of validated normal samples is ', sum(target_test==[1, 0, 0])[0])

    # cm = confusion_matrix(target_test.argmax(axis=1), pred.argmax(axis=1))
    # cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    # print('confusion matrix : \n',cm)
    # cnf_matrix = confusion_matrix(target_test.argmax(axis=1), pred.argmax(axis=1))
    # print('classification_report : \n', classification_report(y_test,pred))

    r11, r12, r21, r22 = confusion_matrix(target_test.argmax(axis=1), pred.argmax(axis=1)).ravel()
    t11 += r11
    f12 += r12
    f21 += r21
    t22 += r22

    print("Completed run ", val)


print(">>>>>>>>>>>>>>>>>>>>>>>>> \n accuracy : ", acc / nr_iter)
cm = np.reshape(np.array([t11, f12, f21, t22]), (2, 2))
# print(cm)

# cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
print(cm)
# plot_confusion_matrix(cm, ['normal', 'anomaly'], normalize=False, title='Confusion matrix')
# plt.show()

# save the model to disk
# filename = 'CNN_30_turn_rostock.h5'
# joblib.dump(model, filename)


print('train time per 1000 samples= ', train_time / nr_iter)
print('test time per 1000 samples= ', test_time / nr_iter)