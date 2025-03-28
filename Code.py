import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# Loading the data
file_path = "Full_DB.xlsx" # Using the football database I made in another project
df = pd.read_excel(file_path, engine="openpyxl")
X = df.iloc[:, 11:].dropna(axis=1)  # To remove the informations not needed to create new metrics


# Standardizing the data 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# Performing PCA
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

optimal_pcs = np.argmax(cumulative_variance >= 0.80) + 1  # Find the number of PCs explaining 80% variance
print(f"Optimal number of PCs: {optimal_pcs}")


# Variance Explained Plot
def plot_scree(cumulative_variance):
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, marker='o', linestyle='--',
             label="Cumulative Variance")
    plt.axhline(y=0.80, color='r', linestyle='--', label="80% Threshold")
    plt.xlabel('Number of Principal Components')
    plt.ylabel('Cumulative Explained Variance')
    plt.title('Scree Plot')
    plt.legend()
    plt.show()


plot_scree(cumulative_variance)


# Variance explained by each PC
variance_df = pd.DataFrame({
    "PC": [f"PC{i + 1}" for i in range(len(explained_variance))],
    "Explained Variance": explained_variance * 100,  
    "Cumulative Variance": cumulative_variance * 100
})
print(variance_df.head(optimal_pcs))  

loadings = pd.DataFrame(pca.components_, columns=X.columns, index=[f'PC{i + 1}' for i in range(len(pca.components_))])

top_n = 20
for i in range(optimal_pcs):
    print(f"\nTop Variables for {loadings.index[i]}:")
    print(loadings.iloc[i, :].abs().sort_values(ascending=False).head(top_n))


# Elbow and Silhouette Method for clustering
def optimal_k_clusters(X_pca, range_k=range(2, 11)):
    wcss = []  # Within-cluster sum of squares
    silhouette_scores = []  # Silhouette scores for cluster evaluation

    for k in range_k:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_pca[:, :optimal_pcs])  # Use first 'optimal_pcs' principal components
        wcss.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_pca[:, :optimal_pcs], kmeans.labels_))

    # Elbow plot
    plt.figure(figsize=(8, 5))
    plt.plot(range_k, wcss, marker='o', linestyle='--')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
    plt.title('Elbow Method')
    plt.show()

    # Silhouette score plot
    plt.figure(figsize=(8, 5))
    plt.plot(range_k, silhouette_scores, marker='o', linestyle='--')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Silhouette Score')
    plt.title('Silhouette Scores for Different Numbers of Clusters')
    plt.show()

    optimal_clusters = range_k[np.argmax(silhouette_scores)]
    print(f"Optimal Number of Clusters: {optimal_clusters}")
    return optimal_clusters, silhouette_scores


optimal_clusters, _ = optimal_k_clusters(X_pca)


kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
labels = kmeans.fit_predict(X_pca[:, :optimal_pcs])

pca_cluster_df = pd.DataFrame(X_pca[:, :optimal_pcs], columns=[f"PC{i + 1}" for i in range(optimal_pcs)])
pca_cluster_df['Cluster'] = labels


# Compute mean and variance of each PC per cluster
pc_cluster_means = pca_cluster_df.groupby('Cluster').mean()
pc_cluster_variance = pc_cluster_means.var(axis=0).sort_values(ascending=False)


# Display the top PCs that influence clustering the most
print("Top PCs influencing the clusters the most:")
print(pc_cluster_variance.head(5))


# Plot the clustering based on the first two principal components
plt.figure(figsize=(8, 5))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis')
plt.title('Clustering based on PCA components (PC1 vs. PC2)')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.colorbar(label='Cluster')
plt.show()

