
import argparse

import numpy as np

from bilm.training import train_curriculum, load_vocab, test, load_options_latest_checkpoint
from bilm.data import BidirectionalLMDataset


def main(args):
    vocab = load_vocab(args.vocab_file, args.vocab_min_occur)
    train_tokens = 768648884 #(this for 1B Word Benchmark)
    if args.train_tokens == 'wikitext2':
        train_tokens = 2051910 *3 * 1.5 #Enwiki2 is 3x longer if split into sentences and a further 1.5 when using sentence split size of 20
    elif args.train_tokens == 'wikitext103':
        train_tokens = 101425658*3 *1.5 #wikitext-103
    options = {
     'bidirectional': True,
     'char_cnn': {'activation': 'relu',
      'embedding': {'dim': 16},
      'filters': [[1, 32],
       [2, 32],
       [3, 64],
       [4, 128],
       [5, 256],
       [6, 512],
       [7, 1024]],
      'max_characters_per_token': 50,
      'n_characters': 261,
      'n_highway': 2},
     'dropout': 0.1,
     'lstm': {
      'cell_clip': 3,
      'dim': 4096,
      'n_layers': 2,
      'proj_clip': 3,
      'projection_dim': 512,
      'use_skip_connections': True},
     'all_clip_norm_val': 10.0,
     'n_epochs': 10,
     'n_train_tokens': train_tokens,
     'batch_size': args.train_batch_size,
     'n_tokens_vocab': vocab.size,
     'unroll_steps': 20,
     'n_negative_samples_batch': 8192,
    }

    prefix = args.train_prefix
    train_data = BidirectionalLMDataset(prefix, vocab, test=False, shuffle_on_load=False, curriculum=True, num_steps=20) # we dont shuffle since our curriculum generator shuffles
    tf_save_dir = args.save_dir
    tf_log_dir = args.save_dir
    train_curriculum(options, train_data, args.n_gpus, tf_save_dir, tf_log_dir, args.initial_competence, args.competence_increment, args.target_batches, args.test_prefix, args.test_interval, vocab )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_batches', default=3820, type=int) #18896
    parser.add_argument('--save_dir', help='Location of checkpoint files')
    parser.add_argument('--initial_competence', type=float, default = 0.01) 
    parser.add_argument('--competence_increment', type=float, default = 0.0004)
    parser.add_argument('--converge', default = False)
    parser.add_argument('--vocab_min_occur',type=int, default=50, help='Min occurrence of word in vocab')
    parser.add_argument('--vocab_file', default='wikitext-2/vocab.txt', help='Vocabulary file')
    parser.add_argument('--train_prefix', default='wikitext-103/wiki.train.tokens', help='Prefix for train files')
    parser.add_argument('--test_prefix', default='wikitext-2/wiki.valid.tokens.sent')
    parser.add_argument('--test_interval', default=100, type=int, help='run full test every N batches')
    parser.add_argument('--train_tokens', default = 'wikitext2', help='Choose training tokens size')
    parser.add_argument('--n_gpus',type=int, default=3, help='Number of GPUS')
    parser.add_argument('--train_batch_size', type=int, default=128,help='Train Batch size')
    args = parser.parse_args()
    main(args)

