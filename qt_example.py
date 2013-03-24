#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from functools import partial
import time
import thread
import threading
import urllib

from PyQt4 import QtCore, QtGui

from engine import async, Task, MultiTask

def print_thread(message=""):
    print message, "in thread", thread.get_ident()


class MainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        button = QtGui.QPushButton(
            "Start",
            clicked=partial(self.do_work,
                            "https://www.google.ru/images/srpr/logo4w.png"),
            )
        button2 = QtGui.QPushButton(
            text="Another work",
            clicked=partial(self.do_work,
                            "http://allisonnazarian.com/wp-content/uploads/2012/02/random.jpg"),
            )
        self.image_label = QtGui.QLabel()
        self.status_label = QtGui.QLabel("Status")
        self.image_result_label = QtGui.QLabel()
        hlayout = QtGui.QHBoxLayout()
        layout.addWidget(button)
        layout.addWidget(button2)
        layout.addWidget(self.status_label)
        hlayout.addWidget(self.image_label)
        hlayout.addWidget(self.image_result_label)
        layout.addLayout(hlayout)

    @async
    def do_work(self, url, *rest):
        print_thread("gui")
        self.image_label.clear()
        self.image_result_label.clear()
        self.status_label.setText("Loading...")
        image = yield Task(self.load_image, url)
        pixmap = QtGui.QPixmap.fromImage(image).scaledToWidth(200)
        self.image_label.setPixmap(pixmap)
        self.status_label.setText("Calculating histogram...")
        histo_image = yield Task(analyze_image, image)
        self.image_result_label.setPixmap(QtGui.QPixmap.fromImage(histo_image))
        self.status_label.setText("Ready")


    def load_image(self, url):
        print "open"
        data = urllib.urlopen(url).read()
        print "downloaded", len(data)
        image = QtGui.QImage.fromData(data)
        return image



def analyze_image(image, height=200):
    print "analyze"
    histogram = [0] * 256
    for i in range(image.width()):
        for j in range(image.height()):
            color = QtGui.QColor(image.pixel(i, j))
            histogram[color.lightness()] += 1

    max_value = max(histogram)
    scale = float(height) / max_value
    width = len(histogram)
    print scale, width, max_value
    histo_img = QtGui.QImage(
        QtCore.QSize(width, height),
        QtGui.QImage.Format_ARGB32
    )
    print histo_img
    histo_img.fill(QtCore.Qt.white)
    p = QtGui.QPainter()
    p.begin(histo_img)
    for i, value in enumerate(histogram):
        y = height - int(value * scale)
        p.drawLine(i, height, i, y)
    p.end()
    return histo_img


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWidget()
    window.resize(640, 480)
    window.show()
    print 'after start'
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()