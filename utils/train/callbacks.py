from tensorflow.keras.callbacks import Callback
import tensorflow.keras.backend as K
import matplotlib.pyplot as plt
import os


class EncoderCheckpoint(Callback):
    def __init__(self, resnet_enc, save_dir):
        super().__init__()
        self.save_dir = os.path.join(save_dir, 'encoder.h5')
        self.min_loss = 1e5
        self.resnet_enc = resnet_enc

    def on_epoch_end(self, epoch, logs=None):
        if logs['loss'] < self.min_loss:
            self.min_loss = logs['loss']
            print('\nSaving model, new lowest loss:', self.min_loss)
            self.resnet_enc.save_weights(self.save_dir)


# Taken from here: https://www.jeremyjordan.me/nn-learning-rate/
class LRFinder(Callback):
    """
    A simple callback for finding the optimal learning rate range for your model + dataset.

    # Usage
        ```python
            lr_finder = LRFinder(min_lr=1e-5,
                                 max_lr=1e-2,
                                 steps_per_epoch=np.ceil(epoch_size/batch_size),
                                 epochs=3)
            model.fit(X_train, Y_train, callbacks=[lr_finder])

            lr_finder.plot_loss()
        ```

    # Arguments
        min_lr: The lower bound of the learning rate range for the experiment.
        max_lr: The upper bound of the learning rate range for the experiment.
        steps_per_epoch: Number of mini-batches in the dataset. Calculated as `np.ceil(epoch_size/batch_size)`.
        epochs: Number of epochs to run experiment. Usually between 2 and 4 epochs is sufficient.

    # References
        Blog post: jeremyjordan.me/nn-learning-rate
        Original paper: https://arxiv.org/abs/1506.01186
    """

    def __init__(self, min_lr=1e-5, max_lr=1e-2, steps_per_epoch=None, epochs=None):
        super().__init__()

        self.min_lr = min_lr
        self.max_lr = max_lr
        self.total_iterations = steps_per_epoch * epochs
        self.iteration = 0
        self.history = {}

    def clr(self):
        """Calculate the learning rate."""
        x = self.iteration / self.total_iterations
        return self.min_lr + (self.max_lr - self.min_lr) * x

    def on_train_begin(self, logs=None):
        """Initialize the learning rate to the minimum value at the start of training."""
        logs = logs or {}
        K.set_value(self.model.optimizer.lr, self.min_lr)

    def on_batch_end(self, epoch, logs=None):
        """Record previous batch statistics and update the learning rate."""
        logs = logs or {}
        self.iteration += 1

        self.history.setdefault('lr', []).append(K.get_value(self.model.optimizer.lr))
        self.history.setdefault('iterations', []).append(self.iteration)

        for k, v in logs.items():
            self.history.setdefault(k, []).append(v)

        K.set_value(self.model.optimizer.lr, self.clr())

    def plot_lr(self):
        """Helper function to quickly inspect the learning rate schedule."""
        plt.plot(self.history['iterations'], self.history['lr'])
        # plt.yscale('log')
        plt.xlabel('Iteration')
        plt.ylabel('Learning rate')

        plt.savefig('finder_learning_rate.png')
        plt.show()

    def plot_loss(self):
        """Helper function to quickly observe the learning rate experiment results."""
        plt.plot(self.history['lr'], self.history['loss'])
        # plt.xscale('log')
        plt.xlabel('Learning rate')
        plt.ylabel('Loss')

        plt.savefig('finder_loss.png')
        plt.show()