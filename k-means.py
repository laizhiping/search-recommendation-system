from sklearn.cluster import KMeans
from sklearn import metrics
import h5py

cls_data = []
cls_path = 'feature_set/feature_set.h5'
with h5py.File(cls_path, 'r') as f:
    fset = f['feature_set']
    tset = f['token_set']
    cla_data = fset[:10000]

data = cla_data

for n_cluster in range(30)[0:-1]:
    # n_cluster = 18
    print("cluster:", n_cluster)
    kmeans = KMeans(n_clusters=n_cluster, init='k-means++')
    kmeans.fit_predict(data)  # 聚类
    label_pred = kmeans.labels_  # 获取聚类标签 [0,2,2,3...]
    centroids = kmeans.cluster_centers_  # 获取聚类中心
    print(centroids)
    chs = metrics.calinski_harabasz_score(data, label_pred)
    print("chs:", chs)
    dbi = metrics. davies_bouldin_score(data, label_pred)
    print("dbi:", dbi)

with h5py.File(cls_path, 'a') as f:
    # del f['label_set']
    # del f['center_set']
    f.create_dataset('center_set', data=centroids)

with h5py.File('label_set.h5', 'w') as f:
    f.create_dataset('label_set', data=label_pred)