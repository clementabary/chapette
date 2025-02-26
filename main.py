import os
import sys

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtCore import Qt

from music21 import converter, note, chord  #, expressions
from valve_fingerings import VALVE_FINGERINGS


def get_formatted_pitch(n: note.Note):
    return n.nameWithOctave


def add_valve_fingerings_to(sheet_filename: str, output_path: str):
    score = converter.parse(sheet_filename)
    
    for element in score.flatten().notes:
        if isinstance(element, note.Note):
            # Single note, handle fingering
            pitch = get_formatted_pitch(element.pitch)
            if pitch in VALVE_FINGERINGS:
                fingering_comment = VALVE_FINGERINGS[pitch]
                # text_expr = expressions.TextExpression(fingering_comment)
                # text_expr.style.size = font_size
                # element.expressions.append(text_expr)
                element.addLyric(fingering_comment)
        elif isinstance(element, chord.Chord):
            # Chord, iterate through notes and handle fingerings for each
            fingering_comment = ""
            for note_in_chord in element.notes:
                if len(fingering_comment) != 0:
                    fingering_comment = "\n" + fingering_comment
                formatted_pitch = get_formatted_pitch(note_in_chord.pitch)
                if formatted_pitch in VALVE_FINGERINGS:
                    fingering_comment = VALVE_FINGERINGS[formatted_pitch] + fingering_comment
            # text_expr = expressions.TextExpression(fingering_comment)
            # text_expr.style.size = font_size
            # element.expressions.append(text_expr)
            element.addLyric(fingering_comment)
    score.write('musicxml', fp=output_path)


class DragDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.setWindowTitle("🎺 Chapette 🎺")
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2E3440;
                border-radius: 15px;
            }
            QLabel {
                color: #D8DEE9;
                font-size: 18px;
                font-weight: bold;
                border: 1px dashed #88C0D0;
                border-radius: 10px;
                padding: 40px;
                background-color: rgba(46, 52, 64, 0.5);
            }
            """
        )

        # Drag-and-Drop Label
        self.label = QLabel("🗂 Drag your .mxl file here", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)

        # Enable Drag & Drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Only accept files with the .mxl extension
        file_path = event.mimeData().urls()[0].toLocalFile()
        if file_path.endswith('.mxl'):
            event.acceptProposedAction()
        else:
            self.show_invalid_file_popup()
            event.ignore()
            
    def show_invalid_file_popup(self):
        """Show a pop-up message if the file type is invalid."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Set custom icon
        msg.setIconPixmap(QIcon("assets/error.png").pixmap(64, 64))
        
        msg.setWindowTitle("Invalid File Type")
        msg.setText("Only files with the .mxl extension are allowed!\n\nExport it with MuseScore 📁")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            input_file = urls[0].toLocalFile()
            
            extension = os.path.splitext(input_file)[-1]
            

            # Open a file dialog for the user to choose the output location
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Save Processed File",
                input_file.replace(extension, f"_with_fingerings{extension}"),
                f"Text Files (*.{extension});;All Files (*)"
            )

            # If the user selects a file path
            if output_file:
                _ = add_valve_fingerings_to(input_file, output_file)
                self.label.setText(f"✅ Processed file saved at:\n{output_file}")


app = QApplication(sys.argv)
window = DragDropWindow()
window.show()
app.exec()
