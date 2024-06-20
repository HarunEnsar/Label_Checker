# -*- encoding: utf-8 -*-

if __name__ != '__main__':
    exit(1)

import os
import shutil
import threading
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from datetime import datetime

"""
usage='Boşluk tuşu ile bir sonraki resme geçebilirsiniz. Onaylamak için "a" tuşuna, reddetmek için "r" tuşuna, geri almak için "u" tuşuna ve çıkmak için ise "q" veya da "esc" tuşuna basınız.'
"""

messagebox.showwarning(
    'UYARI!!', 'Boşluk tuşu ile bir sonraki resme geçebilirsiniz. Onaylamak için "a" tuşuna, reddetmek için "r" tuşuna, geri almak için "u" tuşuna ve çıkmak için ise "q" veya da "esc" tuşuna basınız'
)

messagebox.showinfo("Resim", "Resim yolunu seçiniz.")
image_folder_path = filedialog.askdirectory()
messagebox.showinfo("Etiket", "Etiket yolunu seçiniz.")
label_folder_path = filedialog.askdirectory()


image_files = [
    f for f in os.listdir(image_folder_path)
    if os.path.isfile(
        os.path.join(image_folder_path, f)
    )
]
label_files = [
    f for f in os.listdir(label_folder_path)
    if os.path.isfile(
        os.path.join(label_folder_path, f)
    )
]

image_files.sort()
label_files.sort()

formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_")

approved_folder = formatted_date + 'approved'
rejected_folder = formatted_date + 'rejected'

os.makedirs(str.format('{}/images', approved_folder), exist_ok=True)
os.makedirs(str.format('{}/labels', approved_folder), exist_ok=True)

os.makedirs(str.format('{}/images', rejected_folder), exist_ok=True)
os.makedirs(str.format('{}/labels', rejected_folder), exist_ok=True)

root = tkinter.Toplevel()
root.title('Label Checker')
root.geometry('1440x930+0+0')
root.resizable(False, False)

label_color_mapping = {
    '0': 'orange',
    '1': 'green',
    '2': 'red',
    '3': 'blue'
}

display_data: dict = {}

canvas_current_image = None

text_label = tkinter.Label(root, text="", font=('Helvetica', 14))
text_label.pack()


class Action:
    def __init__(self, name, do_function, undo_function, do_args=[], do_kwargs={}, undo_args=[], undo_kwargs={}):
        self.name = name
        self._do_function = do_function
        self._undo_function = undo_function
        self.do_args = do_args
        self.do_kwargs = do_kwargs
        self.undo_args = undo_args
        self.undo_kwargs = undo_kwargs

    def do(self, *args, **kwargs):
        new_args = self.do_args
        if args is not None and len(args) > 0:
            new_args += args

        new_kwargs = self.do_kwargs
        if kwargs is not None and len(kwargs) > 0:
            new_kwargs.update(kwargs)

        self._do_function(*new_args, **new_kwargs)

    def undo(self, *args, **kwargs):
        new_args = self.undo_args
        if args is not None and len(args) > 0:
            new_args += args

        new_kwargs = self.undo_kwargs
        if kwargs is not None and len(kwargs) > 0:
            new_kwargs.update(kwargs)

        self._undo_function(*new_args, **new_kwargs)


undoable_actions = []


def update_display(event):
    image_path: str = display_data['image_path']
    label_path: str = display_data['label_path']
    coordinates: list = display_data['coordinates']
    image_name = os.path.basename(image_path)
    label_name = os.path.basename(label_path)
    print(os.path.basename(image_path))
    with open(label_path, 'r') as file:
        label_file_contents = file.read()
    if os.stat(label_path).st_size == 0:
        print(f"Etiket dosyası boş: {label_path}")
    else:
        print(f"{image_name}:{label_name}\n Etiket: \n{label_file_contents}")
        root.title(f'Label Checker----{image_name} ----- {label_name} ----')

    if os.sep == '\\':
        image_path = image_path.replace('/', os.sep)
        label_path = label_path.replace('/', os.sep)
    else:
        image_path = image_path.replace('\\', os.sep)
        label_path = label_path.replace('\\', os.sep)

    global canvas_current_image
    try:
        canvas_current_image = ImageTk.PhotoImage(
            Image.open(image_path).resize((1440, 900)))
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    canvas.delete('all')

    canvas.create_image((0, 0), image=canvas_current_image, anchor='nw')

    vehicle_count = 0
    person_count = 0
    uap_count = 0
    uai_count = 0

    if len(coordinates) != 0:
        with open(label_path, 'r') as file:
            lines = file.readlines()

        for coordinate, line in zip(coordinates, lines):
            if len(coordinate) == 0:
                continue
            elements = line.split()
            if elements:
                first_element = elements[0]

                x1 = coordinate[0] * canvas_current_image.width() - coordinate[2] * \
                    canvas_current_image.width() / 2
                y1 = coordinate[1] * canvas_current_image.height() - coordinate[3] * \
                    canvas_current_image.height() / 2
                x2 = x1 + coordinate[2] * canvas_current_image.width()
                y2 = y1 + coordinate[3] * canvas_current_image.height()

                label_color = label_color_mapping.get(first_element, 'black')

                if first_element == '0':
                    label_color = 'orange'
                    vehicle_count += 1
                elif first_element == '1':
                    label_color = 'blue'
                    person_count += 1
                elif first_element == '2':
                    uap_count += 1
                elif first_element == '3':
                    uai_count += 1

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline=label_color,
                    width=2
                )
    print(
        f"Taşıt sayısı: {vehicle_count}, İnsan sayısı: {person_count}, UAP sayısı: {uap_count}, UAI sayısı: {uai_count}"
    )
    text_label.config(
        text=f"Taşıt sayısı: {vehicle_count}, İnsan sayısı: {person_count}, UAP sayısı: {uap_count}, UAI sayısı: {uai_count}"
    )


last_pressed_key = tkinter.StringVar(value='')
key_event: threading.Event = threading.Event()


def key_press(e):
    last_pressed_key.set(chr(e.keycode).lower())
    global key_event
    key_event.set()


root.bind('<Key>', key_press)
root.bind('<Escape>', lambda e: root.quit())
root.bind('<<update_display>>', update_display)

canvas = tkinter.Canvas(root, bg='white', width=1440, height=900)
canvas.pack()


def move_files(image_old_path, image_new_path, label_old_path, label_new_path):
    print(
        f"Resim ve etiket dosyaları taşınıyor: {image_old_path}, {label_old_path} --> {image_new_path}, {label_new_path}"
    )

    shutil.move(
        image_old_path,
        image_new_path
    )
    shutil.move(
        label_old_path,
        label_new_path
    )


def label_thread_main(tkObj: tkinter.Tk, key_event: threading.Event, key_var: tkinter.StringVar):
    file_number = 0

    zipped_list = list(zip(image_files, label_files))

    list_index = 0

    while list_index < len(zipped_list):
        image_file, label_file = zipped_list[list_index]

        print(f"{file_number}/{len(zipped_list)}")

        image_path = os.path.join(image_folder_path, image_file)
        label_path = os.path.join(label_folder_path, label_file)

        with open(label_path, 'r') as file:
            label_file_contents = file.read()

        coordinates = []

        for x in label_file_contents.split('\n'):
            coordinates_for_the_image = [
                float(x) for x in x.split(' ') if x != ''][1:]

            if len(coordinates_for_the_image) == 0:
                continue

            coordinates.append(coordinates_for_the_image)

        global display_data
        display_data = {
            'image_path': image_path,
            'label_path': label_path,
            'coordinates': coordinates
        }

        tkObj.event_generate('<<update_display>>')

        while True:
            key_event.wait()
            key_event.clear()

            if key_var.get() == 'q':
                print('Exiting...')
                tkObj.quit()
                return
            elif key_var.get() == 'a':
                action = Action(
                    'Etiket-Onay',
                    move_files,
                    move_files,
                    do_args=[
                        image_path,
                        os.path.join(
                            approved_folder,
                            'images',
                            image_file
                        ),
                        label_path,
                        os.path.join(
                            approved_folder,
                            'labels',
                            label_file
                        )
                    ],
                    undo_args=[
                        os.path.join(
                            approved_folder,
                            'images',
                            image_file
                        ),
                        image_path,
                        os.path.join(
                            approved_folder,
                            'labels',
                            label_file
                        ),
                        label_path
                    ]
                )

                action.do()

                undoable_actions.append(action)

                print(f"{image_file} onaylandı")
                print(
                    f"Resim ve etiket dosyaları taşındı: {image_file}, {label_file} --> {approved_folder}"
                )

                file_number += 1

                break
            elif key_var.get() == 'r':
                action = Action(
                    'Etiket-Red',
                    move_files,
                    move_files,
                    do_args=[
                        image_path,
                        os.path.join(
                            rejected_folder,
                            'images',
                            image_file
                        ),
                        label_path,
                        os.path.join(
                            rejected_folder,
                            'labels',
                            label_file
                        )
                    ],
                    undo_args=[
                        os.path.join(
                            rejected_folder,
                            'images',
                            image_file
                        ),
                        image_path,
                        os.path.join(
                            rejected_folder,
                            'labels',
                            label_file
                        ),
                        label_path
                    ]
                )

                action.do()

                undoable_actions.append(action)

                print(f"{image_file} reddedildi")
                print(
                    f"Resim ve etiket dosyaları taşındı: {image_file}, {label_file} --> {rejected_folder}"
                )

                file_number += 1

                break
            elif key_var.get() == 'u':
                if len(undoable_actions) == 0 or list_index == 0:
                    continue

                action = undoable_actions.pop()
                action.undo()
                list_index -= 2
                file_number -= 1

                break
            elif key_var.get() == ' ':
                file_number += 1
                break
            else:
                continue

        list_index += 1


label_thread = threading.Thread(
    target=label_thread_main, args=[root, key_event, last_pressed_key], daemon=True)
label_thread.start()

root.mainloop()
