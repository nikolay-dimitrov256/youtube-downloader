import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create a canvas object and scrollbars for scrolling it in both directions.
        self.canvas = tk.Canvas(self)
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the scrollable frame inside the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # mousewheel scrolling
        self.scrollable_frame.bind(
            '<MouseWheel>',
            lambda event: self.canvas.yview_scroll(int(event.delta // 60), 'units'),
        )

        # Add the scrollable frame to the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure the canvas scroll for both directions
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Pack the canvas and scrollbars

        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.bind_mouse_wheel()

    def bind_mouse_wheel(self):
        # Bind mouse wheel to the canvas for vertical scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shift_mouse_wheel)

    def on_mouse_wheel(self, event):
        # Use the sign of event.delta to determine scroll direction
        self.canvas.yview_scroll(-1 * (event.delta // 80), "units")

    def on_shift_mouse_wheel(self, event):
        # Horizontal scrolling with Shift key + Mouse Wheel
        self.canvas.xview_scroll((event.delta // 80), "units")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")

    # Create the scrollable frame
    scrollable_frame = ScrollableFrame(root)
    scrollable_frame.pack(fill="both", expand=True)

    # Add wider content to trigger horizontal scroll
    for i in range(50):
        frame = tk.Frame(scrollable_frame.scrollable_frame, bd=2, relief="groove")
        # Add a label with long text to make the content wide
        label = tk.Label(frame, text="Lorem ipsum dolor sit amet, consectetur adipisicing elit. Beatae quod aliquam officiis fuga, aut illo. Aspernatur nostrum animi, rerum omnis quisquam magni ad similique est quod labore architecto, officiis qui?")
        label.pack(padx=10)
        frame.pack(padx=10, fill="x")

    root.mainloop()
