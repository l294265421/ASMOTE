# The code and data for the paper "Aspect-Sentiment-Multiple-Opinion Triplet Extraction"

# Requirements
- Python 3.6.8
- torch==1.2.0
- pytorch-transformers==1.1.0
- allennlp==0.9.0

# Instructions:
. Before excuting the following commands, replace glove.840B.300d.txt(http://nlp.stanford.edu/data/wordvecs/glove.840B.300d.zip), bert-base-uncased.tar.gz(https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased.tar.gz) and vocab.txt(https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased-vocab.txt) with the corresponding absolute paths in your computer. 

# ASMOTE
## ATE
scripts/ate.asmote-data.multi_run.sh

## TOWE
scripts/towe.asmote-data.multi_run.sh

## TOWE inference
scripts/towe.asmote-data.multi_run.predict.sh

## ATSA
scripts/atsa.asmote-data.multi_run.sh

## AGF
scripts/asmote.asmote-data.multi_run.sh

## AGF inference
scripts/asmote.asmote-data.multi_run.predict_test.sh

## evaluate
scripts/evaluate.sh
