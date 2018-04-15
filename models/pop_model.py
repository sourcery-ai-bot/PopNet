from base.base_model import BaseModel
import tensorflow as tf

class PopModel(BaseModel):
    def __init__(self, config):
        super(PopModel, self).__init__(config)
        # call the build_model and init_saver functions.
        self.build_model()
        self.init_saver()


    def build_model(self):
        # Network placeholders
        self.is_training = tf.placeholder(tf.bool)

        self.x = tf.placeholder(tf.float32, shape=[None, self.config.chunk_height, self.config.chunk_width, self.config.num_features], name='x')
        self.x_proj = tf.placeholder(tf.float32, name='x_proj')
        self.y_true = tf.placeholder(tf.float32, shape=[None, self.config.chunk_height, self.config.chunk_width, 1], name='y_true')
        self.y_pop = tf.placeholder(tf.float32, shape=None, name='y_pop')

        # Network architecture
        conv1 = tf.layers.conv2d(
            inputs=self.x,
            filters=6,
            kernel_size=[7, 7], # [filter height, filter width]
            strides=(1, 1),
            padding="same",
            activation=tf.nn.relu,
            name='convolution_1')

        norm1 = tf.nn.local_response_normalization(
            conv1,
            depth_radius=5,
            bias=1,
            alpha=1,
            beta=0.5,
            name='normalization_1')

        # pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],

        conv2 = tf.layers.conv2d(
            inputs=norm1,
            filters=6,
            kernel_size=[5, 5],
            strides=(1, 1),
            padding="same",
            activation=tf.nn.relu,
            name='convolution_2')

        norm2 = tf.nn.local_response_normalization(
            conv2,
            depth_radius=5,
            bias=1,
            alpha=1,
            beta=0.5,
            name='normalization_2')

        dense1 = tf.layers.dense(inputs=norm2, units=32, activation=tf.nn.relu, name='dense_1')

        self.y = tf.layers.dense(inputs=dense1, units=1, name='y')

        # y_sum = tf.Variable(0)
        #
        # y_sum = tf.add(y_sum, tf.cast(tf.reduce_sum(self.y), tf.int32))
        #
        # y_sum = tf.Variable(y_sum,)

        # self.y_sum = tf.Print(self.y_sum, [self.y_sum], message="This is y_sum: ")
        #
        # b = tf.add(self.y_sum, self.y_sum)

        with tf.name_scope("pop_tot_loss"):
            #self.pop_total_err = tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y)))
            #self.pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.cast(tf.size(self.y), tf.float32)) # 573440)
            self.pop_total_err = tf.reduce_mean(tf.abs(tf.subtract(tf.divide(self.y_pop, self.x_proj), tf.reduce_sum(self.y, axis=0))))
        with tf.name_scope("pop_cell_loss"):
            self.root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(self.y_true, self.y))))

        with tf.name_scope("loss"):
            # Cost function
            # pop_total_err = tf.div(tf.abs(tf.subtract(self.x_proj, tf.reduce_sum(self.y))), tf.size(self.y))

            # MANGLER AT DIVIDE POP_TOTAL_ERR med antallet af celler
            # TensorFlow function for root mean square error

            self.loss_func = tf.add(tf.multiply(0.9, self.root_mean_square_err), tf.multiply(0.1, self.pop_total_err))

            # Initializing the optimizer, that will optimize the root mean square error through backpropagation, and thus learn
            self.train_step = tf.train.AdamOptimizer(self.config.learning_rate).minimize(self.loss_func,
                                                                                   global_step=self.global_step_tensor)

        with tf.name_scope("y_sum"):
            # tf.Print(self.y_sum, [self.y_sum])
            # a = tf.add(self.y_sum, self.y_sum)

            self.y_sum += tf.reduce_sum(self.y)

    def init_saver(self):
        #here you initalize the tensorflow saver that will be used in saving the checkpoints.
        self.saver = tf.train.Saver(max_to_keep=self.config.max_to_keep)