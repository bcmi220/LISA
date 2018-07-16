import tensorflow as tf
import argparse
import dataset
from vocab import Vocab
import os
from LISA_model import LISAModel

arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--train_file', type=str, help='Training data file')
arg_parser.add_argument('--dev_file', type=str, help='Development data file')
arg_parser.add_argument('--save_dir', type=str, help='Training data file')
arg_parser.add_argument('--word_embedding_file', type=str, help='File containing pre-trained word embeddings')

args = arg_parser.parse_args()

data_config = {
      'id': {
        'idx': 0,
      },
      'word': {
        'idx': 3,
        'feature': True,
        'vocab': 'glove.6B.100d.txt',
        'converter': 'lowercase',
        'oov': True
      },
      'auto_pos': {
        'idx': 4,
        'vocab': 'gold_pos'
      },
      'gold_pos': {
        'idx': 5,
        'label': True,
        'vocab': 'gold_pos'
      },
      'parse_head': {
        'idx': 6,
        'label': True,
        'converter': 'parse_roots_self_loop'
      },
      'parse_label': {
        'idx': 7,
        'label': True,
        'vocab': 'parse_label'
      },
      'domain': {
        'idx': 0,
        'vocab': 'domain',
        'converter': 'strip_conll12_domain'
      },
      'predicate': {
        'idx': 10,
        'label': True,
        'vocab': 'predicate',
        'converter': 'conll12_binary_predicates'
      },
      'srl': {
        'idx': [14, -1],
        'label': True,
        'vocab': 'srl'
      },
    }

num_epochs = 1
batch_size = 256
is_train = True

if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir)

tf.logging.set_verbosity(tf.logging.INFO)

train_vocab = Vocab(args.train_file, data_config, args.save_dir)

def get_input_fn(data_file):
  # this needs to be created from here so that it ends up in the same tf.Graph as everything else
  # vocab_lookup_ops = train_vocab.get_lookup_ops(args.word_embedding_file) if args.word_embedding_file \
  #   else train_vocab.get_lookup_ops()
  vocab_lookup_ops = train_vocab.create_vocab_lookup_ops(args.word_embedding_file) if args.word_embedding_file \
    else train_vocab.create_vocab_lookup_ops()

  return dataset.get_data_iterator(data_file, data_config, vocab_lookup_ops, batch_size, num_epochs, is_train)


def train_input_fn():
  return get_input_fn(args.train_file)

def dev_input_fn():
  return get_input_fn(args.dev_file)


model = LISAModel(args)

estimator = tf.estimator.Estimator(model_fn=model.model_fn, model_dir=args.save_dir)

estimator.train(input_fn=train_input_fn, steps=20000)

estimator.evaluate(input_fn=train_input_fn)

# np.set_printoptions(threshold=np.inf)
# with tf.Session() as sess:
#   sess.run(tf.tables_initializer())
#   for i in range(3):
#     print(sess.run(input_fn()))

