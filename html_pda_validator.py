# ---------- Modern HTML Tag Validator----------#   
import tkinter as tk
from tkinter import scrolledtext, ttk
from collections import defaultdict
from html.parser import HTMLParser

def simulate_pda(html_input):
    class TagParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []
            self.valid = True
            self.tag_stats = defaultdict(lambda: {"open": 0, "close": 0})
            self.mismatch_reasons = dict()
            self.output_tokens = []

        def handle_starttag(self, tag, attrs):
            self.stack.append(tag)
            self.tag_stats[tag]["open"] += 1
            full_tag = self.get_starttag_text()
            self.output_tokens.append((full_tag, "valid" if self.valid else "invalid"))

        def handle_endtag(self, tag):
            self.tag_stats[tag]["close"] += 1

            if not self.stack:
                self.valid = False
                if tag not in self.mismatch_reasons:
                    self.mismatch_reasons[tag] = "Extra closing tag"
                self.output_tokens.append((f"</{tag}>", "invalid"))
            else:
                top = self.stack.pop()
                if top == tag:
                    self.output_tokens.append((f"</{tag}>", "valid"))
                else:
                    self.valid = False
                    if tag not in self.mismatch_reasons:
                        self.mismatch_reasons[tag] = f"Tag mismatch: expected </{top}>, but found </{tag}>"
                    if top not in self.mismatch_reasons:
                        self.mismatch_reasons[top] = f"You closed </{tag}> too early, please close </{top}> first"
                    self.output_tokens.append((f"</{tag}>", "invalid"))

        def handle_data(self, data):
            stripped = data.strip()
            if stripped:
                self.output_tokens.append((stripped, "text"))

        def error(self, message):
            pass

    parser = TagParser()
    parser.feed(html_input)

    for tag in parser.stack:
        if tag not in parser.mismatch_reasons:
            parser.mismatch_reasons[tag] = "Missing closing tag"

    if parser.stack:
        parser.valid = False

    return parser.valid, parser.output_tokens, parser.tag_stats, parser.mismatch_reasons

def highlight_tags(text_widget, input_text, tag_stats):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)

    text_widget.tag_configure("valid", foreground='#10B981', font=('SF Pro Display', 11, 'bold'))
    text_widget.tag_configure("invalid", foreground='#EF4444', font=('SF Pro Display', 11, 'bold'))
    text_widget.tag_configure("text", foreground='#374151', font=('SF Pro Display', 11))

    valid, tokenized_output, collected_stats, mismatch_reasons = simulate_pda(input_text)
    tag_stats.clear()
    tag_stats.update(collected_stats)

    pointer = 0
    for token, tag_type in tokenized_output:
        idx = input_text.find(token, pointer)
        if idx == -1:
            continue
        if idx > pointer:
            text_widget.insert(tk.END, input_text[pointer:idx])
        text_widget.insert(tk.END, token, tag_type)
        pointer = idx + len(token)

    if pointer < len(input_text):
        text_widget.insert(tk.END, input_text[pointer:])

    text_widget.config(state=tk.DISABLED)
    return valid, mismatch_reasons

def update_stats_table(tag_stats, mismatch_reasons):
    for row in stats_tree.get_children():
        stats_tree.delete(row)

    for tag, counts in tag_stats.items():
        open_count = counts["open"]
        close_count = counts["close"]
        matched = "✓ Matched" if tag not in mismatch_reasons and open_count == close_count else "✗ Not Matched"
        reason = mismatch_reasons.get(tag, "–")

        row_id = stats_tree.insert("", "end", values=(tag, open_count, close_count, matched, reason))
        if "✗" in matched:
            stats_tree.item(row_id, tags=("unmatched",))
        else:
            stats_tree.item(row_id, tags=("matched",))

def clear_all():
    input_textbox.delete('1.0', tk.END)
    output_textbox.config(state=tk.NORMAL)
    output_textbox.delete('1.0', tk.END)
    output_textbox.config(state=tk.DISABLED)
    status_label.config(text="Ready to validate", fg="#6B7280")
    for row in stats_tree.get_children():
        stats_tree.delete(row)

def process_text():
    input_text = input_textbox.get("1.0", tk.END).strip()
    if not input_text:
        output_textbox.config(state=tk.NORMAL)
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, "⚠️ Please enter some HTML code to validate.")
        output_textbox.config(state=tk.DISABLED)
        status_label.config(text="No input provided", fg="#EF4444")
        for row in stats_tree.get_children():
            stats_tree.delete(row)
        return

    tag_stats = defaultdict(lambda: {"open": 0, "close": 0})
    valid, mismatch_reasons = highlight_tags(output_textbox, input_text, tag_stats)

    if valid:
        status_label.config(text="✅ Valid HTML Structure", fg="#10B981")
    else:
        status_label.config(text="❌ Invalid HTML Structure", fg="#EF4444")
    
    update_stats_table(tag_stats, mismatch_reasons)

def create_rounded_button(parent, text, command, bg_color, fg_color, active_bg, active_fg):
    """Create a button with rounded edges using Canvas"""
    button_frame = tk.Frame(parent, bg="#FFFFFF")
    
    canvas = tk.Canvas(button_frame, width=140, height=40, highlightthickness=0, bg="#FFFFFF")
    canvas.pack()
    
    # Draw rounded rectangle
    def draw_rounded_rect(x1, y1, x2, y2, radius=8, fill_color=bg_color):
        canvas.delete("button_bg")
        # Main rectangle
        canvas.create_rectangle(x1+radius, y1, x2-radius, y2, fill=fill_color, outline="", tags="button_bg")
        canvas.create_rectangle(x1, y1+radius, x2, y2-radius, fill=fill_color, outline="", tags="button_bg")
        # Corners
        canvas.create_oval(x1, y1, x1+2*radius, y1+2*radius, fill=fill_color, outline="", tags="button_bg")
        canvas.create_oval(x2-2*radius, y1, x2, y1+2*radius, fill=fill_color, outline="", tags="button_bg")
        canvas.create_oval(x1, y2-2*radius, x1+2*radius, y2, fill=fill_color, outline="", tags="button_bg")
        canvas.create_oval(x2-2*radius, y2-2*radius, x2, y2, fill=fill_color, outline="", tags="button_bg")
    
    # Initial button background
    draw_rounded_rect(2, 2, 138, 38, fill_color=bg_color)
    
    # Add text on top
    text_id = canvas.create_text(70, 20, text=text, fill=fg_color, font=("Arial", 12, "bold"))
    
    # Hover effects
    def on_enter(e):
        draw_rounded_rect(2, 2, 138, 38, fill_color=active_bg)
        canvas.itemconfig(text_id, fill=active_fg)
        canvas.configure(cursor="hand2")
    
    def on_leave(e):
        draw_rounded_rect(2, 2, 138, 38, fill_color=bg_color)
        canvas.itemconfig(text_id, fill=fg_color)
        canvas.configure(cursor="")
    
    def on_click(e):
        command()
    
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)
    
    return button_frame

def setup_modern_theme():
    """Configure modern theme styles"""
    style = ttk.Style()
    style.theme_use("default")
    
    # Configure Treeview
    style.configure("Modern.Treeview",
                   background="#FFFFFF",
                   foreground="#374151",
                   fieldbackground="#FFFFFF",
                   borderwidth=0,
                   font=('SF Pro Display', 10))
    
    style.configure("Modern.Treeview.Heading",
                   background="#F8FAFC",
                   foreground="#1F2937",
                   font=('SF Pro Display', 10, 'bold'),
                   borderwidth=1,
                   relief="solid")
    
    # Configure tags
    style.configure("matched", background="#F0FDF4")
    style.configure("unmatched", background="#FEF2F2")
    
    # Map colors for selection
    style.map("Modern.Treeview",
              background=[('selected', '#3B82F6')],
              foreground=[('selected', 'white')])

def create_gradient_frame(parent, color1, color2, height=100):
    """Create a gradient effect frame"""
    frame = tk.Frame(parent, height=height)
    frame.pack_propagate(False)
    return frame

# ---------- Main Application ----------
root = tk.Tk()
root.title("HTML Tag Structure Validator")
root.geometry("1200x800")
root.configure(bg="#F8FAFC")

# Set up modern theme
setup_modern_theme()

# ---------- Header Section ----------
header_frame = tk.Frame(root, bg="#1F2937", height=80)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

header_content = tk.Frame(header_frame, bg="#1F2937")
header_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)

title_label = tk.Label(header_content, 
                      text="HTML Tag Validator", 
                      font=("SF Pro Display", 24, "bold"), 
                      bg="#1F2937", 
                      fg="#FFFFFF")
title_label.pack(side=tk.LEFT, anchor=tk.W)

subtitle_label = tk.Label(header_content, 
                         text="Powered by PDA Simulation", 
                         font=("SF Pro Display", 12), 
                         bg="#1F2937", 
                         fg="#9CA3AF")
subtitle_label.pack(side=tk.LEFT, anchor=tk.W, padx=(20, 0))

# ---------- Main Content Container ----------
main_container = tk.Frame(root, bg="#F8FAFC")
main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

# ---------- Left Panel (Input) ----------
left_panel = tk.Frame(main_container, bg="#FFFFFF", relief=tk.RAISED, bd=1)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
left_panel.config(width=400)  # Fixed width for input panel
left_panel.pack_propagate(False)

input_header = tk.Frame(left_panel, bg="#FFFFFF", height=60)
input_header.pack(fill=tk.X)
input_header.pack_propagate(False)

input_label = tk.Label(input_header, 
                      text="📝 HTML Code Input", 
                      font=("SF Pro Display", 14, "bold"), 
                      bg="#FFFFFF", 
                      fg="#1F2937")
input_label.pack(side=tk.LEFT, padx=20, pady=20)

# Clear button in header
clear_button = tk.Button(input_header, 
                        text="🗑️ Clear", 
                        command=clear_all, 
                        bg="#6B7280", 
                        fg="white", 
                        font=("SF Pro Display", 11, "bold"),
                        relief=tk.FLAT,
                        padx=20,
                        pady=8,
                        cursor="hand2")
clear_button.pack(side=tk.RIGHT, padx=20, pady=20)

# Input text area
input_container = tk.Frame(left_panel, bg="#FFFFFF")
input_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

input_textbox = scrolledtext.ScrolledText(input_container, 
                                         wrap=tk.WORD, 
                                         font=("SF Mono", 11), 
                                         bg="#F9FAFB", 
                                         fg="#374151",
                                         insertbackground="#3B82F6",
                                         relief=tk.FLAT,
                                         bd=1,
                                         highlightthickness=1,
                                         highlightcolor="#3B82F6",
                                         highlightbackground="#E5E7EB")
input_textbox.pack(fill=tk.BOTH, expand=True)

# Validate button at bottom
button_container = tk.Frame(left_panel, bg="#FFFFFF")
button_container.pack(fill=tk.X, padx=20, pady=(10, 20))

# Validate button at bottom
button_container = tk.Frame(left_panel, bg="#FFFFFF")
button_container.pack(fill=tk.X, padx=20, pady=(10, 20))

# Standard button with better styling
process_button = tk.Button(button_container, 
                          text="Validate HTML", 
                          command=process_text, 
                          bg="#3B82F6", 
                          fg="white", 
                          font=("SF Pro Display", 12, "bold"),
                          relief=tk.FLAT,
                          padx=30,
                          pady=12,
                          cursor="hand2",
                          activebackground="#2563EB",
                          activeforeground="white",
                          bd=0)
process_button.pack(anchor=tk.CENTER)

# Add hover effect
def on_enter(e):
    process_button.config(bg="#2563EB")
    
def on_leave(e):
    process_button.config(bg="#3B82F6")
    
process_button.bind("<Enter>", on_enter)
process_button.bind("<Leave>", on_leave)

# ---------- Right Panel (Output & Analysis) ----------
right_panel = tk.Frame(main_container, bg="#FFFFFF", relief=tk.RAISED, bd=1)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
right_panel.config(width=750)  # More space for results and analysis

# Output section
output_header = tk.Frame(right_panel, bg="#FFFFFF", height=60)
output_header.pack(fill=tk.X)
output_header.pack_propagate(False)

output_label = tk.Label(output_header, 
                       text="📋 Validation Results", 
                       font=("SF Pro Display", 14, "bold"), 
                       bg="#FFFFFF", 
                       fg="#1F2937")
output_label.pack(side=tk.LEFT, padx=20, pady=20)

status_label = tk.Label(output_header, 
                       text="Ready to validate", 
                       font=("SF Pro Display", 12, "bold"), 
                       bg="#FFFFFF", 
                       fg="#6B7280")
status_label.pack(side=tk.RIGHT, padx=20, pady=20)

# Output text area
output_container = tk.Frame(right_panel, bg="#FFFFFF")
output_container.pack(fill=tk.X, padx=20, pady=(0, 10))

output_textbox = scrolledtext.ScrolledText(output_container, 
                                          wrap=tk.WORD, 
                                          height=12, 
                                          font=("SF Mono", 11), 
                                          bg="#F9FAFB", 
                                          fg="#374151",
                                          relief=tk.FLAT,
                                          bd=1,
                                          highlightthickness=1,
                                          highlightcolor="#3B82F6",
                                          highlightbackground="#E5E7EB")
output_textbox.pack(fill=tk.X)
output_textbox.config(state=tk.DISABLED)

# Stats section
stats_header = tk.Frame(right_panel, bg="#FFFFFF", height=50)
stats_header.pack(fill=tk.X)
stats_header.pack_propagate(False)

stats_label = tk.Label(stats_header, 
                      text="📊 Tag Analysis", 
                      font=("SF Pro Display", 14, "bold"), 
                      bg="#FFFFFF", 
                      fg="#1F2937")
stats_label.pack(side=tk.LEFT, padx=20, pady=15)

# Stats table
stats_container = tk.Frame(right_panel, bg="#FFFFFF")
stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

stats_tree = ttk.Treeview(stats_container,
                         columns=("Tag", "Open", "Close", "Matched", "Reason"),
                         show="headings",
                         style="Modern.Treeview")
stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure scrollbar
scrollbar = ttk.Scrollbar(stats_container, orient="vertical", command=stats_tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
stats_tree.configure(yscrollcommand=scrollbar.set)

# Configure columns
stats_tree.heading("Tag", text="Tag Name")
stats_tree.heading("Open", text="Open")
stats_tree.heading("Close", text="Close")
stats_tree.heading("Matched", text="Status")
stats_tree.heading("Reason", text="Reason")

stats_tree.column("Tag", width=80, anchor=tk.W)
stats_tree.column("Open", width=50, anchor=tk.CENTER)
stats_tree.column("Close", width=50, anchor=tk.CENTER)
stats_tree.column("Matched", width=100, anchor=tk.CENTER)
stats_tree.column("Reason", width=300, anchor=tk.W)

# Configure row tags
stats_tree.tag_configure("matched", background="#F0FDF4")
stats_tree.tag_configure("unmatched", background="#FEF2F2")


# Start the application
root.mainloop()