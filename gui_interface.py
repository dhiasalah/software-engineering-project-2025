"""
PyQt5 GUI Interface for Bit Packing Compression
Author: [Your Name]

This module provides a graphical user interface for testing and using
the bit packing compression algorithms interactively.
"""

import sys
import traceback
import time
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QSpinBox, QGroupBox, QProgressBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QSplitter, QMessageBox, QFileDialog, QCheckBox,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon, QLinearGradient, QPainter

from factory import BitPackingFactory, CompressionType
from benchmark import BenchmarkSuite, DataGenerator, run_default_benchmarks


class ModernStyleSheet:
    """Modern CSS styles for the application"""

    @staticmethod
    def get_style():
        return """
        /* Main Window Style */
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #2c3e50, stop: 1 #34495e);
            color: #ecf0f1;
        }
        
        /* Tab Widget Styling */
        QTabWidget::pane {
            border: 2px solid #3498db;
            border-radius: 10px;
            background-color: #34495e;
            margin-top: -1px;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #5d6d7e, stop: 1 #34495e);
            border: 2px solid #2c3e50;
            border-bottom-color: #3498db;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 120px;
            padding: 8px 16px;
            margin-right: 2px;
            color: #ecf0f1;
            font-weight: bold;
            font-size: 11px;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            border-bottom-color: #3498db;
            color: white;
        }
        
        QTabBar::tab:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #52a3db, stop: 1 #3498db);
        }
        
        /* Group Box Styling */
        QGroupBox {
            font-weight: bold;
            font-size: 12px;
            border: 2px solid #3498db;
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #455a64, stop: 1 #37474f);
            color: #ecf0f1;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 5px 10px 5px 10px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            border-radius: 5px;
            color: white;
        }
        
        /* Button Styling */
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            font-size: 11px;
            padding: 10px 20px;
            min-width: 100px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #52a3db, stop: 1 #3498db);
            transform: translateY(-2px);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #2980b9, stop: 1 #21618c);
        }
        
        QPushButton:disabled {
            background: #7f8c8d;
            color: #bdc3c7;
        }
        
        /* Special button colors */
        QPushButton[objectName="generateBtn"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #27ae60, stop: 1 #229954);
        }
        
        QPushButton[objectName="generateBtn"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #2ecc71, stop: 1 #27ae60);
        }
        
        QPushButton[objectName="benchmarkBtn"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #e67e22, stop: 1 #d35400);
        }
        
        QPushButton[objectName="benchmarkBtn"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #f39c12, stop: 1 #e67e22);
        }
        
        QPushButton[objectName="clearBtn"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #e74c3c, stop: 1 #c0392b);
        }
        
        QPushButton[objectName="clearBtn"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #ec7063, stop: 1 #e74c3c);
        }
        
        /* Input Field Styling */
        QLineEdit, QTextEdit {
            background-color: #2c3e50;
            border: 2px solid #34495e;
            border-radius: 8px;
            padding: 8px 12px;
            color: #ecf0f1;
            font-size: 11px;
            selection-background-color: #3498db;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border-color: #3498db;
            background-color: #34495e;
        }
        
        /* ComboBox Styling */
        QComboBox {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #34495e, stop: 1 #2c3e50);
            border: 2px solid #34495e;
            border-radius: 8px;
            padding: 8px 12px;
            color: #ecf0f1;
            font-size: 11px;
            min-width: 150px;
        }
        
        QComboBox:hover {
            border-color: #3498db;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ecf0f1;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #34495e;
            border: 2px solid #3498db;
            border-radius: 8px;
            color: #ecf0f1;
            selection-background-color: #3498db;
        }
        
        /* SpinBox Styling */
        QSpinBox {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #34495e, stop: 1 #2c3e50);
            border: 2px solid #34495e;
            border-radius: 8px;
            padding: 8px 12px;
            color: #ecf0f1;
            font-size: 11px;
        }
        
        QSpinBox:focus {
            border-color: #3498db;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            border: none;
            border-radius: 4px;
            width: 20px;
        }
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: #52a3db;
        }
        
        /* Table Styling */
        QTableWidget {
            background-color: #2c3e50;
            alternate-background-color: #34495e;
            border: 2px solid #3498db;
            border-radius: 10px;
            gridline-color: #34495e;
            color: #ecf0f1;
            font-size: 11px;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #34495e;
        }
        
        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        QHeaderView::section {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            color: white;
            padding: 10px;
            border: none;
            font-weight: bold;
            font-size: 11px;
        }
        
        /* Progress Bar Styling */
        QProgressBar {
            border: 2px solid #34495e;
            border-radius: 8px;
            background-color: #2c3e50;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                       stop: 0 #3498db, stop: 1 #2980b9);
            border-radius: 6px;
        }
        
        /* Label Styling */
        QLabel {
            color: #ecf0f1;
            font-size: 11px;
        }
        
        QLabel[objectName="titleLabel"] {
            font-size: 16px;
            font-weight: bold;
            color: #3498db;
            padding: 10px;
        }
        
        QLabel[objectName="infoLabel"] {
            color: #3498db;
            font-weight: bold;
        }
        
        QLabel[objectName="successLabel"] {
            color: #27ae60;
            font-weight: bold;
        }
        
        QLabel[objectName="errorLabel"] {
            color: #e74c3c;
            font-weight: bold;
        }
        
        /* Status Bar Styling */
        QStatusBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                       stop: 0 #34495e, stop: 1 #2c3e50);
            border-top: 2px solid #3498db;
            color: #ecf0f1;
            font-weight: bold;
        }
        
        /* Splitter Styling */
        QSplitter::handle {
            background: #3498db;
            width: 4px;
            border-radius: 2px;
        }
        
        QSplitter::handle:hover {
            background: #52a3db;
        }
        
        /* Scroll Bar Styling */
        QScrollBar:vertical {
            background: #34495e;
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background: #3498db;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #52a3db;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        
        /* Message Box Styling */
        QMessageBox {
            background-color: #34495e;
            color: #ecf0f1;
        }
        
        QMessageBox QPushButton {
            min-width: 80px;
            padding: 8px 16px;
        }
        """


class CompressionWorker(QThread):
    """Worker thread for compression operations to avoid UI freezing"""

    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, operation, data, algorithm='simple', **kwargs):
        super().__init__()
        self.operation = operation
        self.data = data
        self.algorithm = algorithm
        self.kwargs = kwargs

    def run(self):
        try:
            if self.operation == 'compress':
                self.compress_data()
            elif self.operation == 'benchmark':
                self.run_benchmark()
            elif self.operation == 'generate':
                self.generate_data()
        except Exception as e:
            self.error.emit(str(e))

    def compress_data(self):
        """Perform compression operation"""
        self.progress.emit("Creating compressor...")
        compressor = BitPackingFactory.create_compressor(self.algorithm)

        self.progress.emit("Compressing data...")
        start_time = time.perf_counter()
        compressed = compressor.compress(self.data.copy())
        compression_time = time.perf_counter() - start_time

        self.progress.emit("Decompressing data...")
        start_time = time.perf_counter()
        decompressed = compressor.decompress(compressed.copy())
        decompression_time = time.perf_counter() - start_time

        self.progress.emit("Testing random access...")
        access_times = []
        for access_index in range(min(10, len(self.data))):
            start_time = time.perf_counter()
            value = compressor.get(access_index)
            access_time = time.perf_counter() - start_time
            access_times.append(access_time)

        # Calculate statistics
        original_size = len(self.data) * 32
        compressed_size = len(compressed) * 32
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

        result = {
            'original_data': self.data,
            'compressed_data': compressed,
            'decompressed_data': decompressed,
            'compression_time': compression_time,
            'decompression_time': decompression_time,
            'average_access_time': sum(access_times) / len(access_times) if access_times else 0,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'integrity_check': decompressed == self.data,
            'algorithm': self.algorithm
        }

        self.finished.emit(result)

    def run_benchmark(self):
        """Run benchmark on data"""
        self.progress.emit("Running benchmarks...")

        results = {}
        for algorithm_index, comp_type in enumerate(CompressionType):
            self.progress.emit(f"Testing {comp_type.value} algorithm...")

            benchmark_suite = BenchmarkSuite(num_iterations=10)
            algorithm = BitPackingFactory.create_compressor(comp_type)
            result = benchmark_suite.benchmark_algorithm(algorithm, self.data, comp_type.value)

            results[comp_type.value] = {
                'compression_ratio': result.compression_ratio,
                'compression_time': result.compression_time * 1000,  # Convert to ms
                'decompression_time': result.decompression_time * 1000,
                'access_time': result.get_time * 1000000,  # Convert to μs
                'original_size': result.original_size_bits,
                'compressed_size': result.compressed_size_bits
            }

        self.finished.emit({'benchmark_results': results})

    def generate_data(self):
        """Generate test data"""
        size = self.kwargs.get('size', 1000)
        data_type = self.kwargs.get('data_type', 'uniform')
        max_value = self.kwargs.get('max_value', 1000)

        self.progress.emit(f"Generating {data_type} data...")

        if data_type == 'uniform':
            data = DataGenerator.generate_uniform(size, max_value)
        elif data_type == 'power_law':
            data = DataGenerator.generate_power_law(size, max_value)
        elif data_type == 'with_outliers':
            outlier_value = self.kwargs.get('outlier_value', max_value * 100)
            data = DataGenerator.generate_with_outliers(size, max_value, outlier_value)
        elif data_type == 'sequential':
            start = self.kwargs.get('start', 0)
            data = DataGenerator.generate_sequential(size, start)
        else:
            data = DataGenerator.generate_uniform(size, max_value)

        result = {
            'generated_data': data,
            'size': len(data),
            'data_type': data_type,
            'min_value': min(data) if data else 0,
            'max_value': max(data) if data else 0
        }

        self.finished.emit(result)


class CompressionGUI(QMainWindow):
    """Main GUI application for bit packing compression"""

    def __init__(self):
        super().__init__()
        self.current_data = []
        self.compression_results = {}
        self.init_ui()
        self.apply_animations()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🔧 Bit Packing Compression - Interactive GUI")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # Apply modern stylesheet
        self.setStyleSheet(ModernStyleSheet.get_style())

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with title
        main_layout = QVBoxLayout(central_widget)

        # Add title header
        self.create_title_header(main_layout)

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.North)
        main_layout.addWidget(tab_widget)

        # Create tabs with icons
        self.create_data_input_tab(tab_widget)
        self.create_compression_tab(tab_widget)
        self.create_benchmark_tab(tab_widget)
        self.create_results_tab(tab_widget)

        # Status bar
        self.statusBar().showMessage("🚀 Ready to compress your data!")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.show()

    def create_title_header(self, layout):
        """Create a beautiful title header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(120)  # Increased from 90 to 120
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 15px;
                margin: 5px;
                border: 3px solid #2980b9;
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)  # Increased vertical margins

        # Title with bigger font size
        title_label = QLabel("🔧 Bit Packing Compression Studio")
        title_label.setAlignment(Qt.AlignCenter)

        # Set font programmatically with larger size
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(28)    # Increased from 18 to 28 for much bigger text
        font.setBold(True)
        title_label.setFont(font)

        # Remove ALL CSS styling that might interfere
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                border: none;
            }
        """)

        # Force the text to be visible by setting it multiple ways
        title_label.setText("🔧 Bit Packing Compression Studio")
        title_label.setVisible(True)
        title_label.show()

        header_layout.addWidget(title_label)
        layout.addWidget(header_frame)

    def apply_animations(self):
        """Apply subtle animations to enhance user experience"""
        # This could be expanded with more sophisticated animations
        pass

    def create_data_input_tab(self, parent):
        """Create data input and generation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Manual data input section
        input_group = QGroupBox("📝 Manual Data Input")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        # Add info label
        info_label = QLabel("💡 Enter positive integers separated by spaces")
        info_label.setObjectName("infoLabel")
        input_layout.addWidget(info_label)

        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Example: 1 2 3 4 5 1024 6 7 8")
        self.data_input.setFixedHeight(40)
        input_layout.addWidget(QLabel("Data Array:"))
        input_layout.addWidget(self.data_input)

        input_buttons_layout = QHBoxLayout()
        input_buttons_layout.setSpacing(10)

        load_data_btn = QPushButton("📁 Load Data")
        load_data_btn.clicked.connect(self.load_manual_data)
        load_data_btn.setFixedHeight(45)

        load_file_btn = QPushButton("📂 Load from File")
        load_file_btn.clicked.connect(self.load_data_from_file)
        load_file_btn.setFixedHeight(45)

        input_buttons_layout.addWidget(load_data_btn)
        input_buttons_layout.addWidget(load_file_btn)
        input_buttons_layout.addStretch()
        input_layout.addLayout(input_buttons_layout)

        # Data generation section
        generation_group = QGroupBox("🎲 Data Generation")
        generation_layout = QGridLayout(generation_group)
        generation_layout.setSpacing(10)

        # Style labels
        for i, label_text in enumerate(["📊 Size:", "📈 Type:", "🎯 Max Value:", "⚡ Outlier Value:"]):
            label = QLabel(label_text)
            generation_layout.addWidget(label, i, 0)

        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(1, 100000)
        self.size_spinbox.setValue(1000)
        self.size_spinbox.setFixedHeight(35)
        generation_layout.addWidget(self.size_spinbox, 0, 1)

        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(['uniform', 'power_law', 'with_outliers', 'sequential'])
        self.data_type_combo.setFixedHeight(35)
        generation_layout.addWidget(self.data_type_combo, 1, 1)

        self.max_value_spinbox = QSpinBox()
        self.max_value_spinbox.setRange(1, 1000000)
        self.max_value_spinbox.setValue(1000)
        self.max_value_spinbox.setFixedHeight(35)
        generation_layout.addWidget(self.max_value_spinbox, 2, 1)

        self.outlier_value_spinbox = QSpinBox()
        self.outlier_value_spinbox.setRange(1, 10000000)
        self.outlier_value_spinbox.setValue(100000)
        self.outlier_value_spinbox.setFixedHeight(35)
        generation_layout.addWidget(self.outlier_value_spinbox, 3, 1)

        generate_btn = QPushButton("🎲 Generate Data")
        generate_btn.setObjectName("generateBtn")
        generate_btn.clicked.connect(self.generate_data)
        generate_btn.setFixedHeight(45)
        generation_layout.addWidget(generate_btn, 4, 0, 1, 2)

        # Current data display
        current_data_group = QGroupBox("📋 Current Data")
        current_data_layout = QVBoxLayout(current_data_group)

        self.data_info_label = QLabel("ℹ️ No data loaded")
        self.data_info_label.setObjectName("infoLabel")
        current_data_layout.addWidget(self.data_info_label)

        self.data_preview = QTextEdit()
        self.data_preview.setMaximumHeight(120)
        self.data_preview.setReadOnly(True)
        current_data_layout.addWidget(self.data_preview)

        # Add all groups to tab
        layout.addWidget(input_group)
        layout.addWidget(generation_group)
        layout.addWidget(current_data_group)
        layout.addStretch()

        parent.addTab(tab, "📝 Data Input")

    def create_compression_tab(self, parent):
        """Create compression testing tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(15)

        # Left side - Controls
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(450)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)

        # Algorithm selection
        algorithm_group = QGroupBox("⚙️ Compression Algorithm")
        algorithm_layout = QVBoxLayout(algorithm_group)
        algorithm_layout.setSpacing(10)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setFixedHeight(40)
        for comp_type in CompressionType:
            self.algorithm_combo.addItem(f"🔧 {comp_type.value.capitalize()}", comp_type.value)
        algorithm_layout.addWidget(self.algorithm_combo)

        # Algorithm description
        self.algorithm_description = QTextEdit()
        self.algorithm_description.setMaximumHeight(100)
        self.algorithm_description.setReadOnly(True)
        algorithm_layout.addWidget(self.algorithm_description)

        # Update description when algorithm changes
        self.algorithm_combo.currentTextChanged.connect(self.update_algorithm_description)
        self.update_algorithm_description()

        # Compression controls
        compress_btn = QPushButton("🚀 Compress Data")
        compress_btn.clicked.connect(self.compress_data)
        compress_btn.setFixedHeight(50)
        algorithm_layout.addWidget(compress_btn)

        controls_layout.addWidget(algorithm_group)

        # Random access test
        access_group = QGroupBox("🎯 Random Access Test")
        access_layout = QVBoxLayout(access_group)

        access_input_layout = QHBoxLayout()
        access_input_layout.addWidget(QLabel("📍 Index:"))
        self.access_index_spinbox = QSpinBox()
        self.access_index_spinbox.setMinimum(0)
        self.access_index_spinbox.setFixedHeight(35)
        access_input_layout.addWidget(self.access_index_spinbox)

        access_btn = QPushButton("🔍 Get Value")
        access_btn.clicked.connect(self.test_random_access)
        access_btn.setFixedHeight(35)
        access_input_layout.addWidget(access_btn)

        access_layout.addLayout(access_input_layout)

        self.access_result_label = QLabel("⏳ No access test performed")
        access_layout.addWidget(self.access_result_label)

        controls_layout.addWidget(access_group)
        controls_layout.addStretch()

        # Right side - Results
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        # Compression statistics
        stats_group = QGroupBox("📊 Compression Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMinimumHeight(300)
        stats_layout.addWidget(self.stats_text)

        results_layout.addWidget(stats_group)

        # Add widgets to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(controls_widget)
        splitter.addWidget(results_widget)
        splitter.setSizes([450, 950])

        layout.addWidget(splitter)
        parent.addTab(tab, "🔧 Compression")

    def create_benchmark_tab(self, parent):
        """Create benchmarking tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Benchmark controls
        controls_group = QGroupBox("🏁 Benchmark Controls")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(15)

        run_benchmark_btn = QPushButton("🏃 Run Benchmark")
        run_benchmark_btn.setObjectName("benchmarkBtn")
        run_benchmark_btn.clicked.connect(self.run_benchmark)
        run_benchmark_btn.setFixedHeight(50)
        controls_layout.addWidget(run_benchmark_btn)

        # Run default benchmarks
        run_default_btn = QPushButton("🎯 Run Default Benchmarks")
        run_default_btn.setObjectName("benchmarkBtn")
        run_default_btn.clicked.connect(self.run_default_benchmarks)
        run_default_btn.setFixedHeight(50)
        controls_layout.addWidget(run_default_btn)

        controls_layout.addStretch()

        # Benchmark results table
        results_group = QGroupBox("📈 Benchmark Results")
        results_layout = QVBoxLayout(results_group)

        self.benchmark_table = QTableWidget()
        self.benchmark_table.setColumnCount(6)
        self.benchmark_table.setHorizontalHeaderLabels([
            '🔧 Algorithm', '📊 Compression Ratio', '⏱️ Compression Time (ms)',
            '⏱️ Decompression Time (ms)', '🎯 Access Time (μs)', '💾 Compressed Size (bytes)'
        ])
        self.benchmark_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.benchmark_table)

        layout.addWidget(controls_group)
        layout.addWidget(results_group)

        parent.addTab(tab, "🏁 Benchmark")

    def create_results_tab(self, parent):
        """Create results visualization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Results display
        results_group = QGroupBox("📋 Results History")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

        # Export options
        export_group = QGroupBox("💾 Export Options")
        export_layout = QHBoxLayout(export_group)
        export_layout.setSpacing(15)

        save_results_btn = QPushButton("💾 Save Results")
        save_results_btn.clicked.connect(self.save_results)
        save_results_btn.setFixedHeight(45)
        export_layout.addWidget(save_results_btn)

        clear_results_btn = QPushButton("🗑️ Clear Results")
        clear_results_btn.setObjectName("clearBtn")
        clear_results_btn.clicked.connect(self.clear_results)
        clear_results_btn.setFixedHeight(45)
        export_layout.addWidget(clear_results_btn)

        export_layout.addStretch()

        layout.addWidget(export_group)
        parent.addTab(tab, "📋 Results")

    def load_manual_data(self):
        """Load data from manual input"""
        try:
            text = self.data_input.text().strip()
            if not text:
                QMessageBox.warning(self, "Warning", "Please enter some data")
                return

            data = [int(x) for x in text.split()]
            if not data:
                QMessageBox.warning(self, "Warning", "No valid integers found")
                return

            if any(x < 0 for x in data):
                QMessageBox.warning(self, "Warning", "Negative numbers are not supported")
                return

            self.current_data = data
            self.update_data_display()
            self.statusBar().showMessage(f"Loaded {len(data)} integers from manual input")

        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid input. Please enter integers separated by spaces.")

    def load_data_from_file(self):
        """Load data from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                content = file.read().strip()
                data = [int(x) for x in content.split()]

                if any(x < 0 for x in data):
                    QMessageBox.warning(self, "Warning", "Negative numbers are not supported")
                    return

                self.current_data = data
                self.update_data_display()
                self.statusBar().showMessage(f"Loaded {len(data)} integers from file")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def generate_data(self):
        """Generate test data"""
        if not hasattr(self, 'generation_worker') or not self.generation_worker.isRunning():
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress

            size = self.size_spinbox.value()
            data_type = self.data_type_combo.currentText()
            max_value = self.max_value_spinbox.value()
            outlier_value = self.outlier_value_spinbox.value()

            self.generation_worker = CompressionWorker(
                'generate', [], size=size, data_type=data_type,
                max_value=max_value, outlier_value=outlier_value
            )
            self.generation_worker.finished.connect(self.on_generation_finished)
            self.generation_worker.progress.connect(self.update_status)
            self.generation_worker.error.connect(self.on_error)
            self.generation_worker.start()

    def update_data_display(self):
        """Update the data display widgets"""
        if not self.current_data:
            self.data_info_label.setText("ℹ️ No data loaded")
            self.data_preview.setText("")
            self.access_index_spinbox.setMaximum(0)
            return

        # Update info label
        info_text = f"✅ Data loaded: {len(self.current_data)} integers, "
        info_text += f"Range: {min(self.current_data)} - {max(self.current_data)}"
        self.data_info_label.setText(info_text)
        self.data_info_label.setObjectName("successLabel")

        # Update preview
        preview_data = self.current_data[:20]
        preview_text = " ".join(map(str, preview_data))
        if len(self.current_data) > 20:
            preview_text += "..."
        self.data_preview.setText(preview_text)

        # Update access index range
        self.access_index_spinbox.setMaximum(len(self.current_data) - 1)

    def update_algorithm_description(self):
        """Update algorithm description"""
        algorithm = self.algorithm_combo.currentData()
        description = BitPackingFactory.get_description(algorithm)
        self.algorithm_description.setText(description)

    def compress_data(self):
        """Compress current data"""
        if not self.current_data:
            QMessageBox.warning(self, "Warning", "Please load some data first")
            return

        if not hasattr(self, 'compression_worker') or not self.compression_worker.isRunning():
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            algorithm = self.algorithm_combo.currentData()

            self.compression_worker = CompressionWorker(
                'compress', self.current_data, algorithm
            )
            self.compression_worker.finished.connect(self.on_compression_finished)
            self.compression_worker.progress.connect(self.update_status)
            self.compression_worker.error.connect(self.on_error)
            self.compression_worker.start()

    def test_random_access(self):
        """Test random access to compressed data"""
        if not self.compression_results:
            QMessageBox.warning(self, "Warning", "Please compress data first")
            return

        try:
            index = self.access_index_spinbox.value()
            algorithm = self.algorithm_combo.currentData()

            # Create compressor and compress data again (for access test)
            compressor = BitPackingFactory.create_compressor(algorithm)
            compressor.compress(self.current_data.copy())

            start_time = time.perf_counter()
            value = compressor.get(index)
            access_time = time.perf_counter() - start_time

            expected_value = self.current_data[index]
            status = "✓ PASS" if value == expected_value else "✗ FAIL"

            result_text = f"Index {index}: Got {value}, Expected {expected_value} {status}\n"
            result_text += f"Access time: {access_time * 1000000:.2f} μs"

            self.access_result_label.setText(result_text)

        except Exception as e:
            self.access_result_label.setText(f"Error: {str(e)}")

    def run_benchmark(self):
        """Run benchmark on current data"""
        if not self.current_data:
            QMessageBox.warning(self, "Warning", "Please load some data first")
            return

        if not hasattr(self, 'benchmark_worker') or not self.benchmark_worker.isRunning():
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)

            self.benchmark_worker = CompressionWorker(
                'benchmark', self.current_data
            )
            self.benchmark_worker.finished.connect(self.on_benchmark_finished)
            self.benchmark_worker.progress.connect(self.update_status)
            self.benchmark_worker.error.connect(self.on_error)
            self.benchmark_worker.start()

    def run_default_benchmarks(self):
        """Run default benchmarks with preset datasets"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.update_status("Running default benchmarks...")

        try:
            # This might take a while, so we run it in a separate thread
            results = run_default_benchmarks()

            # Display results in the results tab
            from benchmark import BenchmarkSuite
            benchmark_suite = BenchmarkSuite()
            report = benchmark_suite.generate_report(results)

            self.results_text.append("=== DEFAULT BENCHMARKS RESULTS ===\n")
            self.results_text.append(report)

            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Default benchmarks completed")

        except Exception as e:
            self.on_error(str(e))

    def update_status(self, message):
        """Update status bar message"""
        self.statusBar().showMessage(message)

    def on_compression_finished(self, result):
        """Handle compression completion"""
        self.progress_bar.setVisible(False)
        self.compression_results = result

        # Update statistics display with emojis and better formatting
        stats_text = f"🔧 Algorithm: {result['algorithm'].upper()}\n\n"
        stats_text += f"📦 Original size: {result['original_size']:,} bits ({result['original_size'] // 8:,} bytes)\n"
        stats_text += f"🗜️ Compressed size: {result['compressed_size']:,} bits ({result['compressed_size'] // 8:,} bytes)\n"
        stats_text += f"📊 Compression ratio: {result['compression_ratio']:.3f}x\n"
        stats_text += f"💾 Space saved: {result['original_size'] - result['compressed_size']:,} bits\n\n"
        stats_text += f"⏱️ Compression time: {result['compression_time'] * 1000:.3f} ms\n"
        stats_text += f"⏱️ Decompression time: {result['decompression_time'] * 1000:.3f} ms\n"
        stats_text += f"🎯 Average access time: {result['average_access_time'] * 1000000:.3f} μs\n\n"
        if result['integrity_check']:
            stats_text += f"✅ Integrity check: PASS\n"
        else:
            stats_text += f"❌ Integrity check: FAIL\n"

        self.stats_text.setText(stats_text)

        # Add to results log
        self.results_text.append(f"\n🚀 === COMPRESSION RESULT ({time.strftime('%H:%M:%S')}) ===\n")
        self.results_text.append(stats_text)

        self.statusBar().showMessage("✅ Compression completed successfully!")

    def on_benchmark_finished(self, result):
        """Handle benchmark completion"""
        self.progress_bar.setVisible(False)

        if 'benchmark_results' in result:
            self.update_benchmark_table(result['benchmark_results'])

            # Add to results log
            self.results_text.append(f"\n=== BENCHMARK RESULT ({time.strftime('%H:%M:%S')}) ===\n")
            for algo, metrics in result['benchmark_results'].items():
                self.results_text.append(f"{algo.upper()}:\n")
                self.results_text.append(f"  Compression ratio: {metrics['compression_ratio']:.3f}x\n")
                self.results_text.append(f"  Compression time: {metrics['compression_time']:.3f} ms\n")
                self.results_text.append(f"  Decompression time: {metrics['decompression_time']:.3f} ms\n")
                self.results_text.append(f"  Access time: {metrics['access_time']:.3f} μs\n")

        self.statusBar().showMessage("Benchmark completed successfully")

    def on_generation_finished(self, result):
        """Handle data generation completion"""
        self.progress_bar.setVisible(False)

        if 'generated_data' in result:
            self.current_data = result['generated_data']
            self.update_data_display()

            info_text = f"Generated {result['size']} {result['data_type']} integers\n"
            info_text += f"Range: {result['min_value']} - {result['max_value']}"

            self.statusBar().showMessage(f"Generated {result['size']} integers successfully")

    def on_error(self, error_message):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Operation failed: {error_message}")
        self.statusBar().showMessage("Operation failed")

    def update_benchmark_table(self, results):
        """Update benchmark results table"""
        self.benchmark_table.setRowCount(len(results))

        for row, (algorithm, metrics) in enumerate(results.items()):
            self.benchmark_table.setItem(row, 0, QTableWidgetItem(algorithm.upper()))
            self.benchmark_table.setItem(row, 1, QTableWidgetItem(f"{metrics['compression_ratio']:.3f}x"))
            self.benchmark_table.setItem(row, 2, QTableWidgetItem(f"{metrics['compression_time']:.3f}"))
            self.benchmark_table.setItem(row, 3, QTableWidgetItem(f"{metrics['decompression_time']:.3f}"))
            self.benchmark_table.setItem(row, 4, QTableWidgetItem(f"{metrics['access_time']:.3f}"))
            self.benchmark_table.setItem(row, 5, QTableWidgetItem(f"{metrics['compressed_size'] // 8}"))

        self.benchmark_table.resizeColumnsToContents()

    def save_results(self):
        """Save results to file"""
        if not self.results_text.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "No results to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "compression_results.txt", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.results_text.toPlainText())
                self.statusBar().showMessage(f"Results saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def clear_results(self):
        """Clear results display"""
        self.results_text.clear()
        self.statusBar().showMessage("Results cleared")


def main():
    """Main function to run the GUI application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Bit Packing Compression GUI")
    app.setOrganizationName("Software Engineering Project")

    # Set modern application style
    app.setStyle('Fusion')

    # Set application icon (if available)
    # app.setWindowIcon(QIcon('icon.png'))

    # Create and show main window
    window = CompressionGUI()

    # Handle application exit
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
