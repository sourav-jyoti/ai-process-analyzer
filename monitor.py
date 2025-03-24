import psutil
import pandas as pd
from sklearn.cluster import KMeans
import time

# Load the clustered data and train the K-means model
df = pd.read_csv('clustered_data.csv')
kmeans = KMeans(n_clusters=3, random_state=42).fit(df[['CPU%', 'Memory%']])

# Identify the high-usage cluster based on the highest average CPU usage
cluster_centers = kmeans.cluster_centers_
high_usage_cluster = cluster_centers[:, 0].argmax()  # CPU% is the first column

# List of critical processes that should not be terminated
critical_processes = ['systemd', 'dbus', 'NetworkManager', 'sshd', 'kernel']

def is_terminable(proc_name, cpu, mem):
    """
    Determine if a process is terminable based on its name and resource usage.

    Args:
        proc_name (str): Name of the process.
        cpu (float): CPU usage percentage.
        mem (float): Memory usage percentage.

    Returns:
        bool: True if the process is terminable, False otherwise.
    """
    # Process is terminable if it's not critical and exceeds usage thresholds
    return proc_name not in critical_processes and (cpu > 60 or mem > 60)

def monitor_processes():
    """
    Monitor running processes and categorize them into live and terminable lists.

    Returns:
        tuple: (live_data, terminable_data)
            - live_data: List of [pid, name, cpu, mem] for all processes.
            - terminable_data: List of [pid, name, cpu, mem] for terminable processes.
    """
    live_data = []
    terminable_data = []

    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu = proc.cpu_percent(interval=0.1)  # Measure over a short interval
            mem = proc.info['memory_percent']

            # Predict the cluster for this process's resource usage
            pred_df = pd.DataFrame([[cpu, mem]], columns=['CPU%', 'Memory%'])
            cluster = kmeans.predict(pred_df)[0]

            # Check if the process has a baseline in the clustered data
            baseline = df[df['Name'] == name]
            if not baseline.empty:
                normal_cluster = baseline['Cluster'].mode()[0]
                # Consider it an anomaly if cluster differs and usage is notable
                anomaly = cluster != normal_cluster and (cpu > 30 or mem > 30)
            else:
                anomaly = True  # New process with no baseline

            # Add to live data
            live_data.append([pid, name, cpu, mem])

            # Add to terminable data if it meets the criteria
            if is_terminable(name, cpu, mem):
                terminable_data.append([pid, name, cpu, mem])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue  # Skip processes that disappear or are inaccessible

    return live_data, terminable_data

def get_advanced_optimization_suggestions():
    """
    Generate AI-based optimization suggestions based on clustered process data.

    Returns:
        list: Up to 4 optimization suggestions as strings.
    """
    try:
        # Reload the clustered data (for fresh analysis)
        df = pd.read_csv('clustered_data.csv')

        # Calculate how often each process is in the high-usage cluster
        process_usage = df.groupby('Name')['Cluster'].apply(
            lambda x: (x == high_usage_cluster).mean()
        )
        # Select processes that are in the high-usage cluster more than 50% of the time
        high_usage_procs = process_usage[process_usage > 0.5].index.tolist()

        suggestions = []
        for proc_name in high_usage_procs[:4]:  # Limit to 4 processes
            if proc_name not in critical_processes:
                # Compute average CPU and memory usage for the process
                proc_data = df[df['Name'] == proc_name]
                avg_cpu = proc_data['CPU%'].mean()
                avg_mem = proc_data['Memory%'].mean()

                # Tiered suggestions based on usage levels
                if avg_cpu > 80 or avg_mem > 80:
                    suggestions.append(
                        f"Terminate '{proc_name}' (Avg CPU: {avg_cpu:.1f}%, Mem: {avg_mem:.1f}%) - Excessive resource usage."
                    )
                elif avg_cpu > 50 or avg_mem > 50:
                    suggestions.append(
                        f"Suspend '{proc_name}' (Avg CPU: {avg_cpu:.1f}%, Mem: {avg_mem:.1f}%) - High resource demand."
                    )
                else:
                    suggestions.append(
                        f"Adjust priority of '{proc_name}' (Avg CPU: {avg_cpu:.1f}%, Mem: {avg_mem:.1f}%) - Moderate usage."
                    )

        # Ensure at least 3 suggestions by adding a generic one if needed
        if len(suggestions) < 3:
            suggestions.append("Review background processes for potential resource leaks.")

        return suggestions[:4]  # Return up to 4 suggestions
    except FileNotFoundError:
        return ["No data available for optimization suggestions."]

if __name__ == "__main__":
    # Test the monitoring functionality in a loop
    while True:
        live, term = monitor_processes()
        print("Live Processes:", live)
        print("Terminable Processes:", term)
        time.sleep(2)  # Wait 2 seconds between iterations