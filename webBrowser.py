"""
This program is to be a web browser and a search engine to handle http operations

"""
import sys
import urllib.parse
import os

from PyQt5.QtCore import QUrl, Qt, QStringListModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QHBoxLayout, QTextEdit, QPushButton, \
    QCompleter

# The local server url
server_url = "http://127.0.0.1:8080"

class webBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLACKPEARL")
        self.showMaximized()
        self.directory = localDirectory
        self.browserUI()


    def browserUI(self):
        layout = QVBoxLayout()

        # navigation and search bar layout
        topBar = QHBoxLayout()

        # Back buttons
        backButton = QPushButton("<")
        backButton.setToolTip("Click to go back")
        backButton.setFixedSize(20, 20)
        topBar.addWidget(backButton)

        # Forward button
        forwardButton = QPushButton(">")
        forwardButton.setToolTip("Click to go forward")
        forwardButton.setFixedSize(20,20)
        topBar.addWidget(forwardButton)

        # Reload button
        self.reloadButton = QPushButton()
        self.reloadIcon = QIcon("assets/reload_icon.svg")
        self.reloadButton.setIcon(self.reloadIcon)
        self.reloadButton.setToolTip("Reload page")
        self.reloadButton.setFixedSize(20, 20)
        topBar.addWidget(self.reloadButton)

        # URL or Search query input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Search or Type a URL")
        searchIcon = QIcon("assets/search_icon.svg")
        self.url_input.addAction(searchIcon, QLineEdit.LeadingPosition)
        self.url_input.returnPressed.connect(self.defaultConfig)

        # A local file dropdown menu
        self.dropDown = QCompleter()
        self.dropDown.setCaseSensitivity(False)
        self.url_input.setCompleter(self.dropDown)
        self.dropDown.setFilterMode(Qt.MatchContains)

        self.model = QStringListModel()
        self.dropDown.setModel(self.model)

        self.url_input.textChanged.connect(self.updateDropDown)

        topBar.addWidget(self.url_input)

        layout.addLayout(topBar)

        # Sets webview, back, forward, reload and cancel buttons
        # Calls pageLoadStart & pageLoadEnd when a page begins and finishes loading respectively
        self.responseWindow = QWebEngineView()
        self.responseWindow.urlChanged.connect(self.updateUrlBar)
        backButton.clicked.connect(self.responseWindow.back)
        forwardButton.clicked.connect(self.responseWindow.forward)
        self.reloadButton.clicked.connect(self.responseWindow.reload)
        self.responseWindow.loadStarted.connect(self.pageLoadStart)
        self.responseWindow.loadFinished.connect(self.pageLoadEnd)
        layout.addWidget(self.responseWindow)


        self.setLayout(layout)

        # Traversing through the local directories
        self.allFiles = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                fullPath = os.path.relpath(os.path.join(root, file), self.directory)
                self.allFiles.append(fullPath)

    # Page Reload and Cancel button transitions
    def pageLoadStart(self):
        cancelIcon = QIcon("assets/cancel_icon.svg")
        self.reloadButton.setIcon(cancelIcon)
        self.reloadButton.setToolTip("Stop loading")
        self.reloadButton.clicked.disconnect()
        self.reloadButton.clicked.connect(self.responseWindow.stop)

    def pageLoadEnd(self):
        self.reloadButton.setIcon(self.reloadIcon)
        self.reloadButton.setToolTip("Reload page")
        self.reloadButton.clicked.disconnect()
        self.reloadButton.clicked.connect(self.responseWindow.reload)


    def updateDropDown(self, text):
        if not text:
            self.model.setStringList([])
            return
        filtered = [
            f for f in self.allFiles
            if text.lower() in os.path.basename(f).lower()
        ]
        self.model.setStringList(filtered)

    # Updating the search bar url
    def updateUrlBar(self, url):
        self.url_input.setText(url.toString())

    # handles the default configurations if the query  not found locally
    def  defaultConfig(self):
        query = self.url_input.text().strip()
        localDoc = f"{server_url}/{query}"

        # if the query is not found locally
        def defaultPageLoad(status):
            if not status:
                htmlDefault = f"""
                <html> 
                <head><title> 404 Not Found</title></head>
                <body>
                    <h1>Document '{query}' not found locally.</h1>
                    <p>Try searching with other search engines:</p>
                    <a href="https://www.google.com/search?q={urllib.parse.quote(query)}">Search on Google</a><br>
                    <a href="https://www.bing.com/search?q={urllib.parse.quote(query)}">Search on Microsoft Bing</a><br>
                    <a href="https://www.DuckDuckGo.com/search?q={urllib.parse.quote(query)}">Search on DuckDuckGo</a>
                </body>
                </html>
                """
                self.responseWindow.setHtml(htmlDefault, QUrl("http://localhost"))

        self.responseWindow.loadFinished.connect(defaultPageLoad)
        self.responseWindow.load(QUrl(localDoc))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    localDirectory = os.path.dirname(os.path.abspath(__file__))

    window = webBrowser()
    window.show()

    sys.exit(app.exec_())