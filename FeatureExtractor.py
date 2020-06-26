import re
import sys
import numpy as np
import tensorflow as tf
import transformers as trsfm
import time
import h5py

BATCH_SIZE = 64
test_batch_size = 256
TOP_K = 10
data_path = 'G:\\data\\sogou\\SogouQ.reduced'
feature_set_path = 'G:\\data\\sogou\\feature_set_new\\feature_set.h5'

tokenizer = trsfm.BertTokenizer.from_pretrained('bert-base-chinese')
model = trsfm.TFBertModel.from_pretrained('bert-base-chinese')


def build_dataset(data_path):
    n = 0
    data = []
    rgx = re.compile(r'[^\w\u4e00-\u9fa5]+')
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            keyword = line.split('\t')[2][1:-1]
            keyword = rgx.sub(' ', keyword).strip()
            data.append(keyword)
            n += 1
            sys.stdout.write('\r')
            sys.stdout.write('processing: {}'.format(n))
            sys.stdout.flush() 
    print('\n')
    n = 0
    with open('data_sougou.csv', 'w', encoding='utf-8') as f:
        for x in data:
            enc = tokenizer.encode(x)
            f.write(str(enc)[1:-1])
            f.write('\n')
            n += 1
            sys.stdout.write('\r')
            sys.stdout.write('writing: {}'.format(n))
            sys.stdout.flush()
    print('\n')


def preprocess(s):
    s = s.numpy().decode('UTF-8')
    list_of_s = s.split(', ')
    list_of_s = [int(x) for x in list_of_s]
    return tf.cast(list_of_s, tf.int32)


def tf_preprocess(s):
    result = tf.py_function(preprocess, [s], tf.int32)
    result.set_shape([None])
    return result


def getFeatureVector(s):
    rgx = re.compile(r'[^\w\u4e00-\u9fa5]+')
    s = rgx.sub(' ', s).strip()
    x = tokenizer.encode(s, return_tensors='tf')
    if x.shape[1] < 7:
        x = tf.concat([x, tf.zeros((1, 7 - x.shape[1]), dtype='int32')], axis=1)
    output, _ = model(x)
    return output[:, 0, :]


def build_feature_set():
    with open('data_sougou.csv', 'r', encoding='utf-8') as f:
        data_list = f.readlines()
    test_dataset = tf.data.Dataset.from_tensor_slices(data_list)
    test_dataset = test_dataset.map(tf_preprocess, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    test_dataset = test_dataset.padded_batch(BATCH_SIZE, padded_shapes=(-1,))
    n = 0
    with h5py.File(feature_set_path, "w") as f:
        fset = f.create_dataset("feature_set", (0, 768), dtype='float32', maxshape=(None, 768), chunks=(64, 768))
        tset = f.create_dataset("token_set", (0,), dtype=h5py.string_dtype(), maxshape=(None,), chunks=(64,))
        for x in test_dataset:
            size = x.shape[0]
            fset.resize(fset.shape[0] + size, axis=0)
            tset.resize(tset.shape[0] + size, axis=0)
            out, _ = model(x)
            out = out[:, 0, :]
            fset[-size:] = out
            token_str_list = [str(list(filter(lambda x: x != 0, list(line.numpy()))))[1:-1] for line in x]
            tset[-size:] = token_str_list
            n += 1
            sys.stdout.write('\r')
            sys.stdout.write('processing: {}'.format(n))
            sys.stdout.flush()
        print('\n')


signature = [
    tf.TensorSpec(shape=(None, 768), dtype=tf.float32),
    tf.TensorSpec(shape=(1, 768), dtype=tf.float32)
]
@tf.function(input_signature=signature)
def cal_similarity(his, query):
    norm_history = tf.norm(his, axis=1)
    norm_query = tf.norm(query)
    similary = tf.squeeze(tf.matmul(his, tf.transpose(query))) / (norm_history * norm_query)
    return similary


def sort_and_unique(lst):
    result_lst = []
    seen = set()
    for item in lst:
        if item[1] not in seen:
            result_lst.append(item)
            seen.add(item[1])
    return sorted(result_lst, key=lambda x: -x[0])


def find_cluster(query, center_set):
    min_dis = 1e9
    cluster_id = -1
    for c in enumerate(center_set):
        dis = np.linalg.norm(query.numpy() - c[1])
        if dis < min_dis:
            min_dis = dis
            cluster_id = c[0]
    return cluster_id


class Feature_set_loader:
    feature_set = None
    token_set = None
    label_set = None
    center_set = None
    loaded = False
    path = feature_set_path

    def __init__(self):
        pass

    @classmethod
    def load_feature_set(cls):
        if not cls.loaded:
            with h5py.File(cls.path, "r") as f:
                # deploy code
                # fset = f['feature_set']
                # tset = f['token_set']
                # lset = f['label_set']
                # cset = f['center_set']
                # test code
                fset = f['feature_set'][:22500]
                tset = f['token_set'][:22500]
                lset = f['label_set'][:22500]
                cset = f['center_set'][:22500]
                cls.feature_set = np.array(fset)
                cls.token_set = np.array(tset)
                cls.label_set = np.array(lset)
                cls.center_set = np.array(cset)

            cls.loaded = True
            print('feature set loaded: {}'.format(cls.path))


def do_query(s_query):
    # load dataset
    if not Feature_set_loader.loaded:
        Feature_set_loader.load_feature_set()
    feature_set = Feature_set_loader.feature_set
    token_set = Feature_set_loader.token_set
    label_set = Feature_set_loader.label_set
    center_set = Feature_set_loader.center_set
    result = []
    query = getFeatureVector(s_query)
    # select search range
    cluster_id = find_cluster(query, center_set)
    search_id = np.where(label_set == cluster_id)
    feature_set = feature_set[search_id]
    token_set = token_set[search_id]
    # start searching
    num_of_batches = feature_set.shape[0] // test_batch_size + 1
    for b in range(num_of_batches):
        if b == num_of_batches - 1:
            his = feature_set[b * test_batch_size:]
        else:
            his = feature_set[b * test_batch_size: (b + 1) * test_batch_size]
        if len(his) == 0:
            continue
        similary = cal_similarity(his, query)
        max_id = np.argsort(similary)[-TOP_K:][::-1] + b * test_batch_size
        max_sim = np.sort(similary)[-TOP_K:][::-1]
        recommand_key = token_set[max_id]
        recommand_key = [x.split(', ') for x in recommand_key]
        recommand_key = [[int(i) for i in x] for x in recommand_key]
        recommand_key = [tokenizer.decode(x) for x in recommand_key]
        recommand_key = [re.compile('\[CLS\]|\[SEP\]|\[PAD\]|\[UNK\]').sub(' ', x).replace(' ', '') for x in recommand_key]
        recommand_key = list(zip(list(max_sim), recommand_key))
        result.extend(recommand_key)
        result = sort_and_unique(result)[:TOP_K]
    #     print('.', end='')
    # print('\n')
    # print(result)
    return result


if __name__ == '__main__':
    s = '北京'
    start = time.time()
    result = do_query(s)
    end = time.time()
    print(result)
    print("duration: {}".format(end - start))
