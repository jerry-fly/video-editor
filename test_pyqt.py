#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5 测试')
    window.setGeometry(100, 100, 300, 200)
    
    layout = QVBoxLayout()
    label = QLabel('PyQt5 测试成功!')
    layout.addWidget(label)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 