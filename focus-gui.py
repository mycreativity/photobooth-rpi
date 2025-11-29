#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# Oorspronkelijk script van Jim Easterbrook, aangepast voor Canon EOS 750D
#
# BELANGRIJKE OPMERKING: De 750D is een modernere camera. Dit script is aangepast
# om in de 'continuous' mode altijd de snelle live preview functie te gebruiken
# in plaats van de trage full capture functie.

from __future__ import print_function

import io
import logging
import math
import sys

from PIL import Image, ImageChops, ImageStat
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt

import gphoto2 as gp


class CameraHandler(QtCore.QObject):
    new_image = QtCore.pyqtSignal(object)

    def __init__(self):
        self.do_next = QtCore.QEvent.registerEventType()
        super(CameraHandler, self).__init__()
        self.running = False
        # initialise camera
        self.camera = gp.Camera()
        self.camera.init()
        # get camera config tree
        self.config = self.camera.get_config()
        self.old_capturetarget = None
        
        # get the camera model
        OK, camera_model = gp.gp_widget_get_child_by_name(
            self.config, 'cameramodel')
        if OK < gp.GP_OK:
            OK, camera_model = gp.gp_widget_get_child_by_name(
                self.config, 'model')
        if OK >= gp.GP_OK:
            self.camera_model = camera_model.get_value()
            print('Camera model:', self.camera_model)
        else:
            print('No camera model info')
            self.camera_model = ''
            
        # Oude logica voor 350D/onbekende modellen (niet relevant voor 750D)
        if self.camera_model == 'unknown':
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                self.config, 'capturesizeclass')
            if OK >= gp.GP_OK:
                value = capture_size_class.get_choice(2)
                capture_size_class.set_value(value)
                self.camera.set_config(self.config)
        else:
            # Zet de camera in preview-modus om de spiegel op te klappen (belangrijk voor Canon)
            try:
                gp.gp_camera_capture_preview(self.camera)
            except gp.GPhoto2Error as e:
                print(f"Waarschuwing: Kan preview niet starten. Fout: {e}")

    @QtCore.pyqtSlot()
    def one_shot(self):
        if self.running:
            return
        if not self._set_config():
            return
        
        # Voor een enkele preview: altijd de snelle preview functie gebruiken
        self._do_preview()

    @QtCore.pyqtSlot()
    def continuous(self):
        if self.running:
            self.running = False
            return
        if not self._set_config():
            return
        self.running = True
        self._do_continuous()

    @QtCore.pyqtSlot()
    def take_photo(self):
        if self.running:
            return
        self._reset_config()
        self._do_capture()

    def shut_down(self):
        self.running = False
        self._reset_config()
        self.camera.exit()

    def event(self, event):
        if event.type() != self.do_next:
            return super(CameraHandler, self).event(event)
        event.accept()
        self._do_continuous()
        return True

    def _do_continuous(self):
        if not self.running:
            self._reset_config()
            return
        
        # BELANGRIJKE FIX: Gebruik ALTIJD de snelle preview functie voor een stream, 
        # ongeacht of het cameramodel bekend is (nodig voor Canon 750D)
        self._do_preview()

        # post event to trigger next capture
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_next), Qt.LowEventPriority - 1)

    def _do_preview(self):
        # capture preview image
        try:
            OK, camera_file = gp.gp_camera_capture_preview(self.camera)
        except gp.GPhoto2Error as e:
             print(f'Fout bij opvragen preview: {e}')
             self.running = False
             return
             
        self._send_file(camera_file)

    def _do_capture(self):
        # capture actual image (deze is traag, alleen voor foto's)
        try:
            OK, camera_file_path = gp.gp_camera_capture(
                self.camera, gp.GP_CAPTURE_IMAGE)
            camera_file = self.camera.file_get(
                camera_file_path.folder, camera_file_path.name,
                gp.GP_FILE_TYPE_NORMAL)
            self._send_file(camera_file)
        except gp.GPhoto2Error as e:
            print(f'Fout bij maken van foto: {e}')
            self.running = False

    def _send_file(self, camera_file):
        file_data = camera_file.get_data_and_size()
        image = Image.open(io.BytesIO(file_data))
        image.load()
        self.new_image.emit(image)

    def _set_config(self):
        # ... (configuratie logica, ongewijzigd) ...
        OK, capture_target = gp.gp_widget_get_child_by_name(
            self.config, 'capturetarget')
        if OK >= gp.GP_OK:
            if self.old_capturetarget is None:
                self.old_capturetarget = capture_target.get_value()
            choice_count = capture_target.count_choices()
            for n in range(choice_count):
                choice = capture_target.get_choice(n)
                if 'internal' in choice.lower():
                    capture_target.set_value(choice)
                    self.camera.set_config(self.config)
                    break
        OK, image_format = gp.gp_widget_get_child_by_name(
            self.config, 'imageformat')
        if OK >= gp.GP_OK:
            value = image_format.get_value()
            if 'raw' in value.lower():
                print('Kan geen preview van RAW-afbeeldingen weergeven')
                return False
        return True

    def _reset_config(self):
        if self.old_capturetarget is not None:
            OK, capture_target = gp.gp_widget_get_child_by_name(
                self.config, 'capturetarget')
            if OK >= gp.GP_OK:
                capture_target.set_value(self.old_capturetarget)
                self.camera.set_config(self.config)
                self.old_capturetarget = None


class ImageWidget(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(QtCore.QPoint)

    def mousePressEvent(self, event):
        self.clicked.emit(event.pos())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Focus assistant")
        self.focus_scale = 1.0
        self.zoomed = False
        self.q_image = None
        # main widget
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QGridLayout())
        widget.layout().setRowStretch(8, 1)
        self.setCentralWidget(widget)
        # image display area
        self.image_display = QtWidgets.QScrollArea()
        self.image_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.image_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.image_display.setWidget(ImageWidget())
        self.image_display.setWidgetResizable(True)
        widget.layout().addWidget(self.image_display, 0, 1, 10, 1)
        # histogram
        self.histogram_display = QtWidgets.QLabel()
        self.histogram_display.setPixmap(QtGui.QPixmap(100, 256))
        self.histogram_display.pixmap().fill(Qt.white)
        widget.layout().addWidget(self.histogram_display, 0, 0)
        # focus measurement
        widget.layout().addWidget(QtWidgets.QLabel('Focus:'), 1, 0)
        self.focus_display = QtWidgets.QLabel('-, -, -')
        widget.layout().addWidget(self.focus_display, 2, 0)
        # clipping measurement
        widget.layout().addWidget(QtWidgets.QLabel('Clipping:'), 3, 0)
        self.clipping_display = QtWidgets.QLabel('-, -, -')
        widget.layout().addWidget(self.clipping_display, 4, 0)
        # 'single' button
        single_button = QtWidgets.QPushButton('preview')
        single_button.setShortcut('Ctrl+G')
        widget.layout().addWidget(single_button, 5, 0)
        # 'continuous' button
        continuous_button = QtWidgets.QPushButton('repeat preview')
        continuous_button.setShortcut('Ctrl+R')
        widget.layout().addWidget(continuous_button, 6, 0)
        # 'take photo' button
        take_button = QtWidgets.QPushButton('take photo')
        widget.layout().addWidget(take_button, 7, 0)
        # 'quit' button
        quit_button = QtWidgets.QPushButton('quit')
        quit_button.setShortcut('Ctrl+Q')
        widget.layout().addWidget(quit_button, 9, 0)
        # create camera handler and run it in a separate thread
        self.ch_thread = QtCore.QThread()
        self.camera_handler = CameraHandler()
        self.camera_handler.moveToThread(self.ch_thread)
        self.ch_thread.start()
        # connect things up
        quit_button.clicked.connect(QtWidgets.qApp.closeAllWindows)
        single_button.clicked.connect(self.camera_handler.one_shot)
        continuous_button.clicked.connect(self.camera_handler.continuous)
        take_button.clicked.connect(self.camera_handler.take_photo)
        self.image_display.widget().clicked.connect(self.toggle_zoom)
        self.camera_handler.new_image.connect(self.new_image)

    @QtCore.pyqtSlot(object)
    def new_image(self, image):
        w, h = image.size
        image_data = image.tobytes('raw', 'RGB')
        self.q_image = QtGui.QImage(image_data, w, h, QtGui.QImage.Format_RGB888)
        self._draw_image()
        # generate histogram and count clipped pixels
        histogram = image.histogram()
        q_image = QtGui.QImage(100, 256, QtGui.QImage.Format_RGB888)
        q_image.fill(Qt.white)
        clipping = []
        start = 0
        for colour in (0xff0000, 0x00ff00, 0x0000ff):
            stop = start + 256
            band_hist = histogram[start:stop]
            max_value = float(1 + max(band_hist))
            for x in range(len(band_hist)):
                y = float(1 + band_hist[x]) / max_value
                y = 98.0 * max(0.0, 1.0 + (math.log10(y) / 5.0))
                
                # FIX voor TypeError: converteer de float y naar een integer
                pixel_y = int(round(y))
                
                q_image.setPixel(pixel_y,      x, colour)
                q_image.setPixel(pixel_y + 1, x, colour)
                
            clipping.append(band_hist[-1])
            start = stop
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.histogram_display.setPixmap(pixmap)
        self.clipping_display.setText(
            ', '.join(map(lambda x: '{:d}'.format(x), clipping)))
        # measure focus by summing inter-pixel differences
        shifted = ImageChops.offset(image, 1, 0)
        diff = ImageChops.difference(image, shifted).crop((1, 0, w, h))
        stats = ImageStat.Stat(diff)
        h_rms = stats.rms
        shifted = ImageChops.offset(image, 0, 1)
        diff = ImageChops.difference(image, shifted).crop((0, 1, w, h))
        stats = ImageStat.Stat(diff)
        rms = stats.rms
        for n in range(len(rms)):
            rms[n] += h_rms[n]
        # "auto-ranging" of focus measurement
        while self.focus_scale < 1.0e12 and (max(rms) * self.focus_scale) < 1.0:
            self.focus_scale *= 10.0
            print('+', self.focus_scale)
        while self.focus_scale > 1.0e-12 and (max(rms) * self.focus_scale) > 100.0:
            self.focus_scale /= 10.0
            print('-', self.focus_scale)
        self.focus_display.setText(
            ', '.join(map(lambda x: '{:.2f}'.format(x * self.focus_scale), rms)))

    @QtCore.pyqtSlot(QtCore.QPoint)
    def toggle_zoom(self, pos):
        # ... (zoom logica, ongewijzigd) ...
        self.zoomed = not self.zoomed
        self._draw_image()
        if self.zoomed:
            QtWidgets.QApplication.processEvents()
            size = self.image_display.viewport().size()
            for bar, value in ((self.image_display.horizontalScrollBar(),
                                float(pos.x()) / float(size.width())),
                              (self.image_display.verticalScrollBar(),
                               float(pos.y()) / float(size.height()))):
                min_val = bar.minimum()
                max_val = bar.maximum()
                step = bar.pageStep()
                visible = float(step) / float(step + max_val - min_val)
                if visible >= 0.99:
                    continue
                value = (value - (visible/ 2.0)) / (1.0 - visible)
                bar.setValue(min_val + ((max_val - min_val) * value))

    def _draw_image(self):
        if not self.q_image:
            return
        pixmap = QtGui.QPixmap.fromImage(self.q_image)
        if not self.zoomed:
            pixmap = pixmap.scaled(
                self.image_display.viewport().size(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_display.widget().setPixmap(pixmap)

    def sizeHint(self):
        return QtCore.QSize(4000, 3000)

    def closeEvent(self, event):
        self.camera_handler.shut_down()
        self.ch_thread.quit()
        self.ch_thread.wait()
        return super(MainWindow, self).closeEvent(event)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())