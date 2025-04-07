import psutil
import pandas as pd
from sklearn.cluster import KMeans
import time
import threading

# Load the clustered data and train the K-means model once
try:
    df = pd.read_csv('clustered_data.csv')
    kmeans = KMeans(n_clusters=3, random_state=42).fit(df[['CPU%', 'Memory%']])
    cluster_centers = kmeans.cluster_centers_
    high_usage_cluster = cluster_centers[:, 0].argmax()  # CPU% is the first column
except FileNotFoundError:
    df = pd.DataFrame(columns=['Name', 'CPU%', 'Memory%', 'Cluster'])
    kmeans = None
    high_usage_cluster = 0

# List of critical processes that should not be terminated
critical_processes = ['systemd', 'dbus', 'NetworkManager', 'sshd', 'kernel']

def is_terminable(proc_name, cpu, mem):
    return proc_name not in critical_processes and (cpu > 60 or mem > 60)

# Background data cache to avoid repeated heavy calls
_cached_data = {
    'live_data': [],
    'terminable_data': [],
    'last_update': 0
}
_cache_lock = threading.Lock()

CACHE_TTL = 2  # seconds


def monitor_processes():
    now = time.time()
    with _cache_lock:
        if now - _cached_data['last_update'] < CACHE_TTL:
            return _cached_data['live_data'], _cached_data['terminable_data']

    live_data = []
    terminable_data = []

    all_procs = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))

    # Prime CPU readings without delay
    for proc in all_procs:
        try:
            proc.cpu_percent(interval=None)
        except Exception:
            continue

    time.sleep(0.1)  # Let CPU stats settle slightly

    process_info = []
    for proc in all_procs:
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu = proc.cpu_percent(interval=None)
            mem = proc.info['memory_percent']
            process_info.append((pid, name, cpu, mem))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if kmeans:
        usage_array = pd.DataFrame([[cpu, mem] for (_, _, cpu, mem) in process_info], columns=['CPU%', 'Memory%'])
        clusters = kmeans.predict(usage_array)
    else:
        clusters = [0] * len(process_info)

    for i, (pid, name, cpu, mem) in enumerate(process_info):
        cluster = clusters[i]
        baseline = df[df['Name'] == name] if not df.empty else pd.DataFrame()
        if not baseline.empty:
            normal_cluster = baseline['Cluster'].mode()[0]
            anomaly = cluster != normal_cluster and (cpu > 30 or mem > 30)
        else:
            anomaly = True

        live_data.append([pid, name, cpu, mem])

        if is_terminable(name, cpu, mem):
            terminable_data.append([pid, name, cpu, mem])

    with _cache_lock:
        _cached_data['live_data'] = live_data
        _cached_data['terminable_data'] = terminable_data
        _cached_data['last_update'] = time.time()

    return live_data, terminable_data

def get_advanced_optimization_suggestions():
    try:
        # Use already-loaded df instead of reloading every time
        if df.empty:
            return ["No data available for optimization suggestions."]

        process_usage = df.groupby('Name')['Cluster'].apply(
            lambda x: (x == high_usage_cluster).mean()
        )
        high_usage_procs = process_usage[process_usage > 0.5].index.tolist()

        suggestions = []
        for proc_name in high_usage_procs[:4]:
            if proc_name not in critical_processes:
                proc_data = df[df['Name'] == proc_name]
                avg_cpu = proc_data['CPU%'].mean()
                avg_mem = proc_data['Memory%'].mean()

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

        if len(suggestions) < 3:
            suggestions.append("Review background processes for potential resource leaks.")

        return suggestions[:4]
    except Exception:
        return ["Error generating optimization suggestions."]

if __name__ == "__main__":
    while True:
        live, term = monitor_processes()
        print("Live Processes:", live)
        print("Terminable Processes:", term)
        time.sleep(2)  # Wait 2 seconds between iterations