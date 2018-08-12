from time import sleep
from math import floor
from os.path import basename, abspath, join, exists, dirname
from os import makedirs
from shutil import rmtree
from sys import argv
# GUI
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# Converters
from markdown import markdown
from pdf2image import convert_from_path
import pdfkit
# Custom css for markdown to html convertion
CSS_FILE = "./style.css"

class MyLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        BoxLayout.__init__(self, *args, **kwargs)

class TestBarApp(App):
    def __init__(self):
        super().__init__()
        self.current_img = "./resources/front-page.png"
        self.file_chooser_active = False
        self.img_index = 0
        self.amount = 0
        self.img_basename = ""
        self.selected_file = ""
    
    def build(self):
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
        #Hidden file
        if file_name[0] == ".":
            file_name = file_name[1::]
        file_name = file_name.split(".")[0]
        for index, image in enumerate(images):
            image.save("./.mdtmp/" + file_name + str(index) + ".png")
        self.amount = len(images)
        self.img_basename = "./.mdtmp/" + file_name

    def toggle_file_chooser(self, file_chooser, img):
        if self.file_chooser_active:
            img.size = file_chooser.size
            img.size_hint = file_chooser.size_hint
            file_chooser.size = (0, 0)
            file_chooser.size_hint = (0, 0)
        else:
            file_chooser.size = img.size
            file_chooser.size_hint = img.size_hint
            img.size = (0, 0)
            img.size_hint = (0, 0)
        self.file_chooser_active = not self.file_chooser_active
    
    def select_file(self, file_chooser, img):
        self.selected_path = file_chooser.path
        self.selected_file = join(file_chooser.path, file_chooser.selection[0])
        pdf_file = self.create_pdf(self.selected_file)
        self.create_images(pdf_file)
        self.img_index = 0
        self.toggle_file_chooser(file_chooser, img)
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
            html_text = markdown(f.read(), output_format="html4")
        output = "./.mdtmp/" + basename(path).split(".")[0] + ".pdf"
        pdfkit.from_string(html_text, output, css=CSS_FILE)
        return output
    
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
