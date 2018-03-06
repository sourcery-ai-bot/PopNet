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

        self.x = tf.placeholder(tf.float32, shape=[None, 32, 32, 1])
        self.y_true = tf.placeholder(tf.float32, shape=[None, 32, 32, 1])

        # Network architecture
        conv1 = tf.layers.conv2d(
            inputs=self.x,
            filters=32,
            kernel_size=[5, 5],
            padding="same",
            activation=tf.nn.relu)

        conv2 = tf.layers.conv2d(
            inputs=conv1,
            filters=48,
            kernel_size=[5, 5],
            padding="same",
            activation=tf.nn.relu)

        # MÅSKE VI SKAL BRUGE POOLING FOR AT GÅ FRA 48 I SIDSTE DIMENSION TIL 1?
        # conv2_flat = tf.reshape(conv2, [None, 32 * 32 * 48])
        dense1 = tf.layers.dense(inputs=conv2, units=1024, activation=tf.nn.relu)

        self.y = tf.layers.dense(inputs=dense1, units=1)

        with tf.name_scope("loss"):
            # TensorFlow function for root mean square error
            self.root_mean_square_err = tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(self.y_true, self.y))))

            # Initializing the optimizer, that will optimize the root mean square error through backpropagation, and thus learn
            self.train_step = tf.train.AdamOptimizer(self.config.learning_rate).minimize(self.root_mean_square_err,
                                                                                   global_step=self.global_step_tensor)


    def init_saver(self):
        #here you initalize the tensorflow saver that will be used in saving the checkpoints.
        self.saver = tf.train.Saver(max_to_keep=self.config.max_to_keep)