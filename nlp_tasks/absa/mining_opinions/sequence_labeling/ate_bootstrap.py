# -*- coding: utf-8 -*-


import argparse
import sys
import random
import copy

import torch
import numpy

from nlp_tasks.absa.utils import argument_utils
from nlp_tasks.absa.mining_opinions.sequence_labeling import sequence_labeling_train_templates as templates


parser = argparse.ArgumentParser()
parser.add_argument('--current_dataset', help='dataset name', default='RealASOTripletRest16', type=str)
parser.add_argument('--task_name', help='task name', default='ate', type=str)
parser.add_argument('--data_type', help='data type', default='common', type=str)
parser.add_argument('--model_name', help='model name', default='NerLstm', type=str)
parser.add_argument('--timestamp', help='timestamp', default=int(1571400646), type=int)
parser.add_argument('--train', help='if train a new model', default=False, type=argument_utils.my_bool)
parser.add_argument('--evaluate', help='evaluate', default=False, type=argument_utils.my_bool)
parser.add_argument('--predict', help='predict text', default=False, type=argument_utils.my_bool)
parser.add_argument('--predict_test', help='predict test set', default=True, type=argument_utils.my_bool)
parser.add_argument('--epochs', help='epochs', default=100, type=int)
parser.add_argument('--batch_size', help='batch_size', default=32, type=int)
parser.add_argument('--patience', help='patience', default=10, type=int)
parser.add_argument('--visualize_attention', help='visualize attention', default=False, type=argument_utils.my_bool)
parser.add_argument('--embedding_filepath', help='embedding filepath',
                    default='D:\program\word-vector\glove.840B.300d.txt', type=str)
parser.add_argument('--embed_size', help='embedding dim', default=300, type=int)
parser.add_argument('--seed', default=776, type=int)
parser.add_argument('--repeat', default='0', type=str)
parser.add_argument('--device', default=None, type=str)
parser.add_argument('--gpu_id', default='0', type=str)
parser.add_argument('--position', default=False, type=argument_utils.my_bool)
parser.add_argument('--position_embeddings_dim', help='position embeddings dim', default=32, type=int)
parser.add_argument('--debug', default=False, type=argument_utils.my_bool)
parser.add_argument('--early_stopping_by_batch', default=False, type=argument_utils.my_bool)

parser.add_argument('--crf', help='True for crf tagger, False for simple tagger', default=False,
                    type=argument_utils.my_bool)

parser.add_argument('--fixed_bert', default=True, type=argument_utils.my_bool)
parser.add_argument('--learning_rate_in_bert', default=2e-5, type=float)
parser.add_argument('--l2_in_bert', default=0.00001, type=float)
parser.add_argument('--lstm_layer_num_in_bert', default=1, type=int)
parser.add_argument('--bert_file_path', help='bert_file_path',
                    default=r'D:\program\word-vector\bert-base-uncased.tar.gz', type=str)
parser.add_argument('--bert_vocab_file_path', help='bert_vocab_file_path',
                    default=r'D:\program\word-vector\uncased_L-12_H-768_A-12\vocab.txt', type=str)
parser.add_argument('--max_len', help='max length', default=100, type=int)

parser.add_argument('--include_conflict', default=False, type=argument_utils.my_bool)

args = parser.parse_args()

args.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if args.device is None else torch.device(args.device)
gpu_ids = args.gpu_id.split(',')
if len(gpu_ids) == 1:
    args.gpu_id = -1 if int(gpu_ids[0]) == -1 else 0
else:
    args.gpu_id = list(range(len(gpu_ids)))


configuration = args.__dict__

if configuration['seed'] is not None:
    random.seed(configuration['seed'])
    numpy.random.seed(configuration['seed'])
    torch.manual_seed(configuration['seed'])
    torch.cuda.manual_seed(configuration['seed'])
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

model_name_complete_prefix = 'model_name_{model_name}-include_conflict_{include_conflict}'.format_map(configuration)

configuration_for_this_repeat = copy.deepcopy(configuration)
configuration_for_this_repeat['model_name_complete'] = '%s.%s' % (model_name_complete_prefix, args.repeat)

model_name = configuration['model_name']
if model_name in ['NerLstm']:
    template = templates.NerLstm(configuration_for_this_repeat)
elif model_name in ['NerBert']:
    template = templates.NerBert(configuration_for_this_repeat)
else:
    raise NotImplementedError(model_name)

if configuration_for_this_repeat['train']:
    template.train()

if configuration_for_this_repeat['evaluate']:
    template.evaluate()

if configuration_for_this_repeat['predict_test']:
    output_filepath = template.model_dir + 'result_of_predicting_test.txt'
    print('result_of_predicting_test:%s ' % output_filepath)
    template.predict_test(output_filepath, only_error=False)

if configuration_for_this_repeat['predict']:
    texts = [
        {
            'words': 'I love the drinks , esp lychee martini , and the food is also VERY good .',
        },
        {
            'words': 'I love the drinks , esp lychee martini , and the food is also VERY good .',
        },
        {
            'words': 'I love the drinks , esp lychee martini , and the food is also VERY good .',
        },
    ]
    texts_preprocessed = []
    for text in texts:
        text_preprocessed = {
            'words': text['words'].split(' ')
        }
        texts_preprocessed.append(text_preprocessed)
    result = template.predict(texts_preprocessed)
    print(result)

