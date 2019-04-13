#%%
import tensorflow as tf 
import pandas as pd 

#데이터 불러옴
iris_data = pd.read_csv(".\\data\\Iris.csv")
iris_data.head()

#품종 column을 one-hot-encode
iris_data_one_hot_encoded = pd.get_dummies(iris_data)
iris_data_one_hot_encoded.head()

#전체 데이터를 80%은 트레이닝 20% 테스트로 쪼갬
iris_train_data = iris_data_one_hot_encoded.sample(frac=0.8, random_state=200)
iris_test_data = iris_data_one_hot_encoded.drop(iris_train_data.index)

#input은 꽃잎의 너비와길이, 꽃받침의 너비와길이
#output은 세개중 하나로
iris_train_input_data = iris_train_data.filter(['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
iris_train_label_data = iris_train_data.filter(['Species_Iris-setosa', 'Species_Iris-versicolor', 'Species_Iris-virginica'])

#x는 input값을 위한 placeholder
#w는 가중치
#b는 편차
#y는 트레이닝해서 나온 결과(가설)
#y_는 진짜 결과값
x = tf.placeholder(tf.float32,[None, 4])
W = tf.Variable(tf.zeros([4, 3]))
b = tf.Variable(tf.zeros([3]))
y = tf.nn.softmax(tf.matmul(x, W) + b)
y_ = tf.placeholder(tf.float32, [None, 3])

#cross_entropy를 cost함수로
cross_entropy  = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(tf.matmul(x, W) + b, y_))
#cost를 최소화
train_step = tf.train.GradientDescentOptimizer(0.05).minimize(cross_entropy)

sess = tf.InteractiveSession()

#1000번학습
tf.global_variables_initializer().run()
for _ in range(1000):
    #Usually send batches to the training step. But since the dataset is small sending all
    sess.run(train_step, feed_dict={x: iris_train_input_data, y_: iris_train_label_data})

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

#정확도
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

print('Accuracy : ', sess.run(accuracy, feed_dict={x: iris_test_input_data, y_: iris_test_label_data}))