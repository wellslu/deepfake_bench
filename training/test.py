"""
eval pretained model.
"""
<<<<<<< HEAD
import os
=======
# import os
>>>>>>> f0246d710cdd7eefe366ae2322d33ecbed1ce8a4
import numpy as np
from os.path import join
import cv2
import random
<<<<<<< HEAD
import datetime
import time
import yaml
import pickle
from tqdm import tqdm
from copy import deepcopy
from PIL import Image as pil_image
from metrics.utils import get_test_metrics
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.nn.functional as F
import torch.utils.data
import torch.optim as optim

from dataset.abstract_dataset import DeepfakeAbstractBaseDataset
from dataset.ff_blend import FFBlendDataset
from dataset.fwa_blend import FWABlendDataset
from dataset.pair_dataset import pairDataset

from trainer.trainer import Trainer
from detectors import DETECTOR
from metrics.base_metrics_class import Recorder
from collections import defaultdict
=======
# import datetime
# import time
import yaml
# import pickle
from tqdm import tqdm
from copy import deepcopy
# from PIL import Image as pil_image
from metrics.utils import get_test_metrics
import torch
# import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
# import torch.nn.functional as F
import torch.utils.data
# import torch.optim as optim

from dataset.abstract_dataset import DeepfakeAbstractBaseDataset
# from dataset.ff_blend import FFBlendDataset
# from dataset.fwa_blend import FWABlendDataset
# from dataset.pair_dataset import pairDataset

# from trainer.trainer import Trainer
from detectors import DETECTOR
# from metrics.base_metrics_class import Recorder
# from collections import defaultdict
>>>>>>> f0246d710cdd7eefe366ae2322d33ecbed1ce8a4

import argparse
from logger import create_logger

parser = argparse.ArgumentParser(description='Process some paths.')
parser.add_argument('--detector_path', type=str, 
<<<<<<< HEAD
                    default='./training/config/detector/xception.yaml',
                    help='path to detector YAML file')
parser.add_argument("--test_dataset", nargs="+")
parser.add_argument('--weights_path', type=str, 
                    default=None)
=======
                    default='/home/zhiyuanyan/DeepfakeBench/training/config/detector/resnet34.yaml',
                    help='path to detector YAML file')
parser.add_argument("--test_dataset", nargs="+")
parser.add_argument('--weights_path', type=str, 
                    default='/mntcephfs/lab_data/zhiyuanyan/benchmark_results/auc_draw/cnn_aug/resnet34_2023-05-20-16-57-22/test/FaceForensics++/ckpt_epoch_9_best.pth')
>>>>>>> f0246d710cdd7eefe366ae2322d33ecbed1ce8a4
#parser.add_argument("--lmdb", action='store_true', default=False)
args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def init_seed(config):
    if config['manualSeed'] is None:
        config['manualSeed'] = random.randint(1, 10000)
    random.seed(config['manualSeed'])
    torch.manual_seed(config['manualSeed'])
    if config['cuda']:
        torch.cuda.manual_seed_all(config['manualSeed'])


def prepare_testing_data(config):
    def get_test_data_loader(config, test_name):
        # update the config dictionary with the specific testing dataset
        config = config.copy()  # create a copy of config to avoid altering the original one
        config['test_dataset'] = test_name  # specify the current test dataset
        test_set = DeepfakeAbstractBaseDataset(
                config=config,
                mode='test', 
            )
        test_data_loader = \
            torch.utils.data.DataLoader(
                dataset=test_set, 
                batch_size=config['test_batchSize'],
                shuffle=False, 
<<<<<<< HEAD
                num_workers=int(config['workers']),
=======
                # num_workers=int(config['workers']),
>>>>>>> f0246d710cdd7eefe366ae2322d33ecbed1ce8a4
                collate_fn=test_set.collate_fn,
                drop_last=False
            )
        return test_data_loader

    test_data_loaders = {}
    for one_test_name in config['test_dataset']:
        test_data_loaders[one_test_name] = get_test_data_loader(config, one_test_name)
    return test_data_loaders


def choose_metric(config):
    metric_scoring = config['metric_scoring']
    if metric_scoring not in ['eer', 'auc', 'acc', 'ap']:
        raise NotImplementedError('metric {} is not implemented'.format(metric_scoring))
    return metric_scoring


def test_one_dataset(model, data_loader, feature_target=None):
    prediction_lists = []
    feature_lists = []
    label_lists = []
    for i, data_dict in tqdm(enumerate(data_loader), total=len(data_loader)):
        # get data
        data, label, mask, landmark = \
        data_dict['image'], data_dict['label'], data_dict['mask'], data_dict['landmark']
        label = torch.where(data_dict['label'] != 0, 1, 0)
        # move data to GPU
        data_dict['image'], data_dict['label'] = data.to(device), label.to(device)
        if mask is not None:
            data_dict['mask'] = mask.to(device)
        if landmark is not None:
            data_dict['landmark'] = landmark.to(device)

        # model forward without considering gradient computation
        predictions = inference(model, data_dict, feature_target=feature_target)
        label_lists += list(data_dict['label'].cpu().detach().numpy())
        prediction_lists += list(predictions['prob'].cpu().detach().numpy())
        feature_lists += list(predictions['feat'].cpu().detach().numpy())
    
    if feature_target is not None:
        feature_target['labels'] += label_lists

    return np.array(prediction_lists), np.array(label_lists),np.array(feature_lists)
    
def test_epoch(model, test_data_loaders, feature_target=None):
    # set model to eval mode
    model.eval()

    # define test recorder
    metrics_all_datasets = {}

    # testing for all test data
    keys = test_data_loaders.keys()
    print(f"Testing on datasets: {keys}")
    for i, key in enumerate(keys):
        data_dict = test_data_loaders[key].dataset.data_dict
        # compute loss for each dataset
        predictions_nps, label_nps,feat_nps = test_one_dataset(model, test_data_loaders[key], feature_target=feature_target)
        
        # compute metric for each dataset
        metric_one_dataset = get_test_metrics(y_pred=predictions_nps, y_true=label_nps,
                                              img_names=data_dict['image'])
        metrics_all_datasets[key] = metric_one_dataset
        
        # info for each dataset
        tqdm.write(f"dataset: {key}")
        for k, v in metric_one_dataset.items():
            tqdm.write(f"{k}: {v}")

    return metrics_all_datasets

@torch.no_grad()
def inference(model, data_dict, feature_target=None):
    predictions = model(data_dict, inference=True, feature_target=feature_target)
    return predictions


def main():
    # parse options and load config
    with open(args.detector_path, 'r') as f:
        config = yaml.safe_load(f)
    with open('./training/config/test_config.yaml', 'r') as f:
        config2 = yaml.safe_load(f)
    config.update(config2)
    if 'label_dict' in config:
        config2['label_dict']=config['label_dict']
    weights_path = None
    # If arguments are provided, they will overwrite the yaml settings
    if args.test_dataset:
        config['test_dataset'] = args.test_dataset
<<<<<<< HEAD
    if args.weights_path is not None:
        config['weights_path'] = args.weights_path
        weights_path = args.weights_path
    elif 'weights_path' in config:
        print('Using weights_path from config:', config['weights_path'])
        weights_path = config['weights_path']
    else:
        weights_path = None
=======
    if args.weights_path:
        config['weights_path'] = args.weights_path
        weights_path = args.weights_path
>>>>>>> f0246d710cdd7eefe366ae2322d33ecbed1ce8a4
    
    # init seed
    init_seed(config)

    # set cudnn benchmark if needed
    if config['cudnn']:
        cudnn.benchmark = True

    # prepare the testing data loader
    test_data_loaders = prepare_testing_data(config)
    
    # prepare the model (detector)
    model_class = DETECTOR[config['model_name']]
    model = model_class(config).to(device)

    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.current_device()} ({torch.cuda.get_device_name(torch.cuda.current_device())})")

    epoch = 0
    if weights_path:
        try:
            epoch = int(weights_path.split('/')[-1].split('.')[0].split('_')[2])
        except:
            epoch = 0
        ckpt = torch.load(weights_path, map_location=device)
        model.load_state_dict(ckpt, strict=True)
        print('===> Load checkpoint done!')
    else:
        print('Fail to load the pre-trained weights')
    
    # start testing
    feature_vectors = {
        "vectors": [],
        "labels": []
    }

    best_metric = test_epoch(model, test_data_loaders, feature_target=feature_vectors)

    model_name = weights_path.split('/')[-1].split('.')[0] if weights_path else 'model'

    # save feature_vectors to a pickle file for later use
    with open(f"logs/{model_name}_feature_vectors.pkl", 'wb') as f:
        pickle.dump(feature_vectors, f)

    print('===> Test Done!')

if __name__ == '__main__':
    main()
