from time import sleep
from math import floor
from os.path import basename, abspath, join, exists, dirname, isfile
from os import makedirs
from shutil import rmtree
from sys import argv
# GUI
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
# Converters
from markdown import markdown
from pdf2image import convert_from_path
import pdfkit
# Custom css for markdown to html convertion
CSS_FILE = "./dark_style.css"
FRONT_PAGE_IMG = "./resources/front-page.png"
PDF_OPTIONS = {
        "page-size": "A4",
        "margin-top": "0.0in",
        "margin-right": "0.0in",
        "margin-left": "0.0in",
        "margin-bottom": "0.0in",
        "encoding": "UTF-8",
        "no-outline": None,
        "quiet": ""
        }

class MyLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        BoxLayout.__init__(self, *args, **kwargs)

###   ###   ###   ###   ###  Export confirmation popup ###   ###   ###   ###   ###   ###
export_layout = BoxLayout(orientation="vertical", padding=[0.1, 0.1, 0.1, 0.1])
eBtn_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.4))
eLabl = Label(text="Export selected document to pdf?", size_hint=(1, 0.6))
eBtn1 = Button(text="Yes", size_hint=(0.5, 1))
eBtn2 = Button(text="No", size_hint=(0.5, 1))
export_layout.add_widget(eLabl)
eBtn_layout.add_widget(eBtn1)
eBtn_layout.add_widget(eBtn2)
export_layout.add_widget(eBtn_layout)

export_popup = Popup(title="Export to pdf",
        content = export_layout,
        size_hint = (None, None),
        size = (400, 200))
###   ###   ###   ###   ###   ###   ###   ###   ###   ###   ###   ###   ###   ###   ###

class TestBarApp(App):
    def __init__(self):
        super().__init__()
        self.current_img = FRONT_PAGE_IMG
        self.file_chooser_active = False
        self.img_index = 0
        self.amount = 0
        self.img_basename = ""
        self.selected_file = ""
        self.export_open = False
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, ascii_code, keycode, text, 
            modifiers):
        # Ctrl + e/E -> export to pdf
        if ascii_code == 101 and modifiers == ["ctrl"]:
            self.export()
        # j/J        -> page down
        elif ascii_code == 106:
            self.next_img(self.root.ids["image"])
        # k/K        -> page up
        elif ascii_code == 107:
            self.prev_img(self.root.ids["image"])
        # Ctrl + r/R -> reload file
        elif ascii_code == 114 and modifiers == ["ctrl"]:
            self.refresh(self.root.ids["image"])
        # Ctrl + o/O  -> select file
        elif ascii_code == 111 and modifiers == ["ctrl"]:
            self.toggle_file_chooser(self.root.ids["file_chooser"],
                    self.root.ids["image"])
        elif ascii_code == 13 :
            if self.export_open:
                self.export_and_close()
            elif self.file_chooser_active:
                self.select_file(self.root.ids["file_chooser"],
                        self.root.ids["image"])
    
    def build(self):
        eBtn1.bind(on_release=self.export_and_close)
        eBtn2.bind(on_release=export_popup.dismiss)
        self.rootlayout = MyLayout()
        return self.rootlayout

    def on_start(self):
        self.root.ids["file_chooser"].path = abspath("./")
        if len(argv) == 2:
            self.select_file_path("./" + argv[1], self.root.ids["image"])

    def on_stop(self):
        rmtree('./.mdtmp', ignore_errors=True)

    def create_images(self, path):
        images = convert_from_path(path)
        file_name = basename(path)
        # Hidden file special case
        if file_name[0] == ".":
            file_name = file_name[1::]
        file_name = file_name.split(".")[0]
        for index, image in enumerate(images):
            image.save("./.mdtmp/" + file_name + str(index) + ".png")
        self.amount = len(images)
        self.img_basename = "./.mdtmp/" + file_name

    def toggle_file_chooser(self, file_chooser, img):
        # Makes image widget invisible and enlarges file chooser
        # since kivy doesnt allow multiple windows easily
        print(self.root.ids["button_container"].height)
        file_chooser_height = self.root.height - floor(self.root.ids["button_container"].height)
        if self.file_chooser_active:
            img.size = file_chooser.size
            img.size_hint = file_chooser.size_hint
            file_chooser.size = (0, 0)
            file_chooser.size_hint = (0, 0)
        else:
            file_chooser.size = img.size
            file_chooser.height = file_chooser_height
            file_chooser.size_hint = img.size_hint
            file_chooser.size_hint_y = None
            img.size = (0, 0)
            img.size_hint = (0, 0)
        self.file_chooser_active = not self.file_chooser_active
    
    def select_file(self, file_chooser, img):
        self.selected_path = file_chooser.path
        self.selected_file = join(file_chooser.path, file_chooser.selection[0])
        self.toggle_file_chooser(file_chooser, img)
        pdf_file = self.create_pdf(self.selected_file)
        self.create_images(pdf_file)
        self.img_index = 0
        self.select_image(img, 0)
    
    def select_file_path(self, path, img):
        self.selected_path = dirname(path)
        self.selected_file = path
        pdf_file = self.create_pdf(self.selected_file)
        self.create_images(pdf_file)
        self.img_index = 0
        self.select_image(img, 0)

    def create_pdf(self, path):
        with open(path, "r") as f:
            html_text = markdown(f.read(), output_format="html5")
        output = "./.mdtmp/" + basename(path).split(".")[0] + ".pdf"
        pdfkit.from_string(html_text, output, options=PDF_OPTIONS, css=CSS_FILE)
        return output

    def export(self):
        if self.selected_file == "":
            # TODO: Add error handling and messaging
            return
        with open(self.selected_file, "r") as f:
            html_text = markdown(f.read(), output_format="html4")
        output = "./" + basename(self.selected_file).split(".")[0] + ".pdf"
        i = 0
        while isfile(output):
            output = ("./" + basename(self.selected_file).split(".")[0] 
                    + str(i) + ".pdf")
            i += 1
        pdfkit.from_string(html_text, output, options=PDF_OPTIONS, css=CSS_FILE)

    def export_and_close(self, *args, **kwargs):
        self.export()
        export_popup.dismiss()
        self.export_open = False

    def open_export_popup(self):
        self.export_open = True
        export_popup.open()
    
    def select_image(self, img, index):
        img.source = self.img_basename + str(index) + ".png"
        img.reload()

    def next_img(self, img):
        self.img_index += 1
        if self.img_index == self.amount:
            self.img_index -= 1
        self.select_image(img, self.img_index)

    
    def prev_img(self, img):
        self.img_index -= 1
        if self.img_index == -1:
            self.img_index = 0
        self.select_image(img, self.img_index)

    def refresh(self, img):
        pdf_file = self.create_pdf(self.selected_file)
        self.create_images(pdf_file)
        self.select_image(img, self.img_index)

if __name__ == "__main__":
    if not exists("./.mdtmp"):
        makedirs("./.mdtmp")
    TestBarApp().run()
