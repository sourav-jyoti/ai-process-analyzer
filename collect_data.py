import psutil
import time
import pandas as pd

def collect_data(duration_minutes=5):
    data = []
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)  # Stop after exact duration
    print(f"Starting data collection for {duration_minutes} minutes...")

    try:
        while time.time() < end_time:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc.cpu_percent(interval=0.1)  # Small interval for accuracy
                    data.append([proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], proc.info['memory_percent']])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(2)  # Collect every 2 seconds to avoid resource hogging
            
            # Save incrementally every minute to avoid data loss
            if int(time.time() - start_time) % 60 == 0:
                df = pd.DataFrame(data, columns=['PID', 'Name', 'CPU%', 'Memory%'])
                df.to_csv('process_data.csv', index=False)
                print(f"Progress: {int((time.time() - start_time) / 60)} minutes, {len(data)} rows collected")

    except KeyboardInterrupt:
        print("Data collection interrupted by user.")
    
    # Final save
    df = pd.DataFrame(data, columns=['PID', 'Name', 'CPU%', 'Memory%'])
    df.to_csv('process_data.csv', index=False)
    print(f"Data collection stopped. Saved {len(df)} rows to process_data.csv")

if __name__ == "__main__":
    collect_data(5)  # Run for 5 minutes