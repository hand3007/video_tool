from tkinter import *
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from toolkit import *
import moviepy.config as cfg

cfg.change_settings({'IMAGEMAGICK_BINARY': 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'})


class MiniTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Tool")

        # Create a top menu bar
        self.top_menu = tk.Menu(root)
        root.config(menu=self.top_menu)

        # Create instances of the three pages
        self.page1 = PageOne(self, self.root)
        self.page2 = PageTwo(self, self.root)
        self.page3 = PageThree(self, self.root)

        # Add menu items for each page in the top menu bar
        self.top_menu.add_command(label="Tải về", command=self.page1.show)
        self.top_menu.add_command(label="Sửa video", command=self.page2.show)
        self.top_menu.add_command(label="Re-up", command=self.page3.show)

        # Show the first page by default
        self.show_page(self.page2)

    def show_page(self, page):
        # Hide the current page and show the new page
        if hasattr(self, "current_page"):
            self.current_page.frame.pack_forget()
        page.frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        self.current_page = page


class PageOne:
    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.frame = tk.Frame(root)

        def download():
            link = download_entry.get()
            Movie.download_video(link)

        label = tk.Label(self.frame, text="Tải video", font=('Arial', 18))
        label.grid(row=1, column=10, columnspan=20, padx=10, pady=10, sticky=tk.E)

        download_label = tk.Label(self.frame, text="Đường dẫn Youtube video:")
        download_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        download_entry = Entry(self.frame, width=50)
        download_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        submit_entry = tk.Button(self.frame, text="Tải về", command=download)
        submit_entry.grid(row=4, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)

        download_success_label = tk.Label(self.frame, text="")
        download_success_label.grid(row=5, column=1, columnspan=5, padx=5, pady=5, sticky=tk.W)

    def show(self):
        self.app.show_page(self)


def resize_it(event, frame, frame_a, frame_b):
    frame_a.configure(width=event.width / 2, height=event.height / 2)
    frame_b.configure(width=event.width / 2, height=event.height / 2)
    frame.configure(width=event.width, height=event.height)


def remove_item():
    selected_items = tree.selection()
    for item in selected_items:
        tree.delete(item)


class PageTwo:
    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.frame = tk.Frame(root)
        self.links = []
        self.checkbox_vars = None
        self.radio_var = None
        self.entry_default = None
        self.entry_video_default = None
        self.entry_overlay_default = None
        global left_frame
        global right_frame

        label = tk.Label(self.frame, text="Trang sửa video", font=('Arial', 18))
        label.pack()

        # Split into left and right halves
        left_frame = tk.Frame(self.frame)
        left_frame.pack(side="left")
        # left_frame.grid(row=1, column=1)

        right_frame = tk.Frame(self.frame)
        right_frame.pack(side="right", fill="both", expand=True)
        # right_frame.grid(row=1, column=2)

        # Left half: Label, Radio Check, Entry, and Checkboxes
        self.create_left_widgets(left_frame)

        # Right half: Table with scrollbars
        self.create_table(right_frame)

    def on_entry_click(self, event):
        if self.entry_default.get() == "Nhập đường dẫn âm thanh tại đây":
            self.entry_default.delete(0, "end")
            self.entry_default.config(fg='black')

    def on_entry_video_click(self, event):
        if self.entry_video_default.get() == "Nhập đường dẫn video tại đây":
            self.entry_video_default.delete(0, "end")
            self.entry_video_default.config(fg='black')

    def on_entry_overlay_click(self, event):
        if self.entry_overlay_default.get() == "Nhập chữ chèn cho video tại đây":
            self.entry_overlay_default.delete(0, "end")
            self.entry_overlay_default.config(fg='black')

    def open_audio_file(self):
        file_path = filedialog.askopenfilenames()
        self.entry_default.delete(0, "end")
        self.entry_default.insert(0, file_path)

    def open_video_file(self):
        file_path = filedialog.askopenfilenames()
        self.entry_video_default.delete(0, "end")
        self.entry_video_default.insert(0, file_path)

    @staticmethod
    def open_folder():
        folder_path = filedialog.askdirectory()
        table = []
        tree.delete(*tree.get_children())
        if folder_path:
            contents = os.listdir(folder_path)
            PageTwo.links = [os.path.join(folder_path, item) for item in contents if
                             os.path.isfile(os.path.join(folder_path,
                                                         item))]
            for directory in PageTwo.links:
                table.append((PageTwo.links.index(directory) + 1, directory, 0.1, "X"))
                print(directory)
            # Print the selected folder's directory
            for row in table:
                tree.insert("", "end", values=row)
            print(f"Selected Folder: {folder_path}")

    @staticmethod
    def open_file():
        file_path = filedialog.askopenfilenames()
        table = []
        tree.delete(*tree.get_children())
        for directory in file_path:
            print(directory)
            table.append((file_path.index(directory) + 1, directory, 0.1, "X"))
        for row in table:
            tree.insert("", "end", values=row)

    @staticmethod
    def get_entry_value():
        value = entry.get()
        table = []
        tree.delete(*tree.get_children())
        table.append((len(table) + 1, value, 0.1, "X"))
        for row in table:
            tree.insert("", "end", values=row)
        print(value)
        # print(tree.get_children())
        entry.delete(0, 'end')

    def show(self):
        self.app.show_page(self)

    @staticmethod
    def get_column_data(tree, column):
        # Get all items in the specified column
        items_in_column = tree.get_children()

        # Get the data in the specified column for each item
        column_data = [tree.item(item, "values")[column] for item in items_in_column]
        return column_data

    def create_left_widgets(self, left_frame):
        # Label
        global entry
        label = tk.Label(left_frame, text="Options:", font=('Arial', 12))
        label.grid(row=0, column=0, columnspan=5, pady=5, sticky=tk.W)

        # Radio Check with 2 options
        self.radio_var = tk.StringVar(value="Option 1")
        radio_label = tk.Label(left_frame, text="Tùy chọn nhập đường dẫn video:")
        radio_label.grid(row=1, column=0, columnspan=5, pady=5, sticky=tk.W)
        radio1 = tk.Radiobutton(left_frame, text="Nhập thủ công", variable=self.radio_var, value="Option 1")
        radio1.grid(row=2, column=1, columnspan=3, pady=5, sticky=tk.W)
        radio2 = tk.Radiobutton(left_frame, text="File", variable=self.radio_var, value="Option 2")
        radio2.grid(row=3, column=1, columnspan=3, pady=5, sticky=tk.W)
        radio3 = tk.Radiobutton(left_frame, text="Folder", variable=self.radio_var, value="Option 3")
        radio3.grid(row=4, column=1, columnspan=3, pady=5, sticky=tk.W)

        # Entry
        # entry_label = tk.Label(left_frame, text="Đường dẫn:")
        # entry_label.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W)
        entry = tk.Entry(left_frame)
        entry.grid(row=2, column=4, columnspan=20, ipadx=70, ipady=2, pady=5, sticky=tk.W)
        accept_link = tk.Button(left_frame, text="Đồng ý", command=self.get_entry_value)
        accept_link.grid(row=2, column=40, columnspan=10, pady=1, sticky=tk.W)
        open_file = tk.Button(left_frame, text="Chọn", command=self.open_file)
        open_file.grid(row=3, column=4, columnspan=1, pady=1, sticky=tk.W)
        open_folder = tk.Button(left_frame, text="Chọn", command=self.open_folder)
        open_folder.grid(row=4, column=4, columnspan=1, pady=1, sticky=tk.W)

        # Checkboxes with option labels
        checkbox_label = tk.Label(left_frame, text="Tùy chọn:")
        checkbox_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
        options = ["Tách video",
                   "Cắt video",
                   "Thêm intro",
                   "Tắt âm thanh",
                   "Đổi âm thanh",
                   "Ghép 2 video",
                   "Chèn chữ",
                   "Chèn khung"]
        self.checkbox_vars = [tk.BooleanVar() for _ in range(len(options))]
        checkboxes = [tk.Checkbutton(left_frame, text=option, variable=self.checkbox_vars[i]) for i, option in
                      enumerate(options)]
        for i, checkbox in enumerate(checkboxes):
            checkbox.grid(row=6 + i, column=0, columnspan=2, pady=2, sticky=tk.W)

        cut_from_to_label = tk.Label(left_frame, text="From")
        cut_from_to_label.grid(row=7, column=4, pady=2, sticky=tk.E)
        cut_from_to_button = tk.Spinbox(left_frame, from_=0, to=100, width=5)
        cut_from_to_button.grid(row=7, column=5, sticky=tk.W)
        cut_to_button = tk.Label(left_frame, text="To")
        cut_to_button.grid(row=7, column=6, sticky=tk.E)
        cut_to_entry = tk.Spinbox(left_frame, from_=0, to=100, width=5)
        cut_to_entry.grid(row=7, column=7, sticky=tk.W)

        intro_select = ttk.Combobox(left_frame, values=["cloud", "connect", "frame", "travel", "welcome"])
        intro_select.grid(row=8, column=4, pady=2, sticky=tk.W)

        default_text = "Nhập đường dẫn âm thanh tại đây"
        self.entry_default = Entry(left_frame, fg='gray')
        self.entry_default.insert(0, default_text)
        self.entry_default.bind("<FocusIn>", self.on_entry_click)
        self.entry_default.grid(row=10, column=4, columnspan=20, ipadx=70, ipady=2, pady=5, sticky=tk.W)
        accept_audio_link = tk.Button(left_frame, text="Chọn", command=self.open_audio_file)
        accept_audio_link.grid(row=10, column=40, columnspan=10, pady=1, sticky=tk.W)

        default_text_video = "Nhập đường dẫn video tại đây"
        self.entry_video_default = Entry(left_frame, fg='gray')
        self.entry_video_default.insert(0, default_text_video)
        self.entry_video_default.bind("<FocusIn>", self.on_entry_video_click)
        self.entry_video_default.grid(row=11, column=4, columnspan=20, ipadx=70, ipady=2, pady=5, sticky=tk.W)
        accept_audio_link = tk.Button(left_frame, text="Chọn", command=self.open_video_file)
        accept_audio_link.grid(row=11, column=40, columnspan=10, pady=1, sticky=tk.W)

        default_text_overlay_video = "Nhập chữ chèn cho video tại đây"
        self.entry_overlay_default = Entry(left_frame, fg='gray')
        self.entry_overlay_default.insert(0, default_text_overlay_video)
        self.entry_overlay_default.bind("<FocusIn>", self.on_entry_overlay_click)
        self.entry_overlay_default.grid(row=12, column=4, columnspan=20, ipadx=70, ipady=2, pady=5, sticky=tk.W)
        label_colour = tk.Label(left_frame, text="Màu chữ:")
        label_colour.grid(row=12, column=40, sticky=tk.W)
        set_colour_text = ttk.Combobox(left_frame,
                                       values=["black",
                                               "white",
                                               "red",
                                               "green",
                                               "blue",
                                               "gray",
                                               "green",
                                               "yellow",
                                               "purple"],
                                       width=5)
        set_colour_text.grid(row=12, column=41, pady=2, sticky=tk.W)
        size_label = tk.Label(left_frame, text="Kích cỡ:")
        size_label.grid(row=12, column=42, sticky=tk.W)
        size_text = ttk.Spinbox(left_frame, from_=0, to=100, width=3)
        size_text.grid(row=12, column=43, sticky=tk.W)
        back_ground_text_label = tk.Label(left_frame, text="Màu nền:")
        back_ground_text_label.grid(row=12, column=44, sticky=tk.W)
        back_ground_text = ttk.Combobox(left_frame,
                                        values=["black",
                                                "white",
                                                "red",
                                                "green",
                                                "blue",
                                                "gray",
                                                "green",
                                                "yellow",
                                                "purple"],
                                        width=5)
        back_ground_text.grid(row=12, column=45, padx=5, sticky=tk.W)

        def reset():
            result_label['text'] = ""
            self.create_left_widgets(left_frame)
            tree.delete(*tree.get_children())

        def start():
            # count_checkbox = sum(var.get() for var in self.checkbox_vars)
            count_checkbox = 0
            result_label['text'] = ""
            list_videos = self.get_column_data(tree, 1)
            list_videos_if_many_check_boxes = []
            if self.checkbox_vars[0].get() == 1:
                # print(f'{self.checkbox_vars[0]} đã được chọn')
                pass

            if self.checkbox_vars[1].get() == 1:
                begin_time = cut_from_to_button.get()
                end_time = cut_to_entry.get()
                Movie.sub_clip_many(list_videos, get_time(begin_time), get_time(end_time))
                count_checkbox = count_checkbox+1

            if self.checkbox_vars[2].get() == 1:
                get_intro = intro_select.get()
                count_checkbox = count_checkbox+1
                if count_checkbox == 2:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                else:
                    list_videos_if_many_check_boxes = list_videos
                for video in list_videos_if_many_check_boxes:
                    Movie.concatenate([get_intro_path(get_intro), video], video)

            if self.checkbox_vars[3].get() == 1:
                count_checkbox = count_checkbox+1
                list_videos_if_many_check_boxes = []
                if count_checkbox == 3:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 2:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                else:
                    list_videos_if_many_check_boxes = list_videos
                Movie.remove_audio_many(list_videos_if_many_check_boxes)

            if self.checkbox_vars[4].get() == 1:
                count_checkbox = count_checkbox+1
                list_videos_if_many_check_boxes = []
                input_audio = self.entry_default.get()
                if count_checkbox == 4:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 3:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 2:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                else:
                    list_videos_if_many_check_boxes = list_videos
                Movie.add_one_audio_to_many_videos(input_audio, list_videos_if_many_check_boxes)

            if self.checkbox_vars[5].get() == 1:
                count_checkbox = count_checkbox+1
                list_videos_if_many_check_boxes = []
                input_video = self.entry_video_default.get()
                if count_checkbox == 5:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 4:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 3:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 2:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                else:
                    list_videos_if_many_check_boxes = list_videos
                for video in list_videos_if_many_check_boxes:
                    Movie.concatenate([input_video, video], video)

            if self.checkbox_vars[6].get() == 1:
                count_checkbox = count_checkbox+1
                list_videos_if_many_check_boxes = []
                text = self.entry_overlay_default.get()
                colour = set_colour_text.get()
                size = int(size_text.get())
                bg_colour = back_ground_text.get()
                if count_checkbox == 6:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 5:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 4:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 3:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                elif count_checkbox == 2:
                    for video in list_videos:
                        video1 = f"{video[:-4]}_final.mp4"
                        list_videos_if_many_check_boxes.append(video1)
                else:
                    list_videos_if_many_check_boxes = list_videos
                for video in list_videos_if_many_check_boxes:
                    Movie.overlay_text(video, text, colour, size, bg_colour)

            if self.checkbox_vars[7].get() == 1:
                # print(f'{self.checkbox_vars[7]} đã được chọn')
                pass

            result_label['text'] = "Done!"
            start_button.config(text="Bắt đầu", state=tk.NORMAL)

        def submit_button():
            start_button.config(text="Đợi...", state=tk.DISABLED)
            x = threading.Thread(target=start)
            if not x.is_alive():
                x.start()

        reset_button = tk.Button(left_frame, text="Đặt lại", width=7, command=reset)
        reset_button.grid(row=14, column=7, pady=5, sticky=tk.W)

        start_button = tk.Button(left_frame, text="Bắt đầu", width=7, command=submit_button)
        start_button.grid(row=15, column=7, pady=5, sticky=tk.W)

        result_label = tk.Label(left_frame, text="")
        result_label.grid(row=16, column=7)

    def create_table(self, right_frame):
        global tree, data
        headers = ("STT", "Đường dẫn", "Thời gian", "Tình trạng", "Hành động")
        headers_show = ("STT", "Đường dẫn", "Thời gian", "Tình trạng", "Hành động")
        widths = (7, 350, 50, 50, 55)
        anchors = ("center", "w", "center", "center", "center")
        style = ttk.Style(right_frame)
        style.theme_use("classic")
        style.configure("Treeview",
                        background="#f8f8ff",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#f0f8ff", )
        style.configure('Treeview.Heading', background="PowderBlue", font=('Hevetica', 11))
        tree = ttk.Treeview(right_frame, columns=("STT", "Đường dẫn", "Thời gian", "Tình trạng", "Hành động"),
                            show="headings")
        tree['columns'] = headers
        tree['displaycolumns'] = headers_show
        for i in range(len(headers_show)):
            tree.heading(f"#{i + 1}", text=headers_show[i], anchor='center')
            tree.column(f"#{i + 1}", anchor=anchors[i], width=widths[i])
        tree['show'] = 'headings'

        delete_button = tk.Button(right_frame, text="Xóa", width=7, command=remove_item)
        delete_button.pack(side='top', anchor='ne', padx=5, pady=5, fill="none", expand=False)

        data = []
        for row in data:
            tree.insert("", "end", values=row)

        # Add the Tree view to the frame
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(right_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")

        # Configure the Tree view to use the vertical scrollbar
        tree.configure(yscrollcommand=vsb.set)


class PageThree:
    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.frame = tk.Frame(root)

        label = tk.Label(self.frame, text="Re-up", font=('Arial', 18))
        label.pack()

    def show(self):
        self.app.show_page(self)


if __name__ == "__main__":
    root = tk.Tk()
    app = MiniTool(root)
    root.geometry("1500x630")
    root.mainloop()
