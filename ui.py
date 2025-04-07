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

# Tab 3: System Overview
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="System Overview")

overview_frame = ttk.LabelFrame(tab3, text="System Resource Usage")
overview_frame.pack(fill="both", expand=True, padx=5, pady=5)

cpu_label = ttk.Label(overview_frame, text="CPU Usage: ")
cpu_label.pack(anchor="w", padx=10)

mem_label = ttk.Label(overview_frame, text="Memory Usage: ")
mem_label.pack(anchor="w", padx=10)

chart_frame = ttk.Frame(overview_frame)
chart_frame.pack(fill="both", expand=True)

fig, ax = plt.subplots(figsize=(6, 4))
bar_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
bar_canvas.get_tk_widget().pack(fill="both", expand=True)

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

    root.after(5000, update_ui)

def update_overview():
    if live_data:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        cpu_label.config(text=f"CPU Usage: {cpu:.1f}%")
        mem_label.config(text=f"Memory Usage: {mem:.1f}%")

        sorted_procs = sorted(live_data, key=lambda x: x[2], reverse=True)[:5]
        names = [p[1] for p in sorted_procs]
        cpu_vals = [p[2] for p in sorted_procs]
        mem_vals = [p[3] for p in sorted_procs]

        ax.clear()
        ax.barh(names, cpu_vals, color='steelblue', label='CPU %')
        ax.barh(names, mem_vals, color='orange', left=cpu_vals, label='Memory %')
        ax.set_xlabel("Usage (%)")
        ax.set_title("Top 5 Processes by CPU and Memory")
        ax.legend()
        ax.invert_yaxis()
        fig.tight_layout()
        bar_canvas.draw()
    root.after(5000, update_overview)

update_ui()
update_overview()
root.mainloop()
