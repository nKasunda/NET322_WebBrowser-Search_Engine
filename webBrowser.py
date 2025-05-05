"""
This program is to be a web browser and a search engine to handle http operations

"""
import sys
import urllib.parse

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QHBoxLayout, QTextEdit, QPushButton

server_url = "http://127.0.0.1:8080"

class webBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLACKPEARL")
        self.showMaximized()
        self.browserUI()

    def browserUI(self):
        layout = QVBoxLayout()

        # Top bar layout (Back button + URL input)
        topBar = QHBoxLayout()

        # Back button
        backButton = QPushButton("←")
        backButton.setToolTip("Click to go back")
        topBar.addWidget(backButton)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Type a URL")
        searchIcon = QIcon("assets/search_icon.svg")
        self.url_input.addAction(searchIcon, QLineEdit.LeadingPosition)
        self.url_input.returnPressed.connect(self.defaultConfig)
        topBar.addWidget(self.url_input)

        layout.addLayout(topBar)

        self.responseWindow = QWebEngineView()
        backButton.clicked.connect(self.responseWindow.back)
        layout.addWidget(self.responseWindow)


        self.setLayout(layout)
    # handles the default configurations of looking for the query locally initially
    def  defaultConfig(self):
        query = self.url_input.text().strip()
        localDoc = f"{server_url}/templates/{query}.html"

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

    window = webBrowser()
    window.show()

    sys.exit(app.exec_())