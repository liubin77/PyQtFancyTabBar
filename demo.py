import sys

from PyQt4.QtGui import *
from fancytabbar import FancyTabWidget

def test():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setGeometry(200, 200, 800, 600)
    tab = FancyTabWidget(window)
    tab1 = QLineEdit()
    tab2 = QListWidget()
    tab3 = QTreeWidget()
    tab4 = QCalendarWidget()
    tab.insertTab(0, tab1, QIcon("images/mode_Debug.png"), "Debug")
    tab.setCurrentIndex(0)
    tab.insertTab(1, tab2, QIcon("images/mode_Edit.png"), "Edit")
    tab.setTabEnabled(1, False)
    tab.insertTab(2, tab3, QIcon("images/mode_Design.png"), "Design")
    tab.insertTab(3, tab4, QIcon("images/mode_Project.png"), "Project")

    window.setCentralWidget(tab)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test()