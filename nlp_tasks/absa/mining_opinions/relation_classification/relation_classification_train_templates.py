import json
import sys
import os
from collections import defaultdict

import torch
from sklearn.preprocessing import MultiLabelBinarizer
from keras.preprocessing import text as keras_text
from keras.preprocessing import sequence as keras_seq
from allennlp.data.token_indexers import WordpieceIndexer
from allennlp.data.iterators import BucketIterator
from allennlp.data.iterators import BasicIterator
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from allennlp.modules.token_embedders.bert_token_embedder import PretrainedBertEmbedder
from allennlp.modules.text_field_embedders import TextFieldEmbedder
import torch.optim as optim
from torch.optim import adagrad
# from allennlp.training.trainer import Trainer
from nlp_tasks.absa.aspect_category_detection_and_sentiment_classification.my_allennlp_trainer import Trainer
from allennlp.data.vocabulary import Vocabulary
from allennlp.predictors import text_classifier
from allennlp.data.token_indexers import SingleIdTokenIndexer
import spacy
from pytorch_pretrained_bert.tokenization import BertTokenizer
from tqdm import tqdm
from allennlp.nn import util as nn_util
from allennlp.modules.token_embedders.bert_token_embedder import BertModel, PretrainedBertModel
from allennlp.modules.token_embedders.bert_token_embedder import BertEmbedder, PretrainedBertEmbedder

from nlp_tasks.absa.entities import ModelTrainTemplate
from nlp_tasks.utils import word_processor
from nlp_tasks.utils import tokenizers
from nlp_tasks.absa.utils import embedding_utils
from nlp_tasks.utils import attention_visualizer
from nlp_tasks.absa.mining_opinions.relation_classification import relation_classification_data_reader
from nlp_tasks.absa.mining_opinions.relation_classification import pytorch_models
from allennlp.modules.token_embedders import Embedding
from allennlp.modules.token_embedders import embedding
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from nlp_tasks.utils import file_utils
from nlp_tasks.common import common_path
from nlp_tasks.absa.aspect_category_detection_and_sentiment_classification import allennlp_callback
from nlp_tasks.absa.mining_opinions.data_adapter import data_object


class SpanBasedModelForRelationClassification(ModelTrainTemplate.ModelTrainTemplate):
    """
    2019-acl-Open-Domain Targeted Sentiment Analysisvia Span-Based Extraction and Classification
    """

    def __init__(self, configuration):
        super().__init__(configuration)
        self.data_reader = None
        self.train_data = None
        self.dev_data = None
        self.test_data = None
        self.hard_test_data = None
        self.distinct_categories = None
        self.distinct_polarities = None
        self._load_data()
        if self.configuration['debug']:
            self.train_data = self.train_data[: 128]
            self.dev_data = self.dev_data[: 128]
            self.test_data = self.test_data[: 128]

        self.vocab = None
        self._build_vocab()

        self.iterator = None
        self.val_iterator = None
        self._build_iterator()

    def _get_dataset(self):
        return data_object.get_dataset_class_by_name(self.configuration['current_dataset'])(self.configuration)

    def _get_data_reader(self):
        token_indexer = SingleIdTokenIndexer(namespace="tokens")
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = relation_classification_data_reader.RelationClassificationDatasetReader(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )
        return reader

    def _generate_sample_key(self, sample: dict):
        """

        :param sample:
        :return:
        """
        sentence = ' '.join(sample['words'])
        aspect_term = str(sample['opinion']['aspect_term'])
        opinion_term = str(sample['opinion']['opinion_term'])
        return '%s-%s-%s' % (sentence, aspect_term, opinion_term)

    def _load_data(self):
        data_filepath = self.base_data_dir + 'data'
        if os.path.exists(data_filepath):
            self.train_data, self.dev_data, self.test_data, self.distinct_polarities = \
                super()._load_object(data_filepath)
            reader = self._get_data_reader()
            self.data_reader = reader
        else:
            data_type_and_data_temp = self.dataset.get_data_type_and_data_dict()
            data_type_and_data = {}
            for data_type, data_temp in data_type_and_data_temp.items():
                sentence_and_aspect_terms = defaultdict(list)

                for sample in data_temp:
                    original_line_data = sample.metadata['original_line_data']
                    sentence = original_line_data['sentence']
                    opinions = original_line_data['opinions']
                    if len(opinions) == 0 or 'polarity' not in opinions[0]:
                        continue
                    sentence_and_aspect_terms[sentence].append(original_line_data)

                data = []

                # 正样本
                # 解决生产负样本时，正样本之间共享opinion term的问题
                positive_sample_keys = set()
                for original_line_datas in sentence_and_aspect_terms.values():
                    for i in range(len(original_line_datas)):
                        original_line_data_i = original_line_datas[i]
                        words = original_line_data_i['words']
                        opinions_i = original_line_data_i['opinions']
                        for opinion in opinions_i:
                            temp = {'words': words, 'label': 1, 'opinion': opinion}
                            sample_key = self._generate_sample_key(temp)
                            temp['sample_key'] = sample_key
                            positive_sample_keys.add(sample_key)
                            data.append(temp)

                # 负样本
                for original_line_datas in sentence_and_aspect_terms.values():
                    for i in range(len(original_line_datas)):
                        original_line_data_i = original_line_datas[i]
                        words = original_line_data_i['words']
                        opinions_i = original_line_data_i['opinions']
                        aspect_term_i = opinions_i[0]['aspect_term']
                        for j in range(i + 1, len(original_line_datas)):
                            original_line_data_j = original_line_datas[j]
                            opinions_j = original_line_data_j['opinions']
                            aspect_term_j = opinions_j[0]['aspect_term']
                            for opinion_i in opinions_i:
                                temp = {'words': words,
                                     'label': 0,
                                     'opinion': {'aspect_term': aspect_term_j,
                                                 'opinion_term': opinion_i['opinion_term']}
                                     }
                                if self._generate_sample_key(temp) not in positive_sample_keys:
                                    temp['sample_key'] = self._generate_sample_key(temp)
                                    data.append(temp)
                            for opinion_j in opinions_j:
                                temp = {'words': words,
                                     'label': 0,
                                     'opinion': {'aspect_term': aspect_term_i,
                                                 'opinion_term': opinion_j['opinion_term']}
                                     }
                                if self._generate_sample_key(temp) not in positive_sample_keys:
                                    temp['sample_key'] = self._generate_sample_key(temp)
                                    data.append(temp)
                data_type_and_data[data_type] = data

            reader = self._get_data_reader()
            self.data_reader = reader
            self.train_data = reader.read(data_type_and_data['train'])
            self.dev_data = reader.read(data_type_and_data['dev'])
            self.test_data = reader.read(data_type_and_data['test'])
            data = [self.train_data, self.dev_data, self.test_data, self.distinct_polarities]
            super()._save_object(data_filepath, data)

    def _build_vocab(self):
        if self.configuration['train']:
            vocab_file_path = self.base_data_dir + 'vocab'
            if os.path.exists(vocab_file_path):
                self.vocab = super()._load_object(vocab_file_path)
            else:
                data = self.train_data + self.dev_data + self.test_data
                self.vocab = Vocabulary.from_instances(data, max_vocab_size=sys.maxsize)
                super()._save_object(vocab_file_path, self.vocab)
            self.model_meta_data['vocab'] = self.vocab
        else:
            self.vocab = self.model_meta_data['vocab']

    def _build_iterator(self):
        self.iterator = BucketIterator(batch_size=self.configuration['batch_size'],
                                       sorting_keys=[("tokens", "num_tokens")],
                                       )
        self.iterator.index_with(self.vocab)
        self.val_iterator = BasicIterator(batch_size=self.configuration['batch_size'])
        self.val_iterator.index_with(self.vocab)

    def _print_args(self, model):
        n_trainable_params, n_nontrainable_params = 0, 0
        for p in model.parameters():
            n_params = torch.prod(torch.tensor(p.shape)).item()
            if p.requires_grad:
                n_trainable_params += n_params
            else:
                n_nontrainable_params += n_params
        self.logger.info('n_trainable_params: {0}, n_nontrainable_params: {1}'.format(n_trainable_params, n_nontrainable_params))
        self.logger.info('> training arguments:')
        for arg in self.configuration.keys():
            self.logger.info('>>> {0}: {1}'.format(arg, self.configuration[arg]))

    def _find_model_function_pure(self):
        return pytorch_models.SpanBasedModelForRC

    def _get_position_embeddings_dim(self):
        return 300

    def _is_train_token_embeddings(self):
        return False

    def _find_model_function(self):
        embedding_dim = self.configuration['embed_size']
        embedding_matrix_filepath = self.base_data_dir + 'embedding_matrix'
        if os.path.exists(embedding_matrix_filepath):
            embedding_matrix = super()._load_object(embedding_matrix_filepath)
        else:
            embedding_filepath = self.configuration['embedding_filepath']
            embedding_matrix = embedding._read_embeddings_from_text_file(embedding_filepath, embedding_dim,
                                                                         self.vocab, namespace='tokens')
            super()._save_object(embedding_matrix_filepath, embedding_matrix)
        embedding_matrix = embedding_matrix.to(self.configuration['device'])
        token_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='tokens'),
                                    embedding_dim=embedding_dim, padding_index=0, vocab_namespace='tokens',
                                    trainable=self._is_train_token_embeddings(), weight=embedding_matrix)
        # the embedder maps the input tokens to the appropriate embedding matrix
        word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"tokens": token_embedding})

        position_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='position'),
                                    embedding_dim=self._get_position_embeddings_dim(), padding_index=0)
        position_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"position": position_embedding},
                                                                    # we'll be ignoring masks so we'll need to set this to True
                                                                    allow_unmatched_keys=True)

        model_function = self._find_model_function_pure()
        model = model_function(
            word_embedder,
            position_embedder,
            self.distinct_polarities,
            self.vocab,
            self.configuration,
        )
        self._print_args(model)
        model = model.to(self.configuration['device'])
        return model

    def _get_optimizer(self, model):
        _params = filter(lambda p: p.requires_grad, model.parameters())
        return optim.Adam(_params, lr=0.001, weight_decay=0.00001)

    def _get_estimator(self, model):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        estimator = pytorch_models.SpanBasedModelForRCEstimator(model, self.val_iterator, self.distinct_polarities,
                                                                cuda_device=gpu_id, configuration=self.configuration)
        return estimator

    def _get_estimate_callback(self, model):
        result = []
        data_type_and_data = {
            'train': self.train_data,
            'dev': self.dev_data,
            'test': self.test_data
        }
        estimator = self._get_estimator(model)
        estimate_callback = allennlp_callback.EstimateCallback(data_type_and_data, estimator, self.logger)
        result.append(estimate_callback)
        return result

    def _get_loss_weight_callback(self):
        result = []
        set_loss_weight_callback = allennlp_callback.SetLossWeightCallback(self.model, self.logger,
                                                                           acd_warmup_epoch_num=self._get_acd_warmup_epoch_num())
        result.append(set_loss_weight_callback)
        return result

    def _get_fixed_loss_weight_callback(self, model, category_loss_weight=1, sentiment_loss_weight=1):
        result = []
        fixed_loss_weight_callback = allennlp_callback.FixedLossWeightCallback(model, self.logger,
                                                                             category_loss_weight=category_loss_weight,
                                                                             sentiment_loss_weight=sentiment_loss_weight)
        result.append(fixed_loss_weight_callback)
        return result

    def _get_bert_word_embedder(self):
        return None

    def _inner_train(self):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1

        self.model = self._find_model_function()
        estimator = self._get_estimator(self.model)
        callbacks = self._get_estimate_callback(self.model)
        validation_metric = '+rc_f1'
        self.logger.info('validation_metric: %s' % validation_metric)
        optimizer = self._get_optimizer(self.model)
        trainer = Trainer(
            model=self.model,
            optimizer=optimizer,
            iterator=self.iterator,
            train_dataset=self.train_data,
            validation_dataset=self.dev_data,
            cuda_device=gpu_id,
            num_epochs=self.configuration['epochs'],
            validation_metric=validation_metric,
            validation_iterator=self.val_iterator,
            serialization_dir=self.model_dir,
            patience=self.configuration['patience'],
            callbacks=callbacks,
            num_serialized_models_to_keep=2,
            early_stopping_by_batch=self.configuration['early_stopping_by_batch'],
            estimator=estimator,
            grad_clipping=5
        )
        metrics = trainer.train()
        self.logger.info('metrics: %s' % str(metrics))

    def _save_model(self):
        torch.save(self.model, self.best_model_filepath)

    def _load_model(self):
        if torch.cuda.is_available():
            self.model = torch.load(self.best_model_filepath)
        else:
            self.model = torch.load(self.best_model_filepath, map_location=torch.device('cpu'))
        self.model.configuration = self.configuration

    def evaluate(self):
        estimator = self._get_estimator(self.model)

        data_type_and_data = {
            'train': self.train_data,
            'dev': self.dev_data,
            'test': self.test_data
        }
        for data_type, data in data_type_and_data.items():
            result = estimator.estimate(data)
            self.logger.info('data_type: %s result: %s' % (data_type, result))

    def predict_backup(self):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        predictor = pytorch_models.SpanBasedModelPredictor(self.model, self.val_iterator,
                                                           self.distinct_polarities,
                                                           configuration=self.configuration,
                                                           cuda_device=gpu_id)

        data_type_and_data = {
            # 'train': self.train_data,
            # 'dev': self.dev_data,
            'test': self.test_data
        }
        if self.hard_test_data:
            data_type_and_data['hard_test'] = self.hard_test_data
        for data_type, data_temp in data_type_and_data.items():
            # for multi
            data = []
            for instance in data_temp:
                aspect_terms = instance.fields['sample'].metadata['aspect_terms']
                if len(aspect_terms) != 2:
                    continue
                data.append(instance)
                # text = instance.fields['sample'].metadata['text']
                # # i love the keyboard and the screen. 都预测正确(来自测试集)
                # # The best thing about this laptop is the price along with some of the newer features. 来自训练集 都正确
                # if 'that any existing MagSafe' in text:
                #     data.append(instance)
                #     break
            result = predictor.predict(data)
            correct_sentences = []
            for e in result:
                sentiment_outputs_for_aspect_terms = e ['sentiment_outputs_for_aspect_terms']
                aspect_terms = e['aspect_terms']
                for i in range(len(aspect_terms)):
                    if aspect_terms[i].polarity != sentiment_outputs_for_aspect_terms[i][1]:
                        break
                else:
                    correct_sentences.append(e['text'])

            file_utils.write_lines(correct_sentences, 'd:/correct_sentences.txt')

            self.logger.info('data_type: %s result: %s' % (data_type, result))

    def predict(self):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        predictor = pytorch_models.SpanBasedModelForRCPredictor(self.model, self.val_iterator,
                                                           self.distinct_polarities,
                                                           configuration=self.configuration,
                                                           cuda_device=gpu_id)

        data_type_and_data = {
            # 'train': self.train_data,
            # 'dev': self.dev_data,
            'test': self.test_data
        }
        if self.hard_test_data:
            data_type_and_data['hard_test'] = self.hard_test_data
        for data_type, data_temp in data_type_and_data.items():
            # for multi
            correct_sentences = file_utils.read_all_lines('d:/correct_sentences.txt')
            for sentence in correct_sentences:
                data = []
                for instance in data_temp:
                    text = instance.fields['sample'].metadata['text']
                    # i love the keyboard and the screen. 都预测正确(来自测试集)
                    # The best thing about this laptop is the price along with some of the newer features. 来自训练集 都正确
                    if sentence in text:
                        data.append(instance)
                result = predictor.predict(data)
                if result[0]['aspect_terms'][0].polarity == 'neutral' or result[1]['aspect_terms'][0].polarity == 'neutral':
                    continue
                for e in result:
                    sentiment_outputs_for_aspect_terms = e['sentiment_outputs_for_aspect_terms']
                    aspect_terms = e['aspect_terms']
                    for i in range(len(aspect_terms)):
                        if aspect_terms[i].polarity != 'neutral' and aspect_terms[i].polarity != sentiment_outputs_for_aspect_terms[i][1]:
                            print()

    def predict_test(self, output_filepath):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        predictor = pytorch_models.SpanBasedModelForRCPredictor(self.model, self.val_iterator,
                                                           self.distinct_polarities,
                                                           configuration=self.configuration,
                                                           cuda_device=gpu_id)

        data = self.test_data
        result = predictor.predict(data)
        output_lines = []
        for sample in result:
            text = sample['text']
            words_for_test = text.split(' ')
            aspect_terms = sample['aspect_terms']
            word_indices_of_aspect_terms = []
            for aspect_term in aspect_terms:
                from_index = aspect_term.from_index
                term = aspect_term.term
                start_index = 0
                if from_index > 0:
                    start_index = len(text[:from_index].strip().split(' '))
                term_length = len(term.split(' '))
                word_indices_of_aspect_terms.append([start_index, start_index + term_length])
            sentiment_outputs_for_aspect_terms = sample['sentiment_outputs_for_aspect_terms']
            for i in range(len(word_indices_of_aspect_terms)):
                term = aspect_terms[i].term
                word_indices = word_indices_of_aspect_terms[i]
                if term != ' '.join(words_for_test[word_indices[0]: word_indices[1]]):
                    print('error')
                sentiment = sentiment_outputs_for_aspect_terms[i][1]
                output_line = json.dumps({'text': text,
                                          'aspect_term':
                                              '%s-%d-%d' % (term, word_indices[0], word_indices[1]),
                                          'sentiment': sentiment
                                          })
                output_lines.append(output_line)
        file_utils.write_lines(output_lines, output_filepath)


class SpanBasedModelForMultiRelationClassification(SpanBasedModelForRelationClassification):
    """
    2019-acl-Open-Domain Targeted Sentiment Analysisvia Span-Based Extraction and Classification
    """

    def __init__(self, configuration):
        super().__init__(configuration)

    def _get_data_reader(self):
        token_indexer = SingleIdTokenIndexer(namespace="tokens")
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = relation_classification_data_reader.MultiRelationClassificationDatasetReader(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )
        return reader

    def _find_model_function_pure(self):
        return pytorch_models.SpanBasedModelForMultiRC

    def _get_estimator(self, model):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        estimator = pytorch_models.SpanBasedModelForMultiRCEstimator(model, self.val_iterator, self.distinct_polarities,
                                                                     cuda_device=gpu_id, configuration=self.configuration)
        return estimator

    def predict(self):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        predictor = pytorch_models.SpanBasedModelForRCPredictor(self.model, self.val_iterator,
                                                           self.distinct_polarities,
                                                           configuration=self.configuration,
                                                           cuda_device=gpu_id)

        data_type_and_data = {
            # 'train': self.train_data,
            # 'dev': self.dev_data,
            'test': self.test_data
        }
        if self.hard_test_data:
            data_type_and_data['hard_test'] = self.hard_test_data
        for data_type, data_temp in data_type_and_data.items():
            # for multi
            correct_sentences = file_utils.read_all_lines('d:/correct_sentences.txt')
            for sentence in correct_sentences:
                data = []
                for instance in data_temp:
                    text = instance.fields['sample'].metadata['text']
                    # i love the keyboard and the screen. 都预测正确(来自测试集)
                    # The best thing about this laptop is the price along with some of the newer features. 来自训练集 都正确
                    if sentence in text:
                        data.append(instance)
                result = predictor.predict(data)
                if result[0]['aspect_terms'][0].polarity == 'neutral' or result[1]['aspect_terms'][0].polarity == 'neutral':
                    continue
                for e in result:
                    sentiment_outputs_for_aspect_terms = e['sentiment_outputs_for_aspect_terms']
                    aspect_terms = e['aspect_terms']
                    for i in range(len(aspect_terms)):
                        if aspect_terms[i].polarity != 'neutral' and aspect_terms[i].polarity != sentiment_outputs_for_aspect_terms[i][1]:
                            print()

    def predict_test(self, output_filepath):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        predictor = pytorch_models.SpanBasedModelForMultiRCPredictor(self.model, self.val_iterator,
                                                           self.distinct_polarities,
                                                           configuration=self.configuration,
                                                           cuda_device=gpu_id)

        data = self.test_data
        result = predictor.predict(data)
        pred = result['pred']
        true = result['true']
        samples = result['samples']

        output_lines = []
        for i, sample in enumerate(samples):
            sample['pred'] = pred[i]
            sample['true'] = true[i]
            sample['text'] = ' '.join(sample['words'])
            output_line = json.dumps(sample)
            output_lines.append(output_line)
        file_utils.write_lines(output_lines, output_filepath)


class SpanBasedModelForMultiRelationClassificationBert(SpanBasedModelForMultiRelationClassification):
    """
    2019-acl-Open-Domain Targeted Sentiment Analysisvia Span-Based Extraction and Classification
    """

    def __init__(self, configuration):
        self.bert_file_path = configuration['bert_file_path']
        self.bert_vocab_file_path = configuration['bert_vocab_file_path']
        self.max_len = configuration['max_len']
        super().__init__(configuration)

    def _get_data_reader(self):
        token_indexer = SingleIdTokenIndexer(namespace="tokens")
        position_indexer = SingleIdTokenIndexer(namespace='position')
        bert_tokenizer = BertTokenizer.from_pretrained(self.bert_vocab_file_path, do_lower_case=True)
        bert_token_indexer = WordpieceIndexer(vocab=bert_tokenizer.vocab,
                                              wordpiece_tokenizer=bert_tokenizer.wordpiece_tokenizer.tokenize,
                                              namespace="bert",
                                              use_starting_offsets=False,
                                              max_pieces=self.max_len,
                                              do_lowercase=True,
                                              never_lowercase=None,
                                              start_tokens=None,
                                              end_tokens=None,
                                              separator_token="[SEP]",
                                              truncate_long_sequences=True)
        reader = relation_classification_data_reader.MultiRelationClassificationBertDatasetReader(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration,
            bert_tokenizer=bert_tokenizer,
            bert_token_indexers={"bert": bert_token_indexer}
        )
        return reader

    def _find_model_function_pure(self):
        return pytorch_models.SpanBasedModelForMultiRCBert

    def _get_estimator(self, model):
        USE_GPU = torch.cuda.is_available()
        if USE_GPU:
            gpu_id = self.configuration['gpu_id']
        else:
            gpu_id = -1
        estimator = pytorch_models.SpanBasedModelForMultiRCEstimator(model, self.val_iterator, self.distinct_polarities,
                                                                     cuda_device=gpu_id, configuration=self.configuration)
        return estimator

    def _get_bert_word_embedder(self):
        pretrained_model = self.bert_file_path
        bert_model = PretrainedBertModel.load(pretrained_model, cache_model=False)
        for param in bert_model.parameters():
            param.requires_grad = (not self.configuration['fixed_bert'])
        bert_embedder = BertEmbedder(bert_model=bert_model, top_layer_only=True)

        bert_word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"bert": bert_embedder},
                                                                       # we'll be ignoring masks so we'll need to set this to True
                                                                       allow_unmatched_keys=True)
        bert_word_embedder.to(self.configuration['device'])
        return bert_word_embedder

    def _find_model_function(self):
        embedding_dim = self.configuration['embed_size']
        embedding_matrix_filepath = self.base_data_dir + 'embedding_matrix'
        if os.path.exists(embedding_matrix_filepath):
            embedding_matrix = super()._load_object(embedding_matrix_filepath)
        else:
            embedding_filepath = self.configuration['embedding_filepath']
            embedding_matrix = embedding._read_embeddings_from_text_file(embedding_filepath, embedding_dim,
                                                                         self.vocab, namespace='tokens')
            super()._save_object(embedding_matrix_filepath, embedding_matrix)
        token_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='tokens'),
                                    embedding_dim=embedding_dim, padding_index=0, vocab_namespace='tokens',
                                    trainable=False, weight=embedding_matrix)
        # the embedder maps the input tokens to the appropriate embedding matrix
        word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"tokens": token_embedding})

        position_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='position'),
                                       embedding_dim=self._get_position_embeddings_dim(), padding_index=0)
        position_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"position": position_embedding},
                                                                      # we'll be ignoring masks so we'll need to set this to True
                                                                      allow_unmatched_keys=True)

        bert_word_embedder = self._get_bert_word_embedder()

        model_function = self._find_model_function_pure()
        model = model_function(
            word_embedder,
            position_embedder,
            self.distinct_polarities,
            self.vocab,
            self.configuration,
            bert_word_embedder=bert_word_embedder
        )

        self._print_args(model)
        model = model.to(self.configuration['device'])
        return model

    def _get_optimizer(self, model):
        _params = filter(lambda p: p.requires_grad, model.parameters())
        if self.configuration['fixed_bert']:
            return optim.Adam(_params, lr=0.001, weight_decay=0.00001)
        else:
            return optim.Adam(_params, lr=self.configuration['learning_rate_in_bert'],
                              weight_decay=self.configuration['l2_in_bert'])

    def _get_position_embeddings_dim(self):
        return self.configuration['position_embeddings_dim']


class SpanBasedBertModelForAtsa(SpanBasedModelForRelationClassification):
    """
    LSTM
    """

    def __init__(self, configuration):
        self.bert_file_path = configuration['bert_file_path']
        self.bert_vocab_file_path = configuration['bert_vocab_file_path']
        self.max_len = configuration['max_len']
        super().__init__(configuration)

    def _find_model_function_pure(self):
        return pytorch_models.SpanBasedBertModel

    def _get_word_segmenter(self):
        word_segmenter = tokenizers.AllennlpBertTokenizer(self.bert_vocab_file_path)
        return word_segmenter

    def _get_data_reader(self):
        bert_tokenizer = self._get_word_segmenter()
        bert_token_indexer = WordpieceIndexer(vocab=bert_tokenizer.bert_tokenizer.vocab,
                                              wordpiece_tokenizer=bert_tokenizer.bert_tokenizer.wordpiece_tokenizer.tokenize,
                                              namespace="tokens",
                                              use_starting_offsets=False,
                                              max_pieces=self.max_len,
                                              do_lowercase=True,
                                              never_lowercase=None,
                                              start_tokens=None,
                                              end_tokens=None,
                                              separator_token="[SEP]",
                                              truncate_long_sequences=True)
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = atsa_data_reader.TextAspectInSentimentOutForBert(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": bert_token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )

        return reader

    def _get_bert_word_embedder(self):
        pretrained_model = self.bert_file_path
        bert_model = PretrainedBertModel.load(pretrained_model, cache_model=False)
        for param in bert_model.parameters():
            param.requires_grad = self.configuration['train_bert']
        bert_embedder = BertEmbedder(bert_model=bert_model, top_layer_only=True)

        bert_word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"tokens": bert_embedder},
                                                                       # we'll be ignoring masks so we'll need to set this to True
                                                                       allow_unmatched_keys=True)
        return bert_word_embedder

    def _find_model_function(self):
        position_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='position'),
                                    embedding_dim=25, padding_index=0)
        position_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"position": position_embedding},
                                                                    # we'll be ignoring masks so we'll need to set this to True
                                                                    allow_unmatched_keys=True)

        bert_word_embedder = self._get_bert_word_embedder()

        model_function = self._find_model_function_pure()
        model = model_function(
            bert_word_embedder,
            position_embedder,
            self.distinct_polarities,
            self.vocab,
            self.configuration,
        )
        self._print_args(model)
        model = model.to(self.configuration['device'])
        return model

    def _get_optimizer(self, model):
        _params = filter(lambda p: p.requires_grad, model.parameters())
        return optim.Adam(_params, lr=self.configuration['learning_rate_in_bert'], weight_decay=0.00001)


class AtsaBERT(SpanBasedModelForRelationClassification):
    """
    LSTM
    """

    def __init__(self, configuration):
        self.bert_file_path = configuration['bert_file_path']
        self.bert_vocab_file_path = configuration['bert_vocab_file_path']
        self.max_len = configuration['max_len']
        super().__init__(configuration)

    def _find_model_function_pure(self):
        return pytorch_models.AtsaBERT

    def _get_word_segmenter(self):
        word_segmenter = tokenizers.AllennlpBertTokenizer(self.bert_vocab_file_path)
        return word_segmenter

    def _get_data_reader(self):
        bert_tokenizer = self._get_word_segmenter()
        bert_token_indexer = WordpieceIndexer(vocab=bert_tokenizer.bert_tokenizer.vocab,
                                              wordpiece_tokenizer=bert_tokenizer.bert_tokenizer.wordpiece_tokenizer.tokenize,
                                              namespace="tokens",
                                              use_starting_offsets=False,
                                              max_pieces=self.max_len,
                                              do_lowercase=True,
                                              never_lowercase=None,
                                              start_tokens=None,
                                              end_tokens=None,
                                              separator_token="[SEP]",
                                              truncate_long_sequences=True)
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = atsa_data_reader.TextAspectInSentimentOutForAtsaBert(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": bert_token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )

        return reader

    def _get_bert_word_embedder(self):
        pretrained_model = self.bert_file_path
        bert_model = PretrainedBertModel.load(pretrained_model, cache_model=False)
        for param in bert_model.parameters():
            param.requires_grad = self.configuration['train_bert']
        bert_embedder = BertEmbedder(bert_model=bert_model, top_layer_only=True)

        bert_word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"tokens": bert_embedder},
                                                                       # we'll be ignoring masks so we'll need to set this to True
                                                                       allow_unmatched_keys=True)
        return bert_word_embedder

    def _find_model_function(self):
        position_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='position'),
                                    embedding_dim=25, padding_index=0)
        position_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"position": position_embedding},
                                                                    # we'll be ignoring masks so we'll need to set this to True
                                                                    allow_unmatched_keys=True)

        bert_word_embedder = self._get_bert_word_embedder()

        model_function = self._find_model_function_pure()
        model = model_function(
            bert_word_embedder,
            position_embedder,
            self.distinct_polarities,
            self.vocab,
            self.configuration,
        )
        self._print_args(model)
        model = model.to(self.configuration['device'])
        return model

    def _get_optimizer(self, model):
        _params = filter(lambda p: p.requires_grad, model.parameters())
        if not self.configuration['train_bert']:
            return optim.Adam(_params, lr=0.001, weight_decay=0.00001)
        else:
            return optim.Adam(_params, lr=self.configuration['learning_rate_in_bert'],
                              weight_decay=0.00001)


class AtsaLSTM(SpanBasedModelForRelationClassification):
    """
    LSTM
    """

    def __init__(self, configuration):
        self.bert_file_path = configuration['bert_file_path']
        self.bert_vocab_file_path = configuration['bert_vocab_file_path']
        self.max_len = configuration['max_len']
        super().__init__(configuration)

    def _find_model_function_pure(self):
        return pytorch_models.SpanBasedModel

    def _get_data_reader(self):
        token_indexer = SingleIdTokenIndexer(namespace="tokens")
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = atsa_data_reader.TextAspectInSentimentOutForAtsaLSTM(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )

        return reader


class SyntaxAwareSpanBasedBertModelForAtsa(SpanBasedModelForRelationClassification):
    """
    LSTM
    """

    def __init__(self, configuration):
        self.bert_file_path = configuration['bert_file_path']
        self.bert_vocab_file_path = configuration['bert_vocab_file_path']
        self.max_len = configuration['max_len']
        super().__init__(configuration)

    def _find_model_function_pure(self):
        return pytorch_models.SyntaxAwareSpanBasedBertModel

    def _get_word_segmenter(self):
        word_segmenter = tokenizers.AllennlpBertTokenizer(self.bert_vocab_file_path)
        return word_segmenter

    def _get_data_reader(self):
        bert_tokenizer = self._get_word_segmenter()
        bert_token_indexer = WordpieceIndexer(vocab=bert_tokenizer.bert_tokenizer.vocab,
                                              wordpiece_tokenizer=bert_tokenizer.bert_tokenizer.wordpiece_tokenizer.tokenize,
                                              namespace="tokens",
                                              use_starting_offsets=False,
                                              max_pieces=self.max_len,
                                              do_lowercase=True,
                                              never_lowercase=None,
                                              start_tokens=None,
                                              end_tokens=None,
                                              separator_token="[SEP]",
                                              truncate_long_sequences=True)
        position_indexer = SingleIdTokenIndexer(namespace='position')
        reader = atsa_data_reader.TextAspectInSentimentOutForSyntaxAwareBert(
            self.distinct_polarities,
            tokenizer=self._get_word_segmenter(),
            token_indexers={"tokens": bert_token_indexer},
            position_indexers={'position': position_indexer},
            configuration=self.configuration
        )

        return reader

    def _get_bert_word_embedder(self):
        pretrained_model = self.bert_file_path
        bert_model = PretrainedBertModel.load(pretrained_model, cache_model=False)
        for param in bert_model.parameters():
            param.requires_grad = self.configuration['train_bert']
        bert_embedder = BertEmbedder(bert_model=bert_model, top_layer_only=True)

        bert_word_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"tokens": bert_embedder},
                                                                       # we'll be ignoring masks so we'll need to set this to True
                                                                       allow_unmatched_keys=True)
        return bert_word_embedder

    def _find_model_function(self):
        position_embedding = Embedding(num_embeddings=self.vocab.get_vocab_size(namespace='position'),
                                    embedding_dim=25, padding_index=0)
        position_embedder: TextFieldEmbedder = BasicTextFieldEmbedder({"position": position_embedding},
                                                                    # we'll be ignoring masks so we'll need to set this to True
                                                                    allow_unmatched_keys=True)

        bert_word_embedder = self._get_bert_word_embedder()

        model_function = self._find_model_function_pure()
        model = model_function(
            bert_word_embedder,
            position_embedder,
            self.distinct_polarities,
            self.vocab,
            self.configuration,
        )
        self._print_args(model)
        model = model.to(self.configuration['device'])
        return model

    def _get_optimizer(self, model):
        _params = filter(lambda p: p.requires_grad, model.parameters())
        return optim.Adam(_params, lr=self.configuration['learning_rate_in_bert'], weight_decay=0.00001)
