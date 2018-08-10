from math import floor
from kivy.app import App
from kivy.core.window import Window
from pdf2image import convert_from_path
from os.path import basename, abspath, join

class TestBarApp(App):
    def __init__(self):
        super().__init__()
        self.current_img = "./tmp/kek.png"
        self.file_chooser_active = False

    def button1(self, img):
        img.source = "./tmp/kek2.png"
        img.reload()

    def create_images(self, path):
        images = convert_from_path(path)
        file_name = basename(path)
        #Hidden file
        if file_name[0] == ".":
            file_name = file_name[1::]
        file_name = file_name.split(".")[0]
        for index, image in enumerate(images):
            image.save("./tmp/" + file_name + str(index) + ".png")

    def toggle_file_chooser(self, file_chooser, img):
        if self.file_chooser_active:
            img.size = file_chooser.size
            img.size_hint = file_chooser.size_hint
            file_chooser.size = (0, 0)
            file_chooser.size_hint = (0, 0)
        else:
            # Prevent flashing if possible
            file_chooser.path = abspath("./")
            file_chooser.size = img.size
            file_chooser.size_hint = img.size_hint
            img.size = (0, 0)
            img.size_hint = (0, 0)
        self.file_chooser_active = not self.file_chooser_active

    def select_file(self, file_chooser, img):
        self.create_images(join(file_chooser.path, 
            file_chooser.selection[0]))
        self.toggle_file_chooser(file_chooser, img)


if __name__ == "__main__":
    TestBarApp().run()
