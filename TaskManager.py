import tkinter as tk
from tkinter import simpledialog, messagebox
import json


class EisenhowerMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Eisenhower Matrix")

        # Canvas setup
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create the matrix
        self.draw_matrix()

        # Task-related variables
        self.tasks = {}  # Dictionary to store tasks (rectangles and labels)
        self.dragging_task = None

        # Context menu for deleting tasks
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Delete Task", command=self.delete_task)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.add_task)
        self.canvas.bind("<B1-Motion>", self.move_task)
        self.canvas.bind("<ButtonRelease-1>", self.release_task)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # Load tasks from file
        self.load_tasks()

        # Save tasks on close
        self.root.protocol("WM_DELETE_WINDOW", self.save_tasks_and_exit)

    def draw_matrix(self):
        """Draws the matrix grid and axis labels."""
        # Canvas dimensions
        canvas_width = 800
        canvas_height = 600

        # Midpoints for dividing lines
        mid_x = canvas_width / 2
        mid_y = canvas_height / 2

        # Draw vertical and horizontal lines
        self.canvas.create_line(mid_x, 0, mid_x, canvas_height, width=2)
        self.canvas.create_line(0, mid_y, canvas_width, mid_y, width=2)

        # Add axis labels
        self.canvas.create_text(mid_x / 2, 20, text="Urgent", font=("Arial", 12))
        self.canvas.create_text(3 * mid_x / 2, 20, text="Not Urgent", font=("Arial", 12))
        self.canvas.create_text(20, mid_y / 2, text="Important", font=("Arial", 12), angle=90)
        self.canvas.create_text(20, 3 * mid_y / 2, text="Not Important", font=("Arial", 12), angle=90)

    def add_task(self, event):
        """Adds a new task to the clicked position."""
        task_label = simpledialog.askstring("New Task", "Enter task description:")
        if task_label:
            x, y = event.x, event.y
            
            # Calculate width of the rectangle based on the text length
            text_width = len(task_label) * 7  # Approximate width per character (adjust as needed)
            rect_width = max(100, text_width + 20)  # Ensure a minimum width

            # Create the task rectangle and text
            task_rect = self.canvas.create_rectangle(x - rect_width / 2, y - 20, x + rect_width / 2, y + 20, fill="lightblue", outline="black")
            task_text = self.canvas.create_text(x, y, text=task_label, font=("Arial", 10))

            # Create a delete button near the task
            button = tk.Button(self.canvas, text="Delete", command=lambda: self.delete_task(task_rect, task_text))
            self.canvas.create_window(x + rect_width / 2 + 40, y - 20, window=button)  # Position the button

            # Store task and button references in dictionary
            self.tasks[task_rect] = {"text": task_text, "x": x, "y": y, "description": task_label, "button": button, "rect_width": rect_width}

    def delete_task(self, task_rect, task_text):
        """Deletes a task and its associated delete button."""
        # Remove from canvas
        self.canvas.delete(task_rect)
        self.canvas.delete(task_text)

        # Remove button
        task_button = self.tasks[task_rect]["button"]
        task_button.destroy()

        # Remove from tasks dictionary
        del self.tasks[task_rect]

    def move_task(self, event):
        """Moves a task while dragging."""
        if self.dragging_task:
            x, y = event.x, event.y
            task_rect = self.dragging_task
            self.canvas.coords(task_rect, x - self.tasks[task_rect]["rect_width"] / 2, y - 20, x + self.tasks[task_rect]["rect_width"] / 2, y + 20)
            task_text = self.tasks[task_rect]["text"]
            self.canvas.coords(task_text, x, y)
            self.tasks[task_rect]["x"] = x
            self.tasks[task_rect]["y"] = y

    def release_task(self, event):
        """Releases the dragged task."""
        self.dragging_task = None

    def get_task_at_position(self, x, y):
        """Finds the task at the given position."""
        closest = self.canvas.find_closest(x, y)
        if closest and closest[0] in self.tasks:
            return closest[0]
        return None

    def show_context_menu(self, event):
        """Shows a context menu to delete a task."""
        task = self.get_task_at_position(event.x, event.y)
        if task:
            self.dragging_task = task
            self.context_menu.post(event.x_root, event.y_root)

    def save_tasks_and_exit(self):
        """Saves all tasks to a file and exits the application."""
        tasks_data = []
        for task_rect, task_info in self.tasks.items():
            tasks_data.append({
                "x": task_info["x"],
                "y": task_info["y"],
                "description": task_info["description"]
            })
        with open("tasks.json", "w") as file:
            json.dump(tasks_data, file)

        self.root.destroy()

    def load_tasks(self):
        """Loads tasks from a file."""
        try:
            with open("tasks.json", "r") as file:
                tasks_data = json.load(file)
                for task in tasks_data:
                    x, y = task["x"], task["y"]
                    description = task["description"]

                    # Calculate width of the rectangle based on the text length
                    text_width = len(description) * 7  # Approximate width per character (adjust as needed)
                    rect_width = max(100, text_width + 20)  # Ensure a minimum width

                    task_rect = self.canvas.create_rectangle(x - rect_width / 2, y - 20, x + rect_width / 2, y + 20, fill="lightblue", outline="black")
                    task_text = self.canvas.create_text(x, y, text=description, font=("Arial", 10))

                    # Create a delete button near the task
                    button = tk.Button(self.canvas, text="Delete", command=lambda: self.delete_task(task_rect, task_text))
                    self.canvas.create_window(x + rect_width / 2 + 40, y - 20, window=button)  # Position the button

                    # Store task and button references in dictionary
                    self.tasks[task_rect] = {"text": task_text, "x": x, "y": y, "description": description, "button": button, "rect_width": rect_width}
        except FileNotFoundError:
            # No tasks file exists; start with an empty list
            pass


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = EisenhowerMatrixApp(root)
    root.mainloop()
