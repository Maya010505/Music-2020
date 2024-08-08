import sys

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt5.QtCore import QUrl, QAbstractListModel, Qt, QModelIndex
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist

from player import Ui_MainWindow


def time(ms):
    second = round(ms / 1000)
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    if hour:
        return "%d:%02d:%02d" % (hour, minute, second)
    else:
        return "%d:%02d" % (minute, second)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.player = QMediaPlayer()

        self.player.play()

        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        # Настраиваем плейлист

        self.play.clicked.connect(self.player.play)  # Кнопка проигрывания трека
        self.pause.clicked.connect(self.player.pause)  # Кнопка паузы
        self.stop.clicked.connect(self.player.stop)  # Кнопка остановки трека
        self.volume.valueChanged.connect(self.player.setVolume)  # Ползунок регулирования звука

        self.previous.clicked.connect(self.playlist.previous)  # Кнопка перелистывания трека назад
        self.next.clicked.connect(self.playlist.next)  # Кнопка перелистывания трека вперед

        self.model = PlaylistModel(self.playlist)
        self.tracks.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.pl_position_changed)

        selection_model = self.tracks.selectionModel()
        selection_model.selectionChanged.connect(self.pl_selection_changed)

        self.player.durationChanged.connect(self.duration_t)
        self.player.positionChanged.connect(self.all_t)
        self.slider.valueChanged.connect(self.player.setPosition)

        self.file.triggered.connect(self.add_tracks)

        self.setAcceptDrops(True)  # Перетаскивание откуда-угодно треков в плейлист

    def dragEnterEvent(self, file):
        # Проверка на то, можно ли перетащить файл в данное приложение
        if file.mimeData().hasUrls():
            file.acceptProposedAction()

    def dropEvent(self, file):
        # Добавляет в плейлист треки
        for url in file.mimeData().urls():
            self.playlist.addMedia(QMediaContent(url))

        self.model.layoutChanged.emit()

    def add_tracks(self):
        path, _ = QFileDialog.getOpenFileName(self,
                                              'Open file', '',
                                              'mp3 Audio (*.mp3)')

        if path:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))

        self.model.layoutChanged.emit()

    def duration_t(self, duration):
        self.slider.setMaximum(duration)

        if duration >= 0:
            self.all_track.setText(time(duration))

    def all_t(self, position):
        if position >= 0:
            self.duraction_track.setText(time(position))

        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)
        # Обновление положения ползунка

    def pl_selection_changed(self, i):
        x = i.indexes()[0].row()
        self.playlist.setCurrentIndex(x)

    def pl_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.tracks.setCurrentIndex(ix)


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist):
        super().__init__()
        self.playlist = playlist

    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index = QModelIndex):
        return self.playlist.mediaCount()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
