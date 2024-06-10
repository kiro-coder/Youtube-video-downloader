from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserIconView
from pytube import YouTube
from threading import Thread

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.start_image = Image(
            source='start_image.png',
            size_hint=(1, 0.8)
        )

        self.go_button = Button(
            text='Go to App',
            size_hint=(1, 0.2)
        )
        self.go_button.bind(on_press=self.go_to_app)

        self.layout.add_widget(self.start_image)
        self.layout.add_widget(self.go_button)
        self.add_widget(self.layout)

    def go_to_app(self, instance):
        self.manager.current = 'app'

class YouTubeDownloaderScreen(Screen):
    def __init__(self, **kwargs):
        super(YouTubeDownloaderScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.url_input = TextInput(
            hint_text='Enter YouTube video URL',
            multiline=False,
            size_hint=(1, 0.1)
        )

        self.quality_spinner = Spinner(
            text='Select Quality',
            values=('1080p', '720p', '480p', '360p'),
            size_hint=(1, 0.1)
        )

        self.choose_path_button = Button(
            text='Choose Save Location',
            size_hint=(1, 0.1)
        )
        self.choose_path_button.bind(on_press=self.open_filechooser)

        self.download_button = Button(
            text='Download',
            size_hint=(1, 0.1)
        )
        self.download_button.bind(on_press=self.start_download)

        self.progress_bar = ProgressBar(
            max=100,
            size_hint=(1, 0.1)
        )

        self.status_label = Label(
            text='Enter URL, select quality and press Download',
            size_hint=(1, 0.1)
        )

        self.back_button = Button(
            text='Back to Start',
            size_hint=(1, 0.1)
        )
        self.back_button.bind(on_press=self.go_to_start)

        self.layout.add_widget(self.url_input)
        self.layout.add_widget(self.quality_spinner)
        self.layout.add_widget(self.choose_path_button)
        self.layout.add_widget(self.download_button)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.back_button)
        self.add_widget(self.layout)

        self.save_path = None

    def open_filechooser(self, instance):
        self.filechooser = FileChooserIconView()
        filechooser_layout = BoxLayout(orientation='vertical')
        
        self.select_folder_button = Button(
            text='Select This Folder',
            size_hint=(1, 0.1)
        )
        self.select_folder_button.bind(on_press=self.select_this_folder)

        self.back_button_filechooser = Button(
            text='Back to App',
            size_hint=(1, 0.1)
        )
        self.back_button_filechooser.bind(on_press=self.go_to_app)

        filechooser_layout.add_widget(self.filechooser)
        filechooser_layout.add_widget(self.select_folder_button)
        filechooser_layout.add_widget(self.back_button_filechooser)

        self.filechooser_popup = Screen(name='filechooser')
        self.filechooser_popup.add_widget(filechooser_layout)
        
        self.manager.add_widget(self.filechooser_popup)
        self.manager.current = 'filechooser'

    def select_this_folder(self, instance):
        self.save_path = self.filechooser.path
        self.manager.current = 'app'
        self.manager.remove_widget(self.filechooser_popup)

    def start_download(self, instance):
        video_url = self.url_input.text
        quality = self.quality_spinner.text
        if video_url and quality != 'Select Quality' and self.save_path:
            self.status_label.text = "Downloading..."
            Thread(target=self.download_video, args=(video_url, quality)).start()
        else:
            self.status_label.text = "Please fill in all fields and select save location."

    def download_video(self, url, quality):
        try:
            yt = YouTube(url, on_progress_callback=self.update_progress)
            stream = yt.streams.filter(res=quality, progressive=True).first()
            if not stream:
                self.status_label.text = f"Error: Quality {quality} not available"
                return
            stream.download(output_path=self.save_path)
            self.status_label.text = "Download completed!"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar.value = percentage

    def go_to_start(self, instance):
        self.manager.current = 'start'

    def go_to_app(self, instance):
        self.manager.current = 'app'

class YouTubeDownloaderApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(StartScreen(name='start'))
        self.sm.add_widget(YouTubeDownloaderScreen(name='app'))
        return self.sm

if __name__ == '__main__':
    YouTubeDownloaderApp().run()
