import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget, QLineEdit, \
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QDateEdit, QFileDialog, QDialog
from PySide6.QtCore import Qt, QDate, QDateTime
from PySide6.QtGui import QColor, QPainter, QPen

App = QApplication([])
main_windows = QWidget()

calendar = QCalendarWidget()
task_box = QListWidget()
task_box.setStyleSheet("""
    QListWidget {
        font-size: 20px;
        font-family: Arial, sans-serif;
        color: #e6e6e6;
        background-color: #595959;
        border-radius: 5px;
        padding: 10px;
    }
    QListWidget::item {
        background-color: #595959;
        border: 3px solid #666;
        border-radius: 15px;
        margin: 5px;
        padding: 10px;
    }
    QListWidget::item:hover {
        background-color: #777;
        border-color: #e6e6e6;
    }
""")

task_line_edit = QLineEdit()
task_line_edit.setPlaceholderText("Introdu Task-ul")
task_line_edit.setClearButtonEnabled(True)
task_line_edit.setMaxLength(30)
task_line_edit.setStyleSheet("""
    QLineEdit {
        font-size: 20px;
        font-family: Arial, sans-serif;
        background-color: #333;
        color: #e6e6e6;
        border: 2px solid #777;
        border-radius: 5px;
        padding: 10px;
    }
""")

tasks_by_date = {}

TASKS_FILE = "tasks.json"


def load_tasks():
    global tasks_by_date
    try:
        with open(TASKS_FILE, "r") as file:
            tasks_by_date = json.load(file)
    except FileNotFoundError:
        tasks_by_date = {}


def save_tasks():
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks_by_date, file, indent=4)


def add_task():
    task_text = task_line_edit.text()
    selected_date = calendar.selectedDate().toString(Qt.ISODate)

    if task_text:
        if selected_date not in tasks_by_date:
            tasks_by_date[selected_date] = []
        tasks_by_date[selected_date].append(task_text)

        task_item = QListWidgetItem(f" {task_text} ")
        background_color = QColor("#595959")
        task_item.setBackground(background_color)
        task_item.setForeground(QColor('#e6e6e6'))
        task_item.setTextAlignment(Qt.AlignLeft)

        task_box.addItem(task_item)
        task_line_edit.clear()

        save_tasks()
        update_calendar_markers()


def update_task_list():
    selected_date = calendar.selectedDate().toString(Qt.ISODate)
    task_box.clear()

    if selected_date in tasks_by_date:
        for task in tasks_by_date[selected_date]:
            task_item = QListWidgetItem(f" {task}")
            task_item.setBackground(QColor("#595959"))
            task_item.setForeground(QColor('#e6e6e6'))
            task_item.setTextAlignment(Qt.AlignLeft)

            task_box.addItem(task_item)


def delete_task(item):
    selected_date = calendar.selectedDate().toString(Qt.ISODate)
    task_text = item.text().strip()

    if selected_date in tasks_by_date and task_text in tasks_by_date[selected_date]:
        tasks_by_date[selected_date].remove(task_text)
        task_box.takeItem(task_box.row(item))

        save_tasks()
        update_calendar_markers()


def delete_all_tasks():
    selected_date = calendar.selectedDate().toString(Qt.ISODate)

    if selected_date in tasks_by_date:
        reply = QMessageBox.question(main_windows, 'Confirmare Ștergere',
                                     f"Doriți să ștergeți toate task-urile pentru data '{selected_date}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            tasks_by_date[selected_date].clear()
            update_task_list()

        save_tasks()
        update_calendar_markers()


def export_tasks():
    start_date, end_date, ok = get_date_range()

    if ok:
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(main_windows, "Salvează fișierul de export", "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            with open(file_name, 'w') as file:
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.toString(Qt.ISODate)
                    if date_str in tasks_by_date:
                        file.write(f"{date_str}\n")
                        for task in tasks_by_date[date_str]:
                            file.write(f"  - {task}\n")
                    current_date = current_date.addDays(1)

            QMessageBox.information(main_windows, "Exportare finalizată",
                                    f"Task-urile au fost exportate în {file_name}.")


def get_date_range():
    start_date_edit = QDateEdit()
    start_date_edit.setDate(QDate.currentDate())
    start_date_edit.setDisplayFormat("yyyy-MM-dd")

    end_date_edit = QDateEdit()
    end_date_edit.setDate(QDate.currentDate())
    end_date_edit.setDisplayFormat("yyyy-MM-dd")

    date_dialog = QDialog(main_windows)
    date_layout = QVBoxLayout()
    date_layout.addWidget(QLabel("Selectați data de început:"))
    date_layout.addWidget(start_date_edit)
    date_layout.addWidget(QLabel("Selectați data de sfârșit:"))
    date_layout.addWidget(end_date_edit)

    buttons = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")

    buttons.addWidget(ok_button)
    buttons.addWidget(cancel_button)

    date_layout.addLayout(buttons)

    date_dialog.setLayout(date_layout)

    ok_button.clicked.connect(date_dialog.accept)
    cancel_button.clicked.connect(date_dialog.reject)

    if date_dialog.exec() == QDialog.Accepted:
        return start_date_edit.date(), end_date_edit.date(), True
    return QDate(), QDate(), False


def update_calendar_markers():
    calendar.updateCells()


def paint_cell(painter, rect, date):
    QCalendarWidget.paintCell(calendar, painter, rect, date)

    selected_date = date.toString(Qt.ISODate)
    if selected_date in tasks_by_date and tasks_by_date[selected_date]:
        painter.setBrush(QColor(139, 0, 0, 100))
        painter.drawRect(rect)


calendar.paintCell = paint_cell

task_line_edit.returnPressed.connect(add_task)
calendar.selectionChanged.connect(update_task_list)

delete_all_button = QPushButton("Șterge toate task-urile")
delete_all_button.setStyleSheet("""
    QPushButton {
        font-size: 20px;
        font-family: Arial, sans-serif;
        background-color: #cc4c4c;
        color: #fff;
        border-radius: 5px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #e64c4c;
    }
""")
delete_all_button.clicked.connect(delete_all_tasks)

export_button = QPushButton("Exportă task-uri")
export_button.setStyleSheet("""
    QPushButton {
        font-size: 20px;
        font-family: Arial, sans-serif;
        background-color: #4c8ccf;
        color: #fff;
        border-radius: 5px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #6fa3d4;
    }
""")
export_button.clicked.connect(export_tasks)

main_layout = QVBoxLayout()
row1 = QHBoxLayout()
row1_task_slider = QVBoxLayout()

row1.addWidget(calendar)
row1_task_slider.addWidget(task_line_edit)
row1_task_slider.addWidget(task_box)
row1_task_slider.addWidget(delete_all_button)
row1_task_slider.addWidget(export_button)
row1.addLayout(row1_task_slider)

main_layout.addLayout(row1)

main_windows.setLayout(main_layout)

load_tasks()

main_windows.show()
sys.exit(App.exec())
