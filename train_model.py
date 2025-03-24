import pandas as pd
from sklearn.cluster import KMeans

def train_model():
    # Load baseline data
    df = pd.read_csv('process_data.csv')
    
    # Use only CPU% and Memory% for clustering
    X = df[['CPU%', 'Memory%']].values
    
    # Train K-means with 3 clusters (tuned for simplicity and accuracy)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)  # n_init=10 for better accuracy
    df['Cluster'] = kmeans.fit_predict(X)
    
    # Save clustered data
    df.to_csv('clustered_data.csv', index=False)
    print("K-means model trained and clustered data saved to clustered_data.csv")

if __name__ == "__main__":
    train_model()