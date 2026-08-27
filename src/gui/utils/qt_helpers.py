"""Qt helpers."""

from PyQt6.QtWidgets import QMessageBox


def info(parent, title, msg):
    QMessageBox.information(parent, title, msg)


def error(parent, title, msg):
    QMessageBox.critical(parent, title, msg)
