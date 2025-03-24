import tkinter as tk
from tkinter import ttk
import psutil
from monitor import monitor_processes, get_advanced_optimization_suggestions
import threading
import time
from sklearn.linear_model import LinearRegression
import numpy as np

# UI Setup
root = tk.Tk()
root.title("AI Process Analyzer")
root.geometry("800x600")
root.resizable(True, True)

# Create notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Tab 1: Process Monitoring
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Process Monitoring")

# Section 1: All Processes
frame1 = ttk.LabelFrame(tab1, text="All Running Processes")
frame1.pack(fill="both", expand=True, padx=5, pady=5)

scrollbar1 = ttk.Scrollbar(frame1, orient="vertical")
tree1 = ttk.Treeview(frame1, columns=('PID', 'Name', 'CPU%', 'Memory%'), show='headings', yscrollcommand=scrollbar1.set)
scrollbar1.config(command=tree1.yview)
scrollbar1.pack(side="right", fill="y")
tree1.pack(fill="both", expand=True)

tree1.heading('PID', text='PID')
tree1.heading('Name', text='Name')
tree1.heading('CPU%', text='CPU%')
tree1.heading('Memory%', text='Memory%')
tree1.column('PID', width=100)
tree1.column('Name', width=200)
tree1.column('CPU%', width=100)
tree1.column('Memory%', width=100)

def refresh_scrollbar():
    tree1.update()
    scrollbar1.set(0, 1.0)

refresh_button = ttk.Button(frame1, text="Refresh Scrollbar", command=refresh_scrollbar)
refresh_button.pack(side="bottom", pady=5)

# Section 2: Terminable Processes
frame2 = ttk.LabelFrame(tab1, text="Terminable Processes")
frame2.pack(fill="both", expand=True, padx=5, pady=5)

action_label = ttk.Label(frame2, text="Click on 'Kill' or 'Suspend' to perform the action")
action_label.pack(side="top")

tree2 = ttk.Treeview(frame2, columns=('PID', 'Name', 'CPU%', 'Memory%', 'Kill', 'Suspend'), show='headings')
tree2.heading('PID', text='PID')
tree2.heading('Name', text='Name')
tree2.heading('CPU%', text='CPU%')
tree2.heading('Memory%', text='Memory%')
tree2.heading('Kill', text='Kill')
tree2.heading('Suspend', text='Suspend')
tree2.column('PID', width=100)
tree2.column('Name', width=200)
tree2.column('CPU%', width=100)
tree2.column('Memory%', width=100)
tree2.column('Kill', width=50)
tree2.column('Suspend', width=70)
tree2.pack(fill="both", expand=True)

def on_treeview_click(event):
    item = tree2.identify_row(event.y)
    column = tree2.identify_column(event.x)
    if item and column:
        col_index = int(column[1:]) - 1  # Convert '#1' to 0, etc.
        if col_index == 4:  # Kill column
            pid = tree2.item(item, 'values')[0]
            kill_process(int(pid))
        elif col_index == 5:  # Suspend column
            pid = tree2.item(item, 'values')[0]
            suspend_process(int(pid))

tree2.bind('<Button-1>', on_treeview_click)

# Tab 2: Advanced Analytics
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Advanced Analytics")

# Section 1: AI-Based Optimization Suggestions
suggestion_frame = ttk.LabelFrame(tab2, text="AI-Based Optimization Suggestions")
suggestion_frame.pack(fill="both", expand=True, padx=5, pady=5)
suggestion_text = tk.Text(suggestion_frame, height=10)
suggestion_text.pack(fill="both", expand=True)

# Section 2: Resource Forecasting
forecast_frame = ttk.LabelFrame(tab2, text="Resource Forecasting")
forecast_frame.pack(fill="both", expand=True, padx=5, pady=5)
forecast_text = tk.Text(forecast_frame, height=10)
forecast_text.pack(fill="both", expand=True)

# Global data storage
live_data = []
terminable_data = []
system_data = []  # For forecasting: (timestamp, cpu_percent, mem_percent)

# Background data collection
def collect_data():
    global live_data, terminable_data, system_data
    while True:
        live_data, terminable_data = monitor_processes()
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        timestamp = time.time()
        system_data.append((timestamp, cpu, mem))
        if len(system_data) > 150:  # Keep last 5 minutes (150 points at 2-second intervals)
            system_data.pop(0)
        time.sleep(2)

# Start background thread
thread = threading.Thread(target=collect_data, daemon=True)
thread.start()

# Process control functions
def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        print(f"Killed process with PID {pid}")
    except Exception as e:
        print(f"Error killing PID {pid}: {e}")

def suspend_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.suspend()
        print(f"Suspended process with PID {pid}")
    except Exception as e:
        print(f"Error suspending PID {pid}: {e}")

# Update UI function
def update_ui():
    # Update Process Monitoring Tab
    tree1.delete(*tree1.get_children())
    for proc in live_data:
        tree1.insert('', 'end', values=proc)
    
    tree2.delete(*tree2.get_children())
    for proc in terminable_data:
        pid, name, cpu, mem = proc
        values = (pid, name, f"{cpu:.1f}", f"{mem:.1f}", "Kill", "Suspend")
        tree2.insert('', 'end', values=values)
    
    # Update Advanced Analytics Tab
    # AI-Based Optimization Suggestions
    suggestions = get_advanced_optimization_suggestions()
    suggestion_text.delete(1.0, tk.END)
    if suggestions and suggestions[0] != "No data available for optimization suggestions.":
        suggestion_text.insert(tk.END, "AI-Based Optimization Suggestions:\n")
        for i, sug in enumerate(suggestions, 1):
            suggestion_text.insert(tk.END, f"{i}. {sug}\n")
    else:
        suggestion_text.insert(tk.END, "No optimization suggestions available at this time.")
    
    # Resource Forecasting
    if len(system_data) >= 10:  # Need at least 10 points for a meaningful trend
        timestamps, cpus, mems = zip(*system_data)
        timestamps = np.array(timestamps).reshape(-1, 1)
        current_time = time.time()
        future_time = current_time + 300  # Predict 5 minutes ahead

        # CPU forecast
        cpu_model = LinearRegression().fit(timestamps, cpus)
        cpu_pred = cpu_model.predict([[future_time]])[0]
        cpu_slope = cpu_model.coef_[0] * 60  # Change per minute

        # Memory forecast
        mem_model = LinearRegression().fit(timestamps, mems)
        mem_pred = mem_model.predict([[future_time]])[0]
        mem_slope = mem_model.coef_[0] * 60  # Change per minute

        forecast_text.delete(1.0, tk.END)
        forecast_text.insert(tk.END, "Resource Forecast (Next 5 Minutes):\n")
        forecast_text.insert(tk.END, f"Predicted CPU Usage: {cpu_pred:.2f}%\n")
        forecast_text.insert(tk.END, f"CPU Trend: {'+' if cpu_slope > 0 else ''}{cpu_slope:.2f}% per minute\n")
        forecast_text.insert(tk.END, f"Predicted Memory Usage: {mem_pred:.2f}%\n")
        forecast_text.insert(tk.END, f"Memory Trend: {'+' if mem_slope > 0 else ''}{mem_slope:.2f}% per minute\n")
    else:
        forecast_text.delete(1.0, tk.END)
        forecast_text.insert(tk.END, "Collecting data for forecasting...")

    root.after(5000, update_ui)  # Update every 5 seconds

# Start UI updates
update_ui()
root.mainloop()