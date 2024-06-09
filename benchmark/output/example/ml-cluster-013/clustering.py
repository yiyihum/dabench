import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load the dataset
data = pd.read_csv('/workspace/Country-data.csv')

# Drop the 'country' column as it's not a feature to be used in clustering
features = data.drop('country', axis=1)

# Standardize the features
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Determine the optimal number of clusters using the elbow method
inertia = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, random_state=42)
    kmeans.fit(features_scaled)
    inertia.append(kmeans.inertia_)

# Find the elbow point, which is where the inertia starts to decrease more slowly
elbow_point = next(x[0] for x in enumerate(inertia[1:], 1) if abs(inertia[x[0]] - inertia[x[0] - 1]) < abs(inertia[x[0] - 1] - inertia[x[0] - 2]))

# Perform K-Means clustering with the optimal number of clusters
kmeans = KMeans(n_clusters=elbow_point, random_state=42)
clusters = kmeans.fit_predict(features_scaled)

# Create a DataFrame with the cluster results
clustered_data = pd.DataFrame(features_scaled, columns=[f'Feature_{i+1}' for i in range(features_scaled.shape[1])])
clustered_data['Cluster'] = clusters

# Save the clustering results to 'cluster.csv'
clustered_data.to_csv('/workspace/cluster.csv', index=False)
