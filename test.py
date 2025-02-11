import tkinter as tk
from PIL import Image

root = tk.Tk()
root.title("Displaing Gif")

file = "Bjorn-unscreen.gif"
info = Image.open(file)

frames = info.n_frames  # number of frames

photoimage_objects = []
for i in range(frames):
    obj = tk.PhotoImage(file=file, format=f"gif -index {i}")
    photoimage_objects.append(obj)


def animation(current_frame=0):
    global loop
    image = photoimage_objects[current_frame]

    gif_label.configure(image=image)
    current_frame = current_frame + 1

    if current_frame == frames:
        current_frame = 0

    loop = root.after(50, lambda: animation(current_frame))


def stop_animation():
    root.after_cancel(loop)


gif_label = tk.Label(root, image="")
gif_label.pack()

start = tk.Button(root, text="Start", command=lambda: animation(current_frame=0))
start.pack()

stop = tk.Button(root, text="Stop", command=stop_animation)
stop.pack()

root.mainloop()
