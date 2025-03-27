## AI PROCESS ANALYZER

**AI Process Analyzer** is a Python-based desktop application designed to monitor system processes, provide AI-driven optimization suggestions, and forecast future resource usage. Built with Tkinter, it offers a user-friendly interface to analyze process performance, terminate or suspend high-resource processes, and leverage machine learning for system optimization.

## Features

- **Process Monitoring**:
  - Displays all running processes with PID, Name, CPU%, and Memory% usage.
  - Identifies terminable processes (CPU > 60% or Memory > 60%) with clickable "Kill" and "Suspend" actions.
- **AI-Based Optimization Suggestions**:
  - Uses K-means clustering to analyze historical process data and suggest optimization actions (e.g., terminate, suspend, or adjust priority).
- **Resource Forecasting**:
  - Predicts CPU and memory usage 5 minutes ahead using linear regression, based on real-time system data.
- **Tabbed Interface**:
  - Two tabs: "Process Monitoring" for live process management and "Advanced Analytics" for AI insights.

## Requirements

- **Operating System**: Linux (tested on Fedora), potentially compatible with Windows/Mac with minor adjustments.
- **Python**: 3.13 or higher.
- **Dependencies**:
  - `psutil`: For system process monitoring.
  - `pandas`: For data manipulation.
  - `scikit-learn`: For machine learning (K-means and linear regression).
  - `tkinter`: For the GUI (usually included with Python).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sourav-jyoti/ai-process-analyzer.git
   cd ai-process-analyzer

## working

- **Data Collection** : collect_data.py gathers process stats (PID, Name, CPU%, Memory%) for 5 minutes, saved as process_data.csv.
- **Clustering** : train_model.py applies K-means (3 clusters) to identify usage patterns, saving results in clustered_data.csv.
- **Monitoring** : monitor.py uses real-time data and the trained model to flag terminable processes and generate suggestions.
- **UI** : ui.py runs a background thread to collect data every 2 seconds, updating the GUI every 5 seconds with process info and forecasts.
