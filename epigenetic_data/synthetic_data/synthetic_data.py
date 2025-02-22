import numpy as np

from neural_network_models.recurrent_neural_network import RecurrentNeuralNetwork
from neural_network_models.multilayer_perceptron import MultilayerPerceptron


num_classes = 2
num_genes = 64
training_examples_for_class = 500
validation_examples_for_class = 100

num_training_examples = num_classes * training_examples_for_class
num_validation_examples = num_classes * validation_examples_for_class


def normalize_data(data_point):
    """
    Shift the input data in interval [0, 1]

    :param data_point:
    :return:
    """
    min_element = min(data_point)
    max_element = max(data_point)

    # shift data in interval [0, 1]
    normalized_data = np.ndarray(shape=(len(data_point)), dtype=np.float32)
    for index in range(len(data_point)):
        normalized_data[index] = (data_point[index] - min_element)/(max_element - min_element)

    # create probability distribution
    #total_sum = sum(normalized_data)
    #for index in range(len(normalized_data)):
        #normalized_data[index] = normalized_data[index] / total_sum

    return normalized_data


def create_data_point(num_genes, class_id, class_id_to_shifted_genes, shifted_mean):
    mean = 0
    stddev = 0.4
    data_point = np.random.normal(mean, stddev, num_genes)

    shifted_genes = class_id_to_shifted_genes[class_id]

    for shifted_gene in shifted_genes:
        data_point[shifted_gene] = np.random.normal(shifted_mean, stddev, 1)

    return data_point


def create_one_hot_encoding(class_id):
    one_hot_encoding = [0] * num_classes
    one_hot_encoding[class_id] = 1.0

    return one_hot_encoding


def create_training_dataset(class_id_to_shifted_genes, shifted_mean):
    """

    :return:
    """
    training_dataset = dict()

    training_data = np.ndarray(shape=(num_training_examples, num_genes),
                               dtype=np.float32)
    training_labels = np.ndarray(shape=(num_training_examples, num_classes),
                                 dtype=np.float32)

    for class_id in range(num_classes):
        for index in range(training_examples_for_class):
            training_data[class_id * training_examples_for_class + index, :] = \
                normalize_data(create_data_point(num_genes, class_id, class_id_to_shifted_genes, shifted_mean))
            training_labels[class_id * training_examples_for_class + index, :] = create_one_hot_encoding(class_id)

    data_and_labels = (zip(training_data, training_labels))
    np.random.shuffle(data_and_labels)

    permutation = np.random.permutation(len(training_data))

    training_dataset["training_data"] = training_data[permutation]
    training_dataset["training_labels"] = training_labels[permutation]

    return training_dataset


def create_validation_dataset(class_id_to_shifted_genes, shifted_mean):
    """

    :return:
    """
    validation_dataset = dict()

    validation_data = np.ndarray(shape=(num_validation_examples, num_genes),
                               dtype=np.float32)
    validation_labels = np.ndarray(shape=(num_validation_examples, num_classes),
                                 dtype=np.float32)

    for class_id in range(num_classes):
        for index in range(validation_examples_for_class):
            validation_data[class_id * validation_examples_for_class + index, :] = \
                normalize_data(create_data_point(num_genes, class_id, class_id_to_shifted_genes, shifted_mean))
            validation_labels[class_id * validation_examples_for_class + index, :] = create_one_hot_encoding(class_id)

    validation_dataset["validation_data"] = validation_data
    validation_dataset["validation_labels"] = validation_labels

    return validation_dataset


def create_class_id_to_shifted_genes(num_classes, num_genes, num_shifted_genes):

    class_id_to_shifted_genes = dict()

    for index in range(num_classes):
        shifted_genes = np.random.choice(range(num_genes), num_shifted_genes, replace=False)
        class_id_to_shifted_genes[index] = shifted_genes

    return class_id_to_shifted_genes


class SyntheticData(object):

    def __init__(self, num_shifted_genes, shifted_mean):
        self.num_shifted_genes = num_shifted_genes
        self.shifted_mean = shifted_mean
        self.class_id_to_shifted_genes = create_class_id_to_shifted_genes(num_classes, num_genes, num_shifted_genes)
        self.training_dataset = create_training_dataset(self.class_id_to_shifted_genes, shifted_mean)
        self.validation_dataset = create_validation_dataset(self.class_id_to_shifted_genes, shifted_mean)

    def test_MLP(self):
        ffnn = MultilayerPerceptron(num_genes, [256, 128, 64, 32], num_classes)
        validation_accuracy, ffnn_confussion_matrix, ROC_points = ffnn.train_and_evaluate(
            self.training_dataset, self.validation_dataset, 0.05, 0.0, 1)
        print ffnn_confussion_matrix

    def test_RNN(self):
        recurrent_neural_network = RecurrentNeuralNetwork(
            input_sequence_length=8, input_step_size=8,
            LSTM_units_state_size=[64, 128], hidden_units=[128, 64],
            output_size=num_classes)

        learning_rate = 0.0001
        weight_decay = 0.001
        keep_probability = 0.7

        validation_accuracy, rnn_confussion_matrix, ROC_points = recurrent_neural_network.train_and_evaluate(
            self.training_dataset, self.validation_dataset,
            learning_rate, weight_decay, keep_probability)
        print rnn_confussion_matrix
