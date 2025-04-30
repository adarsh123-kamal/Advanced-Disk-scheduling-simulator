Advanced Disk Scheduling Simulator 🎯
This is a Python-based GUI application designed to simulate and visualize various disk scheduling algorithms used in operating systems. It allows users to input custom disk access requests and compare the performance of algorithms like FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK in terms of seek time and throughput.

🧠 Features
📌 Interactive GUI using Tkinter

🔍 Supports six key scheduling algorithms:

FCFS (First-Come-First-Served)

SSTF (Shortest Seek Time First)

SCAN

C-SCAN

LOOK

C-LOOK

📈 Real-time visualization of disk head movement

📊 Displays performance metrics:

Total Seek Time

Average Seek Time

Throughput (requests/sec)

📁 Logs simulation results to a CSV file

🔁 Compare multiple algorithms in a single run

🚀 Getting Started
Prerequisites
Make sure you have Python 3.x installed. Install the required libraries:

bash
Copy
Edit
pip install matplotlib numpy
Run the Application
bash
Copy
Edit
python main.py
Replace main.py with the filename of your simulator (e.g., disk_simulator_gui.py).

