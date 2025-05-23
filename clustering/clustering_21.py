# -*- coding: utf-8 -*-

import pandas as pd

df = pd.read_csv("/content/household_power_consumption.csv")

df.head()

df.shape

df.isnull().sum()

df['Sub_metering_3'].describe()

df["Sub_metering_3"].value_counts()

df.fillna(df["Sub_metering_3"].mean(), inplace = True)
df.isnull().sum()

df.info()

import numpy as np

df = df.replace('?', np.nan)

try:
  df['Global_active_power'] = pd.to_numeric(df['Global_active_power'])
  df['Global_reactive_power'] = pd.to_numeric(df['Global_reactive_power'])
  df['Voltage'] = pd.to_numeric(df['Voltage'])
  df['Global_intensity'] = pd.to_numeric(df['Global_intensity'])
  df['Sub_metering_1'] = pd.to_numeric(df['Sub_metering_1'])
  df['Sub_metering_2'] = pd.to_numeric(df['Sub_metering_2'])
except:
  pass

print(df.head().to_markdown(index=False, numalign="left", stralign="left"))

df.info()

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

cols_to_scale = ['Global_active_power', 'Global_reactive_power', 'Voltage',
                 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2']

df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

print(df.head().to_markdown(index=False, numalign="left", stralign="left"))
df.info()

import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

sample_size = 1000
df_sample = df.sample(n=sample_size, random_state=42)

cols_for_clustering = ['Global_active_power', 'Global_reactive_power', 'Voltage',
                       'Global_intensity', 'Sub_metering_1', 'Sub_metering_2']
X = df_sample[cols_for_clustering]


linkage_methods = ['single', 'complete', 'average', 'ward']

plt.figure(figsize=(15, 10))

for i, method in enumerate(linkage_methods):
    linked = linkage(X, method)

    plt.subplot(2, 2, i + 1)
    dendrogram(linked,
               orientation='top',
               distance_sort='descending',
               show_leaf_counts=True)
    plt.title(f"Dendrogram ({method} linkage)")

plt.tight_layout()
plt.show()

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

inertia = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(8, 6))
plt.plot(range(1, 11), inertia, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.show()



kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df_sample['cluster'] = kmeans.fit_predict(X)


plt.figure(figsize=(8, 6))
plt.scatter(df_sample['Global_active_power'], df_sample['Global_reactive_power'], c=df_sample['cluster'], cmap='viridis')
plt.xlabel('Global_active_power')
plt.ylabel('Global_reactive_power')
plt.title(f'KMeans Clustering with k={optimal_k}')
plt.colorbar(label='Cluster')
plt.show()

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors


sample_size = 1000
df_sample = df.sample(n=sample_size, random_state=42)
X = df_sample[cols_for_clustering]


def k_distance_graph(X, k):
    neigh = NearestNeighbors(n_neighbors=k)
    nbrs = neigh.fit(X)
    distances, indices = nbrs.kneighbors(X)
    k_distances = distances[:, -1]
    k_distances = np.sort(k_distances, axis=0)
    return k_distances


k = 4
k_distances = k_distance_graph(X, k)
plt.plot(k_distances)
plt.xlabel("Points sorted by distance")
plt.ylabel("k-distances")
plt.title(f"k-distance graph (k={k})")
plt.show()



min_pts_values = [4, 5, 6]
epsilon_values = [0.1, 0.2, 0.3]

for min_pts in min_pts_values:
    for epsilon in epsilon_values:
        dbscan = DBSCAN(eps=epsilon, min_samples=min_pts)
        df_sample[f'cluster_dbscan_{min_pts}_{epsilon}'] = dbscan.fit_predict(X)

        plt.figure(figsize=(8, 6))
        plt.scatter(df_sample['Global_active_power'], df_sample['Global_reactive_power'], c=df_sample[f'cluster_dbscan_{min_pts}_{epsilon}'], cmap='viridis')
        plt.xlabel('Global_active_power')
        plt.ylabel('Global_reactive_power')
        plt.title(f'DBSCAN Clustering (MinPts={min_pts}, epsilon={epsilon})')
        plt.colorbar(label='Cluster')
        plt.show()

        print(f"MinPts: {min_pts}, Epsilon: {epsilon}")
        print(df_sample[f'cluster_dbscan_{min_pts}_{epsilon}'].value_counts())

from sklearn.metrics import silhouette_score


kmeans_silhouette = silhouette_score(X, df_sample['cluster'])
print(f"Silhouette score for KMeans: {kmeans_silhouette}")


for min_pts in min_pts_values:
    for epsilon in epsilon_values:
        cluster_labels = df_sample[f'cluster_dbscan_{min_pts}_{epsilon}']

        if len(set(cluster_labels)) > 1:
            dbscan_silhouette = silhouette_score(X, cluster_labels)
            print(f"Silhouette score for DBSCAN (MinPts={min_pts}, epsilon={epsilon}): {dbscan_silhouette}")
        else:
            print(f"Silhouette score cannot be calculated for DBSCAN (MinPts={min_pts}, epsilon={epsilon}) because there is only one cluster or all points are noise")



from scipy.cluster.hierarchy import fcluster


distance_threshold = 0.5
cluster_labels_hierarchical = fcluster(linked, distance_threshold, criterion='distance') # Assuming 'linked' is calculated as in your previous code for hierarchical clustering



if len(set(cluster_labels_hierarchical)) > 1:
  hierarchical_silhouette = silhouette_score(X, cluster_labels_hierarchical)
  print(f"Silhouette score for Hierarchical Clustering: {hierarchical_silhouette}")
else:
  print("Silhouette score cannot be calculated for Hierarchical Clustering because there is only one cluster")

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


def visualize_clusters(X, labels, method='pca', title=None):
    if method == 'pca':
        pca = PCA(n_components=2)
        X_transformed = pca.fit_transform(X)
    elif method == 'tsne':
        tsne = TSNE(n_components=2, random_state=42)
        X_transformed = tsne.fit_transform(X)
    else:
        raise ValueError("Invalid visualization method. Choose 'pca' or 'tsne'.")

    plt.figure(figsize=(8, 6))
    plt.scatter(X_transformed[:, 0], X_transformed[:, 1], c=labels, cmap='viridis')
    plt.xlabel(f"{method.upper()} Component 1")
    plt.ylabel(f"{method.upper()} Component 2")
    if title:
        plt.title(title)
    else:
        plt.title(f'Cluster Visualization ({method.upper()})')
    plt.colorbar(label='Cluster')
    plt.show()



visualize_clusters(X, df_sample['cluster'], method='pca', title='KMeans Clustering (PCA)')
visualize_clusters(X, df_sample['cluster'], method='tsne', title='KMeans Clustering (t-SNE)')

for min_pts in min_pts_values:
    for epsilon in epsilon_values:
        cluster_labels = df_sample[f'cluster_dbscan_{min_pts}_{epsilon}']
        visualize_clusters(X, cluster_labels, method='pca', title=f'DBSCAN Clustering (MinPts={min_pts}, epsilon={epsilon}, PCA)')
        visualize_clusters(X, cluster_labels, method='tsne', title=f'DBSCAN Clustering (MinPts={min_pts}, epsilon={epsilon}, t-SNE)')



if len(set(cluster_labels_hierarchical)) > 1:
    visualize_clusters(X, cluster_labels_hierarchical, method='pca', title='Hierarchical Clustering (PCA)')
    visualize_clusters(X, cluster_labels_hierarchical, method='tsne', title='Hierarchical Clustering (t-SNE)')
else:
    print("Hierarchical clustering visualization skipped: Only one cluster found")

