import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListView, QListWidgetItem,
                             QFileIconProvider, QStyle, QLineEdit, QPushButton,
                             QListWidget, QLabel, QMenu, QMessageBox)
from PyQt6.QtGui import QFileSystemModel, QColor, QPainter, QBrush, QIcon, QAction, QRegion
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QSize, QDir

class RhinoIconProvider(QFileIconProvider):
    def icon(self, info):
        if info.isDir():
            icon = QIcon.fromTheme("folder-yellow")
            return icon if not icon.isNull() else QIcon.fromTheme("folder")

        ext = info.suffix().lower()
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp']:
            icon_name = "image-x-generic"
        elif ext in ['mp4', 'mkv', 'avi', 'mov', 'flv', 'webm']:
            icon_name = "video-x-generic"
        elif ext in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
            icon_name = "audio-x-generic"
        elif ext in ['py', 'sh', 'js', 'html', 'css', 'cpp', 'c']:
            icon_name = "text-x-script"
        elif ext in ['pdf']:
            icon_name = "document-pdf"
        elif ext in ['zip', 'tar', 'gz', 'rar', '7z']:
            icon_name = "package-x-generic"
        else:
            icon_name = "text-x-generic"

        icon = QIcon.fromTheme(icon_name)
        return icon if not icon.isNull() else QIcon.fromTheme("text-x-generic")

class RhinoExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RHINO")
        self.resize(1200, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.history_back = []
        self.history_forward = []
        self.current_path = os.path.expanduser("~")

        self.setStyleSheet("""
            QWidget#MainContainer { 
                background-color: rgba(13, 2, 33, 200);
                border-radius: 15px;
            }
            QLineEdit, QPushButton {
                background-color: rgba(255, 41, 117, 0.05);
                border: 1px solid #ff2975;
                border-radius: 10px;
                color: #ffffff;
                padding: 8px;
                margin-top: 5px;
                font-family: "JetBrainsMono Nerd Font";
            }
            QPushButton:hover { 
                background-color: rgba(255, 41, 117, 0.3); 
            }
            QListWidget#Sidebar {
                background-color: rgba(0, 0, 0, 0.2);
                border-right: 1px solid rgba(255, 41, 117, 0.2);
                color: #ffffff;
                font-family: "JetBrainsMono Nerd Font";
                outline: none;
                border-top-left-radius: 24px;
            }
            QListWidget::item { 
                padding: 12px; 
                border-radius: 15px; 
                margin: 2px 10px; 
            }
            QListWidget::item:selected { 
                background-color: rgba(0, 243, 255, 0.15); 
                color: #00F3FF; 
            }
            QListView#ContentPane {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-family: "JetBrainsMono Nerd Font";
                outline: none;
            }
            QListView::item {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 41, 117, 0.1);
                border-radius: 15px;
                padding: 10px;
                margin: 5px;
                color: #ffffff;
            }
            QListView::item:hover { 
                background-color: rgba(255, 41, 117, 0.15); 
                border: 1px solid #ff2975; 
            }
            QListView::item:selected { 
                background-color: rgba(0, 243, 255, 0.1); 
                border: 1px solid #00F3FF; 
                color: #00F3FF; 
            }
            #DetailsPane {
                background-color: rgba(0, 0, 0, 0.5);
                border-top: 1px solid rgba(255, 41, 117, 0.3);
                color: #00F3FF;
                font-family: "JetBrainsMono Nerd Font";
                font-size: 11px;
                padding: 10px 20px;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
        """)

        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.setCentralWidget(self.main_container)
        self.main_vbox = QVBoxLayout(self.main_container)
        self.main_vbox.setContentsMargins(0, 0, 0, 0)
        self.main_vbox.setSpacing(10)

        self.top_bar_layout = QHBoxLayout()
        self.btn_back = QPushButton("")
        self.btn_forward = QPushButton("")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)

        self.top_bar_layout.setContentsMargins(20, 15, 20, 5)
        self.top_bar_layout.setSpacing(12)

        self.address_bar = QLineEdit()
        self.address_bar.setText(self.current_path)
        self.address_bar.returnPressed.connect(self.navigate_manual)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("   Search...")
        self.search_box.setFixedWidth(220)

        self.top_bar_layout.addWidget(self.btn_back)
        self.top_bar_layout.addWidget(self.btn_forward)
        self.top_bar_layout.addWidget(self.address_bar)
        self.top_bar_layout.addWidget(self.search_box)
        self.main_vbox.addLayout(self.top_bar_layout)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(20, 0, 20, 0)
        self.content_layout.setSpacing(15)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        self.setup_sidebar()
        self.sidebar.itemClicked.connect(self.on_sidebar_clicked)

        self.model = QFileSystemModel()
        self.model.setIconProvider(RenoIconProvider())
        self.model.setRootPath("/")
        self.model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Hidden)

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.search_box.textChanged.connect(lambda t: self.proxy_model.setFilterFixedString(t))

        self.content_view = QListView()
        self.content_view.setObjectName("ContentPane")
        self.content_view.setModel(self.proxy_model)
        self.content_view.setViewMode(QListView.ViewMode.IconMode)
        self.content_view.setFlow(QListView.Flow.LeftToRight)
        self.content_view.setMovement(QListView.Movement.Snap)
        self.content_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.content_view.setGridSize(QSize(250, 100))
        self.content_view.setIconSize(QSize(64, 64))
        self.content_view.setSpacing(5)
        self.content_view.setWordWrap(True)

        self.content_view.setSelectionRectVisible(True)
        self.content_view.setDragDropMode(QListView.DragDropMode.DragDrop)
        self.content_view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

        self.content_view.doubleClicked.connect(self.on_item_double_clicked)
        self.content_view.selectionModel().selectionChanged.connect(self.update_details)

        self.content_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.content_view.customContextMenuRequested.connect(self.show_context_menu)

        self.content_view.setDragEnabled(True)
        self.content_view.setAcceptDrops(True)
        self.content_view.setDropIndicatorShown(True)
        self.content_view.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.content_view)
        self.main_vbox.addLayout(self.content_layout)

        self.details_pane = QLabel("     RENO Tile Engine Active")
        self.details_pane.setObjectName("DetailsPane")
        self.main_vbox.addWidget(self.details_pane)

        self.update_view(self.current_path, update_history=False)

    def setup_sidebar(self):
        shortcuts = [
            ("   Home", os.path.expanduser("~")),
            ("    Documents", os.path.expanduser("~/Documents")),
            ("    Downloads", os.path.expanduser("~/Downloads")),
            ("    Pictures", os.path.expanduser("~/Pictures")),
            ("    Videos", os.path.expanduser("~/Videos")),
            ("    Root", "/")
        ]
        for name, path in shortcuts:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.sidebar.addItem(item)

    def on_sidebar_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.update_view(path)

    def update_details(self):
        indexes = self.content_view.selectionModel().selectedIndexes()
        if not indexes:
            count = self.proxy_model.rowCount(self.content_view.rootIndex())
            self.details_pane.setText(f"     {count} items in directory")
            return
        source_index = self.proxy_model.mapToSource(indexes[0])
        file_info = self.model.fileInfo(source_index)
        self.details_pane.setText(f"     {file_info.fileName()}   |       Size: {file_info.size() / 1024:.1f} KB")

    def update_view(self, path, update_history=True):
        path = os.path.abspath(os.path.expanduser(path))

        if os.path.isdir(path):
            if update_history and path != self.current_path:
                self.history_back.append(self.current_path)
                self.history_forward.clear()
            
            self.current_path = path
            self.address_bar.setText(path)
            
            source_idx = self.model.index(path)

            proxy_idx = self.proxy_model.mapFromSource(source_idx)

            if proxy_idx.isValid():
                self.content_view.setRootIndex(proxy_idx)
                self.update_details()
            else:
                self.model.fetchMore(source_idx)
                self.content_view.setRootIndex(self.proxy_model.mapFromSource(source_idx))


    def go_back(self):
        if self.history_back:
            self.history_forward.append(self.current_path)
            self.update_view(self.history_back.pop(), update_history=False)

    def go_forward(self):
        if self.history_forward:
            self.history_back.append(self.current_path)
            self.update_view(self.history_forward.pop(), update_history=False)

    def navigate_manual(self):
        self.update_view(self.address_bar.text())
        raw_path = self.address_bar.text().strip()
        full_path = os.path.expanduser(raw_path)
        
        if os.path.isdir(full_path):
            self.update_view(full_path)
        elif os.path.isfile(full_path):
            try:
                subprocess.Popen(['xdg-open', full_path])
            except Exception as e:
                print(f"Error opening file: {e}")
        else:
            self.details_pane.setText(f"     Path not found: {raw_path}")

    def update_mask(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect().toRectF(), 24, 24)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def on_item_double_clicked(self, index):
        source_index = self.proxy_model.mapToSource(index)
        path = self.model.filePath(source_index)
        
        if os.path.isdir(path):
            self.update_view(path)
        elif os.path.isfile(path):
            try:
                subprocess.Popen(['xdg-open', path]) 
            except Exception as e:
                print(f"Error opening file: {e}")

    def show_properties(self, index):
        source_index = self.proxy_model.mapToSource(index)
        file_info = self.model.fileInfo(source_index)
        
        name = file_info.fileName()
        path = file_info.absoluteFilePath()
        size = f"{file_info.size() / 1024:.2f} KB" if not file_info.isDir() else "Folder"
        created = file_info.birthTime().toString("yyyy-MM-dd HH:mm")
        modified = file_info.lastModified().toString("yyyy-MM-dd HH:mm")
        owner = file_info.owner()
        
        details = (
            f"<b>Name:</b> {name}<br>"
            f"<b>Path:</b> {path}<br><br>"
            f"<b>Size:</b> {size}<br>"
            f"<b>Owner:</b> {owner}<br>"
            f"<b>Created:</b> {created}<br>"
            f"<b>Modified:</b> {modified}"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Item Properties")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(details)
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0D0221;
                border: 1px solid #00F3FF;
            }
            QLabel {
                color: #ffffff;
                font-family: 'JetBrainsMono Nerd Font';
            }
            QPushButton {
                background-color: #ff2975;
                color: white;
                border-radius: 15px;
                padding: 5px 15px;
            }
        """)
        msg.exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 204)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 24, 24)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def show_context_menu(self, position):
        menu = QMenu(self)
        
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(13, 2, 33, 240);
                border: 1px solid #ff2975;
                color: #ffffff;
                font-family: "JetBrainsMono Nerd Font";
            }
            QMenu::item:selected {
                background-color: rgba(255, 41, 117, 0.3);
                color: #ff2975;
            }
        """)

        index = self.content_view.indexAt(position)
        
        if index.isValid():
            open_act = QAction("     Open", self)
            copy_act = QAction("     Copy", self)
            rename_act = QAction("     Rename", self)
            delete_act = QAction("     Delete", self)
            prop_act = QAction("     Properties", self)

            open_act.triggered.connect(lambda: self.on_item_double_clicked(index))
            prop_act.triggered.connect(lambda: self.show_properties(index))

            menu.addAction(open_act)
            menu.addSeparator()
            menu.addAction(copy_act)
            menu.addAction(rename_act)
            menu.addAction(delete_act)
            menu.addAction(prop_act)
        else:
            paste_act = QAction("     Paste", self)
            new_folder_act = QAction("     New Folder", self)
            menu.addAction(paste_act)
            menu.addAction(new_folder_act)

        menu.exec(self.content_view.mapToGlobal(position))


if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"] = "wayland"
    os.environ["XDG_CURRENT_DESKTOP"] = "KDE"
    app = QApplication(sys.argv)
    QIcon.setThemeName("Papirus-Dark")
    window = RenoExplorer()
    window.show()
    sys.exit(app.exec())
