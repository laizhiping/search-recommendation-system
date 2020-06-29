import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import h5py

cls_data = []
cls_path = 'feature_set_new/feature_set.h5'
with h5py.File(cls_path, 'r') as f:
    fset = f['feature_set']
    tset = f['token_set']
    lset = f['label_set']
    cla_data = fset[:]
    y_ = lset[:]

pca = PCA(n_components=2)
vectors_ = pca.fit_transform(cla_data)   # 降维到二维

plt.scatter(vectors_[:, 0], vectors_[:, 1], c=y_)
plt.show()