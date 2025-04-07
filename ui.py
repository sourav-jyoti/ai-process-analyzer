import tkinter as tk
from tkinter import ttk
import psutil
from monitor import monitor_processes, get_advanced_optimization_suggestions
import threading
import time
from sklearn.linear_model import LinearRegression
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# UI Setup
root = tk.Tk()
root.title("AI Process Analyzer")
root.geometry("800x600")
root.resizable(True, True)

# Apply custom style for colorful tabs
style = ttk.Style()
style.theme_use('default')

style.configure('TNotebook.Tab', background='#D6EAF8', foreground='black', padding=[10, 5])
style.map('TNotebook.Tab',
          background=[('selected', '#5DADE2')],
          foreground=[('selected', 'white')])

# Create notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Tab 1: Process Monitoring
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Process Monitoring")

frame1 = ttk.LabelFrame(tab1, text="All Running Processes")
frame1.pack(fill="both", expand=True, padx=5, pady=5)

scrollbar1 = ttk.Scrollbar(frame1, orient="vertical")
tree1 = ttk.Treeview(frame1, columns=('PID', 'Name', 'CPU%', 'Memory%'), show='headings', yscrollcommand=scrollbar1.set)
scrollbar1.config(command=tree1.yview)
scrollbar1.pack(side="right", fill="y")
tree1.pack(fill="both", expand=True)

for col in ('PID', 'Name', 'CPU%', 'Memory%'):
    tree1.heading(col, text=col)
    tree1.column(col, width=100)

def refresh_scrollbar():
    tree1.update()
    scrollbar1.set(0, 1.0)

refresh_button = ttk.Button(frame1, text="Refresh Scrollbar", command=refresh_scrollbar)
refresh_button.pack(side="bottom", pady=5)

frame2 = ttk.LabelFrame(tab1, text="Terminable Processes")
frame2.pack(fill="both", expand=True, padx=5, pady=5)

action_label = ttk.Label(frame2, text="Click on 'Kill' or 'Suspend' to perform the action")
action_label.pack(side="top")

tree2 = ttk.Treeview(frame2, columns=('PID', 'Name', 'CPU%', 'Memory%', 'Kill', 'Suspend'), show='headings')
for col in ('PID', 'Name', 'CPU%', 'Memory%', 'Kill', 'Suspend'):
    tree2.heading(col, text=col)
    tree2.column(col, width=100 if col != 'Suspend' else 120)
tree2.pack(fill="both", expand=True)

def on_treeview_click(event):
    item = tree2.identify_row(event.y)
    column = tree2.identify_column(event.x)
    if item and column:
        col_index = int(column[1:]) - 1
        if col_index == 4:
            pid = tree2.item(item, 'values')[0]
            kill_process(int(pid))
        elif col_index == 5:
            pid = tree2.item(item, 'values')[0]
            suspend_process(int(pid))

tree2.bind('<Button-1>', on_treeview_click)

# Tab 2: Advanced Analytics
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Advanced Analytics")

suggestion_frame = ttk.LabelFrame(tab2, text="AI-Based Optimization Suggestions")
suggestion_frame.pack(fill="both", expand=True, padx=5, pady=5)
suggestion_text = tk.Text(suggestion_frame, height=10)
suggestion_text.pack(fill="both", expand=True)

forecast_frame = ttk.LabelFrame(tab2, text="Resource Forecasting")
forecast_frame.pack(fill="both", expand=True, padx=5, pady=5)
forecast_text = tk.Text(forecast_frame, height=10)
forecast_text.pack(fill="both", expand=True)

# Tab 3: System Overview
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="System Overview")

cpu_label = ttk.Label(tab3, text="CPU Usage: Calculating...", font=("Arial", 12))
cpu_label.pack(pady=5)
mem_label = ttk.Label(tab3, text="Memory Usage: Calculating...", font=("Arial", 12))
mem_label.pack(pady=5)

fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=tab3)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True)

# Global data storage
live_data = []
terminable_data = []
system_data = []
forecast_result = {
    "cpu_pred": None,
    "mem_pred": None,
    "cpu_slope": None,
    "mem_slope": None,
    "last_updated": None
}

def collect_data():
    global live_data, terminable_data, system_data
    while True:
        live_data, terminable_data = monitor_processes()
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        timestamp = time.time()
        system_data.append((timestamp, cpu, mem))
        if len(system_data) > 150:
            system_data.pop(0)
        time.sleep(2)

def forecast_resources():
    global forecast_result
    while True:
        if len(system_data) >= 10:
            timestamps, cpus, mems = zip(*system_data)
            timestamps = np.array(timestamps).reshape(-1, 1)
            future_time = np.array([[time.time() + 300]])
            cpu_model = LinearRegression().fit(timestamps, cpus)
            mem_model = LinearRegression().fit(timestamps, mems)
            forecast_result = {
                "cpu_pred": cpu_model.predict(future_time)[0],
                "mem_pred": mem_model.predict(future_time)[0],
                "cpu_slope": cpu_model.coef_[0] * 60,
                "mem_slope": mem_model.coef_[0] * 60,
                "last_updated": time.strftime('%H:%M:%S')
            }
        time.sleep(30)

threading.Thread(target=collect_data, daemon=True).start()
threading.Thread(target=forecast_resources, daemon=True).start()

def kill_process(pid):
    try:
        psutil.Process(pid).terminate()
        print(f"Killed process with PID {pid}")
    except Exception as e:
        print(f"Error killing PID {pid}: {e}")

def suspend_process(pid):
    try:
        psutil.Process(pid).suspend()
        print(f"Suspended process with PID {pid}")
    except Exception as e:
        print(f"Error suspending PID {pid}: {e}")

def update_ui():
    tree1.delete(*tree1.get_children())
    for proc in live_data:
        tree1.insert('', 'end', values=proc)

    tree2.delete(*tree2.get_children())
    for proc in terminable_data:
        pid, name, cpu, mem = proc
        values = (pid, name, f"{cpu:.1f}", f"{mem:.1f}", "Kill", "Suspend")
        tree2.insert('', 'end', values=values)

    suggestions = get_advanced_optimization_suggestions()
    suggestion_text.delete(1.0, tk.END)
    if suggestions and suggestions[0] != "No data available for optimization suggestions.":
        suggestion_text.insert(tk.END, "AI-Based Optimization Suggestions:\n")
        for i, sug in enumerate(suggestions, 1):
            suggestion_text.insert(tk.END, f"{i}. {sug}\n")
    else:
        suggestion_text.insert(tk.END, "No optimization suggestions available at this time.")

    forecast_text.delete(1.0, tk.END)
    if forecast_result["cpu_pred"] is not None:
        forecast_text.insert(tk.END, "Resource Forecast (Next 5 Minutes):\n")
        forecast_text.insert(tk.END, f"Predicted CPU Usage: {forecast_result['cpu_pred']:.2f}%\n")
        forecast_text.insert(tk.END, f"CPU Trend: {'+' if forecast_result['cpu_slope'] > 0 else ''}{forecast_result['cpu_slope']:.2f}%/min\n")
        forecast_text.insert(tk.END, f"Predicted Memory Usage: {forecast_result['mem_pred']:.2f}%\n")
        forecast_text.insert(tk.END, f"Memory Trend: {'+' if forecast_result['mem_slope'] > 0 else ''}{forecast_result['mem_slope']:.2f}%/min\n")
        forecast_text.insert(tk.END, f"Last Updated: {forecast_result['last_updated']}")
    else:
        forecast_text.insert(tk.END, "Collecting data for forecasting...")

    if live_data:
        top5 = sorted(live_data, key=lambda x: x[2] + x[3], reverse=True)[:5]
        labels = [f"{p[1]} ({p[0]})" for p in top5]
        usage = [p[2] + p[3] for p in top5]
        ax.clear()
        ax.barh(labels, usage, color='#5DADE2')
        ax.set_xlabel('Combined CPU% + Memory%')
        ax.set_title('Top 5 Resource-Consuming Processes')
        canvas.draw()

        cpu_label.config(text=f"CPU Usage: {psutil.cpu_percent()}%")
        mem_label.config(text=f"Memory Usage: {psutil.virtual_memory().percent}%")

    root.after(5000, update_ui)

update_ui()
root.mainloop()
