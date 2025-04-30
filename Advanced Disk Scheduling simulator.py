import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

class ToolTip:
    """Enhanced tooltip class with better positioning and styling"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        """Display the tooltip with a slight delay"""
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=('tahoma', '8', 'normal'), padx=5, pady=5,
                        wraplength=250)
        label.pack()

    def hide_tip(self, event=None):
        """Destroy the tooltip window"""
        if self.tw:
            self.tw.destroy()
            self.tw = None

class DiskScheduler:
    """Implements disk scheduling algorithms with optimized calculations"""
    def __init__(self, requests, head, max_track):
        self.requests = requests.copy()
        self.head = head
        self.max_track = max_track
        self.validate_inputs()

    def validate_inputs(self):
        """Validate inputs upon initialization"""
        if not isinstance(self.requests, list) or not all(isinstance(r, int) for r in self.requests):
            raise ValueError("Requests must be a list of integers")
        if not isinstance(self.head, int) or not isinstance(self.max_track, int):
            raise ValueError("Head and max track must be integers")
        if self.head < 0 or self.head > self.max_track:
            raise ValueError(f"Head position must be between 0 and {self.max_track}")
        if any(r < 0 or r > self.max_track for r in self.requests):
            raise ValueError(f"All requests must be between 0 and {self.max_track}")

    def _split_requests(self):
        """Optimized request splitting with numpy for large datasets"""
        requests = np.array(self.requests)
        left = np.sort(requests[requests < self.head])[::-1]  # Descending
        right = np.sort(requests[requests >= self.head])      # Ascending
        return left.tolist(), right.tolist()

    def _calculate_seek_time(self, sequence):
        """Vectorized seek time calculation"""
        sequence = np.array(sequence)
        return np.sum(np.abs(sequence[1:] - sequence[:-1]))

    def fcfs(self):
        """First-Come-First-Served with input validation"""
        if not self.requests:
            return [self.head], 0
        sequence = [self.head] + self.requests
        return sequence, self._calculate_seek_time(sequence)

    def sstf(self):
        """Shortest Seek Time First with early termination"""
        if not self.requests:
            return [self.head], 0
            
        sequence = [self.head]
        pending = self.requests.copy()
        current = self.head
        seek_time = 0
        
        while pending:
            distances = [abs(current - r) for r in pending]
            min_idx = np.argmin(distances)
            closest = pending.pop(min_idx)
            seek_time += distances[min_idx]
            current = closest
            sequence.append(current)
            
        return sequence, seek_time

    def scan(self, direction="left"):
        """SCAN algorithm with configurable direction"""
        if not self.requests:
            return [self.head], 0
            
        left, right = self._split_requests()
        
        if direction == "left":
            sequence = [self.head] + left + [0] + right
        else:
            sequence = [self.head] + right + [self.max_track] + left
            
        return sequence, self._calculate_seek_time(sequence)

    def cscan(self):
        """Circular SCAN with optimized endpoint handling"""
        if not self.requests:
            return [self.head], 0
            
        left, right = self._split_requests()
        sequence = [self.head] + right + [self.max_track, 0] + left
        return sequence, self._calculate_seek_time(sequence)

    def look(self, direction="left"):
        """LOOK algorithm with direction control"""
        if not self.requests:
            return [self.head], 0
            
        left, right = self._split_requests()
        
        if direction == "left":
            sequence = [self.head] + left + right
        else:
            sequence = [self.head] + right + left
            
        return sequence, self._calculate_seek_time(sequence)

    def clook(self):
        """Circular LOOK with efficient request grouping"""
        if not self.requests:
            return [self.head], 0
            
        left, right = self._split_requests()
        sequence = [self.head] + right + left
        return sequence, self._calculate_seek_time(sequence)

    def calculate_metrics(self, seek_time, time_scale=1000):
        """Enhanced metrics calculation with edge case handling"""
        if not self.requests:
            return 0, 0
            
        avg_seek = seek_time / len(self.requests)
        throughput = len(self.requests) / (seek_time / time_scale) if seek_time > 0 else float('inf')
        return avg_seek, throughput

class DiskSchedulingApp:
    """Main application class with modern UI and enhanced features"""
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_styles()
        self.setup_ui()
        self.initialize_csv()
        self.animations = []
        self.comparison_mode = False

    def setup_window(self):
        """Configure main window properties"""
        self.root.title("Advanced Disk Scheduling Simulator")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg='#f0f0f0')
        
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        position_right = int(self.root.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.root.winfo_screenheight()/2 - window_height/2)
        self.root.geometry(f"+{position_right}+{position_down}")

    def create_styles(self):
        """Create modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9), padding=5)
        style.configure('TEntry', font=('Consolas', 9), padding=5)
        style.configure('TCombobox', font=('Segoe UI', 9))
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Result.TText', font=('Consolas', 9), background='white')

    def setup_ui(self):
        """Setup all UI components"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_input_section(main_frame)
        self.create_results_section(main_frame)
        self.create_visualization_section(main_frame)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                 anchor=tk.W, style='TLabel').pack(fill=tk.X, side=tk.BOTTOM)

    def create_input_section(self, parent):
        """Create input controls section"""
        input_frame = ttk.LabelFrame(parent, text=" Simulation Parameters ", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Disk Requests:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_requests = ttk.Entry(input_frame, width=60)
        self.entry_requests.grid(row=0, column=1, columnspan=3, padx=5, pady=2, sticky="we")
        ToolTip(self.entry_requests, "Enter space-separated track numbers (e.g., 98 183 37 122 14 124)")

        ttk.Label(input_frame, text="Initial Head:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_head = ttk.Entry(input_frame, width=10)
        self.entry_head.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.entry_head.insert(0, "50")

        ttk.Label(input_frame, text="Max Track:").grid(row=1, column=2, sticky="w", pady=2)
        self.entry_max_track = ttk.Entry(input_frame, width=10)
        self.entry_max_track.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        self.entry_max_track.insert(0, "200")

        ttk.Label(input_frame, text="Algorithm:").grid(row=2, column=0, sticky="w", pady=2)
        self.algorithm_var = tk.StringVar(value="FCFS")
        algorithms = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
        self.algorithm_menu = ttk.Combobox(input_frame, textvariable=self.algorithm_var,
                                          values=algorithms, state="readonly", width=15)
        self.algorithm_menu.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        ToolTip(self.algorithm_menu, "Select disk scheduling algorithm to simulate")

        ttk.Label(input_frame, text="Direction:").grid(row=2, column=2, sticky="w", pady=2)
        self.direction_var = tk.StringVar(value="left")
        ttk.Radiobutton(input_frame, text="Left", variable=self.direction_var, value="left").grid(row=2, column=3, sticky="w", padx=5)
        ttk.Radiobutton(input_frame, text="Right", variable=self.direction_var, value="right").grid(row=2, column=3, sticky="e", padx=5)

        ttk.Label(input_frame, text="Time Scale (ms):").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_time_scale = ttk.Entry(input_frame, width=10)
        self.entry_time_scale.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.entry_time_scale.insert(0, "1000")
        ToolTip(self.entry_time_scale, "Time scale for throughput calculation (milliseconds)")

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky="we")

        ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run All Algorithms", command=self.run_all_algorithms).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Algorithm Info", command=self.show_algorithm_info).pack(side=tk.RIGHT, padx=5)

    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text=" Results ", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.output_text = tk.Text(results_frame, height=8, wrap=tk.WORD, font=('Consolas', 9),
                                 bg='white', fg='black', padx=5, pady=5)
        scrollbar = ttk.Scrollbar(results_frame, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def create_visualization_section(self, parent):
        """Create visualization section with matplotlib canvas"""
        vis_frame = ttk.LabelFrame(parent, text=" Visualization ", padding="10")
        vis_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor='#f8f8f8')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_facecolor('#f8f8f8')
        self.ax.set_xlabel("Track Number", fontsize=10)
        self.ax.set_ylabel("Step", fontsize=10)
        self.ax.set_title("Disk Head Movement", fontsize=11, pad=10)

    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        try:
            with open("disk_scheduling_results.csv", mode="x", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Algorithm", "Requests", "Initial Head",
                                "Max Track", "Seek Sequence", "Total Seek Time",
                                "Average Seek Time", "Throughput (req/sec)"])
        except FileExistsError:
            pass

    def validate_inputs(self):
        """Validate all user inputs with detailed error messages"""
        try:
            requests = list(map(int, self.entry_requests.get().split()))
            head = int(self.entry_head.get())
            max_track = int(self.entry_max_track.get())
            time_scale = int(self.entry_time_scale.get())

            if not requests:
                raise ValueError("Request sequence cannot be empty")
            if head < 0 or head > max_track:
                raise ValueError(f"Head position must be between 0 and {max_track}")
            if any(r < 0 or r > max_track for r in requests):
                raise ValueError(f"All requests must be between 0 and {max_track}")
            if time_scale <= 0:
                raise ValueError("Time scale must be a positive number")

            return requests, head, max_track, time_scale

        except ValueError as e:
            raise ValueError(f"Invalid input: {str(e)}")

    def run_simulation(self, algorithms=None):
        """Run simulation for selected or all algorithms"""
        try:
            start_time = time.time()
            requests, head, max_track, time_scale = self.validate_inputs()
            algo_list = [self.algorithm_var.get()] if algorithms is None else algorithms
            direction = self.direction_var.get()

            self.clear_animations()  # Clear previous animations safely

            scheduler = DiskScheduler(requests, head, max_track)
            results = []

            for algo in algo_list:
                if algo == "FCFS":
                    seq, seek = scheduler.fcfs()
                elif algo == "SSTF":
                    seq, seek = scheduler.sstf()
                elif algo == "SCAN":
                    seq, seek = scheduler.scan(direction)
                elif algo == "C-SCAN":
                    seq, seek = scheduler.cscan()
                elif algo == "LOOK":
                    seq, seek = scheduler.look(direction)
                elif algo == "C-LOOK":
                    seq, seek = scheduler.clook()
                else:
                    continue

                avg_seek, throughput = scheduler.calculate_metrics(seek, time_scale)
                results.append((algo, seq, seek, avg_seek, throughput))

            self.display_results(results)
            self.visualize_movement(results)
            
            for algo, seq, seek, avg_seek, throughput in results:
                self.save_to_csv(algo, requests, head, max_track, seq, seek, avg_seek, throughput)

            elapsed = time.time() - start_time
            self.status_var.set(f"Completed {len(results)} simulations in {elapsed:.2f} seconds")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.status_var.set(f"Error: {str(e)}")

    def run_all_algorithms(self):
        """Run simulation for all available algorithms"""
        algorithms = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]
        self.run_simulation(algorithms)

    def display_results(self, results):
        """Display formatted results in the output text widget"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        
        for algo, seq, seek, avg_seek, throughput in results:
            seq_str = ' → '.join(map(str, seq[:10]))
            if len(seq) > 10:
                seq_str += f" → ... (total {len(seq)} steps)"
                
            result_text = (f"Algorithm: {algo: <8}\n"
                         f"Seek Sequence: {seq_str}\n"
                         f"Total Seek Time: {seek: <5}  "
                         f"Avg Seek Time: {avg_seek:.2f}\n"
                         f"Throughput: {throughput:.2f} requests/sec\n"
                         f"{'-'*50}\n")
            
            self.output_text.insert(tk.END, result_text)
        
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def save_to_csv(self, algorithm, requests, head, max_track, sequence, seek_time, avg_seek_time, throughput):
        """Save results to CSV with timestamp and all parameters"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("disk_scheduling_results.csv", mode="a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                algorithm,
                ' '.join(map(str, requests)),
                head,
                max_track,
                ' → '.join(map(str, sequence)),
                seek_time,
                round(avg_seek_time, 2),
                round(throughput, 2)
            ])

    def visualize_movement(self, results):
        """Enhanced visualization with multiple algorithm support"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_facecolor('#f8f8f8')
        self.ax.set_xlabel("Track Number", fontsize=10)
        self.ax.set_ylabel("Step", fontsize=10)
        
        all_sequences = [seq for _, seq, _, _, _ in results]
        max_track = max(max(seq) for seq in all_sequences) + 10 if all_sequences else 200
        max_steps = max(len(seq) for seq in all_sequences) if all_sequences else 10
        self.ax.set_xlim(0, max_track)
        self.ax.set_ylim(0, max_steps)
        
        colors = plt.cm.tab10.colors
        lines = []
        labels = []
        
        for i, (algo, seq, _, _, _) in enumerate(results):
            line, = self.ax.plot([], [], marker='o', linestyle='-', 
                                color=colors[i % len(colors)], 
                                linewidth=2, markersize=6, 
                                label=algo)
            lines.append(line)
            labels.append(algo)
        
        def update(frame):
            annotations = []
            for i, (_, seq, _, _, _) in enumerate(results):
                steps = min(frame + 1, len(seq))
                lines[i].set_data(seq[:steps], range(steps))
                
                if steps > 0:
                    x, y = seq[steps-1], steps-1
                    annotation = self.ax.annotate(f"{x}", (x, y), textcoords="offset points",
                                                 xytext=(0,5), ha='center', fontsize=8,
                                                 color=colors[i % len(colors)])
                    annotations.append(annotation)
            
            return lines + annotations
        
        if len(results) == 1:
            self.ax.set_title(f"{results[0][0]} Algorithm - Head Movement", fontsize=11)
        else:
            self.ax.set_title("Algorithm Comparison - Head Movement", fontsize=11)
            self.ax.legend(loc='upper right', fontsize=9)
        
        if results:
            max_frames = max(len(seq) for _, seq, _, _, _ in results)
            try:
                ani = FuncAnimation(self.fig, update, frames=max_frames, 
                                  interval=400, blit=False, repeat=False)  # Changed blit=True to False for annotations
                self.animations.append(ani)
            except Exception as e:
                self.status_var.set(f"Animation error: {str(e)}")
                return
        
        self.canvas.draw()

    def clear_animations(self):
        """Clear existing animations safely to prevent memory leaks"""
        for ani in self.animations[:]:  # Iterate over a copy to allow modification
            if ani is not None and hasattr(ani, 'event_source'):
                try:
                    ani.event_source.stop()
                except AttributeError:
                    pass  # Ignore if event_source is missing
        self.animations.clear()

    def show_algorithm_info(self):
        """Show detailed information about algorithms in a new window"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Algorithm Information")
        info_window.geometry("600x450")
        info_window.resizable(True, True)
        
        text_frame = ttk.Frame(info_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10, 
                      font=('Segoe UI', 9), bg='white')
        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)
        
        info_text = """
Disk Scheduling Algorithms:

1. FCFS (First-Come-First-Served):
   - Services requests in the order they arrive
   - Simple implementation but often poor performance
   - No starvation of requests
   - Average performance case: O(n)

2. SSTF (Shortest Seek Time First):
   - Services the nearest request first
   - Better performance than FCFS
   - May cause starvation of distant requests
   - Average performance case: O(n^2)

3. SCAN (Elevator Algorithm):
   - Moves back and forth across the disk
   - Services all requests along the way
   - Reaches disk ends before reversing
   - Good for heavy loads

4. C-SCAN (Circular SCAN):
   - Moves in one direction only
   - When reaching end, jumps to start
   - More uniform wait times than SCAN
   - Better for systems with many requests

5. LOOK:
   - Similar to SCAN but doesn't go to disk ends
   - Reverses direction after last request
   - More efficient than SCAN

6. C-LOOK:
   - Circular version of LOOK
   - After servicing last request, jumps to first request
   - Combines benefits of C-SCAN and LOOK

Performance Characteristics:
- FCFS: Simple but often worst performance
- SSTF: Better but can starve requests
- SCAN/LOOK: Good for heavy loads
- C-SCAN/C-LOOK: Most uniform service times
"""
        text.insert(tk.END, info_text)
        text.config(state=tk.DISABLED)
        
        button_frame = ttk.Frame(info_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="Close", command=info_window.destroy).pack(side=tk.RIGHT)

    def reset(self):
        """Reset all inputs and outputs to default state"""
        self.clear_animations()
        
        self.entry_requests.delete(0, tk.END)
        self.entry_head.delete(0, tk.END)
        self.entry_head.insert(0, "50")
        self.entry_max_track.delete(0, tk.END)
        self.entry_max_track.insert(0, "200")
        self.entry_time_scale.delete(0, tk.END)
        self.entry_time_scale.insert(0, "1000")
        self.algorithm_var.set("FCFS")
        self.direction_var.set("left")
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_facecolor('#f8f8f8')
        self.ax.set_xlabel("Track Number", fontsize=10)
        self.ax.set_ylabel("Step", fontsize=10)
        self.ax.set_title("Disk Head Movement", fontsize=12)
        self.canvas.draw()
        
        self.status_var.set("Reset complete. Ready for new simulation.")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = DiskSchedulingApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
        root.destroy()
