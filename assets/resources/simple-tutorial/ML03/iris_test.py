#%%
import tensorflow as tf 
import pandas as pd 

iris_data = pd.read_csv("C:\\Users\\SeungYeonLee\\Documents\\GitHub\\GRuuuuu.github.io\\assets\\resources\\simple-tutorial\\ML03\\data\\Iris.csv")

iris_data.head()

iris_data_one_hot_encoded = pd.get_dummies(iris_data)

iris_data_one_hot_encoded.head()

iris_train_data = iris_data_one_hot_encoded.sample(frac=0.8, random_state=200)
iris_test_data = iris_data_one_hot_encoded.drop(iris_train_data.index)

iris_train_input_data = iris_train_data.filter(['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
iris_train_label_data = iris_train_data.filter(['Species_Iris-setosa', 'Species_Iris-versicolor', 'Species_Iris-virginica'])
iris_test_input_data = iris_test_data.filter(['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
iris_test_label_data = iris_test_data.filter(['Species_Iris-setosa', 'Species_Iris-versicolor', 'Species_Iris-virginica'])

x = tf.placeholder(tf.float32,[None, 4])

W = tf.Variable(tf.zeros([4, 3]))
b = tf.Variable(tf.zeros([3]))

y = tf.nn.softmax(tf.matmul(x, W) + b)

y_ = tf.placeholder(tf.float32, [None, 3])

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

train_step = tf.train.GradientDescentOptimizer(0.05).minimize(cross_entropy)

sess = tf.InteractiveSession()

tf.global_variables_initializer().run()
for _ in range(1000):
    #Usually send batches to the training step. But since the dataset is small sending all
    sess.run(train_step, feed_dict={x: iris_train_input_data, y_: iris_train_label_data})

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

print('Accuracy : ', sess.run(accuracy, feed_dict={x: iris_test_input_data, y_: iris_test_label_data}))