import tkinter as tk
from tkinter import ttk

def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry("+0+0")
    label = ttk.Label(tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1)
    label.pack()
    tooltip.withdraw()
    
    def show(event):
        x = event.x_root + 20
        y = event.y_root + 10
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()
    
    def hide(event):
        tooltip.withdraw()
    
    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)