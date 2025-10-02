# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGroupBox, QHBoxLayout, QDoubleSpinBox, QMessageBox, QSlider, QAbstractSpinBox, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFontDatabase, QFont, QColor
from pathlib import Path
import sys
from PyQt5.QtCore import Qt, QObject, QEvent, QVariantAnimation, QEasingCurve
policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

CUSTOM_FONTS = {
    "cyberpunk": "Cyberpunk_RUS_BY_LYAJKA.ttf",
    "zelek": "newzelekc.otf",
    "latoBold": "Lato-Bold.ttf"
}

class FocusGlowFilter(QObject):
    def __init__(self, color, duration):
        super().__init__()
        self.base_color = QColor(color)     # сохраняем исходный цвет
        self.effect = QGraphicsDropShadowEffect()
        self.effect.setBlurRadius(20)
        self.effect.setColor(QColor(self.base_color))
        self.effect.setOffset(0, 0)

        # Анимация по альфе (0 → color.alpha())
        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.base_color.alpha())
        self.animation.setDuration(duration)    # в мс
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._apply_alpha)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            obj.setGraphicsEffect(self.effect)
            self.effect.setEnabled(True)
            
            # Запускаем анимацию вперёд
            self.animation.setDirection(QVariantAnimation.Forward)
            self.animation.start()
        elif event.type() == QEvent.FocusOut:
            if self.effect:
                # Анимация назад (затухание)
                self.animation.setDirection(QVariantAnimation.Backward)
                self.animation.start()
                self.effect.setEnabled(False)
        return False # пропускаем событие дальше
    
    def _apply_alpha(self, alpha):
        if not self.effect:
            return
        self.base_color.setAlpha(int(alpha))
        self.effect.setColor(self.base_color)
        self.effect.setEnabled(alpha > 0)

def load_custom_fonts():
    fonts_dir = Path(__file__).parent / "fonts"
    families = {}
    for key, filename in CUSTOM_FONTS.items():
        font_path = fonts_dir / filename
        if not font_path.exists():
            raise FileNotFoundError(f"{font_path} не найден")
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id == -1:
            raise RuntimeError(f"Не удалось загрузить {filename}")
        registered = QFontDatabase.applicationFontFamilies(font_id)
        if not registered:
            raise RuntimeError(f"{filename} загружен, но семейства не зарегистрированы")
        families[key] = registered[0]   # берем первое семейство
    return families

class sa_vape(QWidget): # класс окна
    def __init__(self): # конструктор
        super().__init__() # вызов конструктора родительского класса
        self._updating_ratio = False # служебный флаг для синхронизации ползунка и спинбоксов
        self.init_ui() # инициализация интерфейса
        
    def init_ui(self): # функция инициализации интерфейса
        # Основные поля ввода
        self.total_volume_input = QDoubleSpinBox() # поле ввода общего объема
        self.total_volume_input.setRange(0.1, 1000.0) # диапазон значений
        self.total_volume_input.setSuffix(" мл") # суффикс
        self.total_volume_input.setValue(100.0)
        self.total_volume_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у volumeinput
        
        self.nic_base_input = QDoubleSpinBox() # поле ввода крепости никотиновой базы
        self.nic_base_input.setRange(0.0, 100.0) # диапазон значений
        self.nic_base_input.setSuffix(" мг/мл") # суффикс
        self.nic_base_input.setValue(100.0)
        self.nic_base_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у nicbase
        
        self.pg_input = QDoubleSpinBox() # поле ввода PG
        self.pg_input.setRange(0.0, 100.0) # диапазон значений
        self.pg_input.setSuffix(" %") # суффикс
        
        self.vg_input = QDoubleSpinBox() # поле ввода VG
        self.vg_input.setRange(0.0, 100.0) # диапазон значений
        self.vg_input.setSuffix(" %") # суффикс
        
        self.nic_target_input = QDoubleSpinBox() # поле ввода желаемой крепости никотина
        self.nic_target_input.setRange(0.0, 100.0) # диапазон значений
        self.nic_target_input.setSuffix(" мг/мл") # суффикс
        self.nic_target_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у nic

        self.pg_input.setDecimals(1) # точность PG до десятых
        self.pg_input.setSingleStep(0.5) # шаг изменения PG по умолчанию
        self.pg_input.setValue(50.0) # базовое значение PG
        self.pg_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у PG

        self.vg_input.setDecimals(1) # точность VG до десятых
        self.vg_input.setSingleStep(0.5) # шаг изменения VG по умолчанию
        self.vg_input.setValue(50.0) # базовое значение VG
        self.vg_input.setReadOnly(True) # запрет ручного ввода VG
        self.vg_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у VG

        self.pg_slider = QSlider(Qt.Horizontal) # ползунок для управления соотношением PG/VG
        self.pg_slider.setRange(0, 100) # диапазон значений в процентах
        self.pg_slider.setSingleStep(10) # шаг при управлении с клавиатуры
        self.pg_slider.setPageStep(10) # шаг при PageUp/PageDown
        self.pg_slider.setValue(int(round(self.pg_input.value()))) # синхронизация ползунка c PG
        self.pg_slider.valueChanged.connect(self.update_ratio_from_slider) # связь ползунка со значениями
        self.pg_input.valueChanged.connect(self.update_slider_from_pg) # связь ручного ввода PG с ползунком

        # Секция ароматизаторов
        self.aroma_section = QVBoxLayout() # вертикальный лэйаут для ароматизаторов
        self.aroma_section.setContentsMargins(5, 45, 5, 5)  # (int left, int top, int right, int bottom)
        self.aroma_widgets = [] # список виджетов ароматизаторов
        self.aroma_group = QGroupBox("Ароматизаторы") # группа для ароматизаторов
        self.aroma_group.setMinimumSize(260, 150)
        self.aroma_group.setSizePolicy(policy)
        # Кнопки
        self.btn_add = QPushButton("Добавить ароматизатор") # кнопка добавления ароматизатора
        self.btn_add.clicked.connect(self.add_aroma) # обработчик нажатия кнопки
        
        self.btn_calculate = QPushButton("Рассчитать") # кнопка расчета
        self.btn_calculate.clicked.connect(self.calculate) # обработчик нажатия кнопки
        
        # блок результатов
        self.result_total_label = QLabel("Общий объем: —") # строка для общего объема
        self.result_nic_label = QLabel("Никотиновая база: —") # строка для никотиновой базы
        self.result_pg_label = QLabel("PG: —") # строка для PG
        self.result_vg_label = QLabel("VG: —") # строка для VG
        self.result_aroma_label = QLabel("Ароматизаторы: —") # строка для ароматизаторов
        self.result_aroma_label.setWordWrap(True) # перенос строк для списка ароматизаторов

        # Основной лэйаут
        main_layout = QVBoxLayout() # вертикальный лэйаут
        header_label = QLabel("<center>SA-VAPE</center>") # метка приветствия
        header_rofl = QLabel("<center>Йоу, чумба, пора делать стекло!!!</center>") # метка обращения с приколом
        main_layout.addWidget(header_label)
        main_layout.addWidget(header_rofl)
        
        content_layout = QHBoxLayout() # горизонтальное размещение параметров и результатов
        
        # Группа основных параметров

        ## Создаём группу подписей для полей ввода
        param_labels = [
            QLabel("Общий объём жидкости"),
            QLabel("Крепость никотиновой базы"),
            QLabel("Соотношение PG/VG"),
            QLabel("PG"),
            QLabel("VG"),
            QLabel("Желаемая крепость никотина"),
        ]
        
        ## Создаем объекты
        self.total_volume_label = param_labels[0]
        self.nic_base_label = param_labels[1]
        self.PG_VG_ratio_label = param_labels[2]
        self.PG_label = param_labels[3]
        self.VG_label = param_labels[4]
        self.nic_target_label = param_labels[5]

        ## добавляем объекты на лэйаут
        # Основные параметры
        param_layout = QVBoxLayout() # вертикальный лэйаут для параметров
        param_layout.setContentsMargins(1, 10, 1, 1)  # (int left, int top, int right, int bottom)
        param_layout.addWidget(self.total_volume_label) # метка общего объема
        param_layout.addWidget(self.total_volume_input) # поле ввода общего объема
        param_layout.addWidget(self.nic_base_label) # метка крепости никотиновой базы
        param_layout.addWidget(self.nic_base_input) # поле ввода крепости никотиновой базы
        param_layout.addWidget(self.PG_VG_ratio_label) # метка соотношения PG/VG
        param_layout.addWidget(self.pg_slider) # ползунок регулировки соотношения
        
        # соотношения PG и VG, никотин
        ratio_values_layout = QHBoxLayout() # горизонтальный лэйаут для отображения значений PG/VG
        ratio_values_layout.addWidget(self.PG_label) # подпись для PG
        ratio_values_layout.addWidget(self.pg_input) # поле отображения PG
        ratio_values_layout.addWidget(self.VG_label) # подпись для VG
        ratio_values_layout.addWidget(self.vg_input) # поле отображения VG
        param_layout.addLayout(ratio_values_layout) # добавление значений PG/VG в параметры
        param_layout.addWidget(self.nic_target_label)  # метка желаемой крепости никотина
        param_layout.addWidget(self.nic_target_input) # поле ввода желаемой крепости никотина
        
        controls_layout = QVBoxLayout() # левая колонка с параметрами и контролами
        controls_layout.addLayout(param_layout)
        controls_layout.addWidget(self.btn_add) # добавление кнопки добавления ароматизатора
        self.aroma_group.setLayout(self.aroma_section) # установка секции ароматизаторов в группу
        controls_layout.addWidget(self.aroma_group) # добавление группы ароматизаторов в колонку
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_calculate) # добавление кнопки расчета
        
        result_group = QGroupBox("Результаты") # блок результатов
        result_group_layout = QVBoxLayout() # вертикальный лэйаут блока результатов
        result_group_layout.setContentsMargins(6, 45, 12, 1)   # top = 24 создаёт зазор над первой строкой (int left, int top, int right, int bottom)
        result_group_layout.addWidget(self.result_total_label) # строка общего объема
        result_group_layout.addWidget(self.result_nic_label) # строка никотиновой базы
        result_group_layout.addWidget(self.result_pg_label) # строка PG
        result_group_layout.addWidget(self.result_vg_label) # строка VG
        result_group_layout.addWidget(self.result_aroma_label) # строка ароматизаторов
        result_group_layout.addStretch()
        result_group.setObjectName("ResultGroup") # помещаем в контейнер для задания стилей
        result_group.setLayout(result_group_layout)                         

        content_layout.addLayout(controls_layout, 2)
        content_layout.addWidget(result_group, 1)
        
        main_layout.addLayout(content_layout)
        header_label2 = QLabel("<center>By SilverDire And Ameteon</center>") # метка о авторах
        main_layout.addWidget(header_label2)
        
        # Графика

        ## Надписи основных параметров
        labels_font = QFont(FONT_FAMILIES["latoBold"], 14)
        for i in param_labels:
            i.setFont(labels_font)

        ## Заголовки
        header_label.setFont(QFont(FONT_FAMILIES["cyberpunk"], 45)) # установка шрифта заголовка
        header_label2.setFont(QFont(FONT_FAMILIES["zelek"], 20)) # установка шрифта надписи о авторах
        header_rofl.setFont(QFont(FONT_FAMILIES["zelek"], 15)) # установка шрифта рофло надписи
        
        ## Включаем подсветку выбранных полей (для ароматизаторов в функции добавления)
        self.input_glow = FocusGlowFilter(QColor(0, 244, 255, 128), duration=200)
        self.total_volume_input.installEventFilter(self.input_glow)
        self.nic_base_input.installEventFilter(self.input_glow)
        self.nic_target_input.installEventFilter(self.input_glow)

        ## графика через стили
        result_group.setStyleSheet(f"""
            #ResultGroup QLabel {{
                font-family: '{FONT_FAMILIES['latoBold']}';
                font-size: 14pt;
        }}
        """)

        self.setStyleSheet(f"""
               
        QWidget {{
            background-color: #060814;
            color: #e0f7ff;
        }}
        
        QDoubleSpinBox {{
            border: 1px solid #143245;
            border-radius: 6px;
            background: rgba(8, 12, 25, 0.85);
            color: #e0f7ff;
            selection-background-color: #00f4ff;
            selection-color: #060814;
            font-size: 14pt;
            font-family: '{FONT_FAMILIES['latoBold']}';
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.9,
                                        fx:0.5, fy:0.5,
                                        stop:0 rgba(0, 244, 255, 0.20),
                                        stop:1 rgba(8, 12, 25, 0.9));
        }}


        QLineEdit {{
            border: 1px solid #143245;
            border-radius: 6px;
            background: rgba(8, 12, 25, 0.85);
            color: #e0f7ff;
            selection-background-color: #00f4ff;
            selection-color: #060814;
            font-size: 15pt;
            font-family: '{FONT_FAMILIES['zelek']}';
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.9,
                                        fx:0.5, fy:0.5,
                                        stop:0 rgba(0, 244, 255, 0.20),
                                        stop:1 rgba(8, 12, 25, 0.9));

        }}        

        QLineEdit:hover, QDoubleSpinBox:hover {{
            border: 1px solid #ff3bf1;
        }}

        QLineEdit:disabled, QDoubleSpinBox:disabled {{
            color: #597a8b;
            border-color: #0c1822;
            background: rgba(8, 12, 25, 0.4);
        }}
        
        QGroupBox {{
            font-size: 22pt;
            font-family: '{FONT_FAMILIES['zelek']}';
            border: 1px solid #143245;
            border-radius: 8px;
            margin-top: 12px;
            background: rgba(8, 12, 25, 0.6);
        }}
   
        QGroupBox::title {{
            subcontrol-origin: content;
            subcontrol-position: top left;
            padding: 7px 1px 0 5px;
        }}
                           
        QPushButton {{
            font-size: 20pt;
            font-family: '{FONT_FAMILIES['zelek']}';
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #00f4ff, stop:1 #ff3bf1);
            color: #060814;
            border-radius: 15px;
            padding: 6px 12px;
        }}
        
        QPushButton:hover {{
            border: 1px solid #00f4ff;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3dffff, stop:1 #ff6bff);
        }}
        
        QSlider::groove:horizontal {{
            background: #143245;
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #3dffff, stop:1 #ff6bff);
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        
        """)
        
        # Стили
        self.setLayout(main_layout) # установка основного лэйаута
        self.setWindowTitle("Расчет СТЕКЛА!") # заголовок окна
        self.resize(800, 970) # размер окна
        
    def add_aroma(self):
        """Добавление строки с ароматизатором"""
        row = QHBoxLayout() # вертикальный лэйаут для строки
        name = QLineEdit() # поле ввода названия ароматизатора
        name.setPlaceholderText("Название ароматизатора") # подсказка
        
        percent = QDoubleSpinBox() # поле ввода процента
        percent.setRange(0.0, 100.0) # диапазон значений
        percent.setSingleStep(0.5) # шаг
        percent.setSuffix(" %") # суффикс
        percent.setButtonSymbols(QAbstractSpinBox.NoButtons) # скрываем стрелки у аромок
        
        del_btn = QPushButton("×") # кнопка удаления
        del_btn.clicked.connect(lambda ch, w=row: self.remove_aroma(w)) # обработчик нажатия кнопки
        
        row.addWidget(name) # добавление названия в строку
        row.addWidget(percent) # добавление процента в строку
        row.addWidget(del_btn) # добавление кнопки удаления в строку
        
        self.aroma_section.addLayout(row) # добавление строки в секцию ароматизаторов
        self.aroma_group.setMinimumHeight(self.aroma_group.sizeHint().height())
        self.aroma_group.updateGeometry()
        self.aroma_widgets.append((name, percent, row)) # добавление в список виджетов
        
    def remove_aroma(self, layout):
        """Удаление строки с ароматизатором"""
        index = self.aroma_section.indexOf(layout) # индекс строки
        if index >= 0: # если индекс существует
            item = self.aroma_section.takeAt(index) # удаление строки
            if item.widget(): # если виджет
                item.widget().deleteLater() # удаление виджета
            elif item.layout(): # если лэйаут
                while item.layout().count(): # пока лэйаут содержит элементы
                    child = item.layout().takeAt(0) # удаление первого элемента
                    if child.widget(): # если виджет
                        child.widget().deleteLater() # удаление виджета
                item.layout().deleteLater() # удаление лэйаута
            self.aroma_widgets = [w for w in self.aroma_widgets if w[2] != layout] # обновление списка виджетов


    def update_ratio_from_slider(self, slider_value):
        """Синхронизация значений PG/VG при движении ползунка"""
        if self._updating_ratio: # предотвращаем зацикливание сигналов
            return
        snapped_value = int(round(slider_value / 10) * 10)
        snapped_value = max(0, min(100, snapped_value))
        self._updating_ratio = True
        if snapped_value != slider_value:
            self.pg_slider.setValue(snapped_value)
            slider_value = snapped_value
        pg_percent = float(slider_value)
        self.pg_input.setValue(pg_percent)
        vg_percent = max(0.0, 100.0 - pg_percent)
        self.vg_input.setValue(vg_percent)
        self._updating_ratio = False

    def update_slider_from_pg(self, pg_percent):
        """Синхронизация ползунка при ручном вводе PG"""
        if self._updating_ratio: # предотвращаем зацикливание сигналов
            return
        snapped_pg = round(pg_percent / 10.0) * 10
        snapped_pg = min(max(snapped_pg, 0.0), 100.0)
        self._updating_ratio = True
        if self.pg_input.value() != snapped_pg:
            self.pg_input.setValue(snapped_pg)
        slider_value = int(snapped_pg)
        if self.pg_slider.value() != slider_value:
            self.pg_slider.setValue(slider_value)
        vg_percent = max(0.0, 100.0 - snapped_pg)
        self.vg_input.setValue(vg_percent)
        self._updating_ratio = False

    def calculate(self):
        """Расчет параметров"""
        try: # обработка ошибок
            total_volume = self.total_volume_input.value() # общий объем
            nic_base = self.nic_base_input.value() # крепость никотиновой базы
            target_nic = self.nic_target_input.value() # желаемая крепость никотина
                       
            # Фиксируем VG как задано
            vg_percent = self.vg_input.value()
            vg_ml = (total_volume * vg_percent) / 100

            # Расчет никотина
            nic_needed = (target_nic * total_volume) / nic_base # расчет необходимого количества никотина          
          
            # Расчет ароматизаторов
            aroma_total = 0
            aromas = []
            for name, percent, _ in self.aroma_widgets: # для каждого ароматизатора
                amount = (total_volume * percent.value()) / 100 # расчет объема
                aroma_total += amount
                aromas.append(f"{name.text()}: {amount:.2f} мл") # добавление в список
            
            # PG получает оставшийся объем после ароматизаторов и никотина
            pg_ml = total_volume - (vg_ml + nic_needed + aroma_total)
            
            # Проверка на отрицательные значения
            if pg_ml < 0:
                raise ValueError("Недостаточно объема для всех компонентов")
            
            self.result_total_label.setText(f"Общий объем: {total_volume:.1f} мл")
            self.result_nic_label.setText(f"Никотиновая база: {nic_needed:.2f} мл")
            self.result_pg_label.setText(f"PG: {pg_ml:.2f} мл")
            self.result_vg_label.setText(f"VG: {vg_ml:.2f} мл")
            if aromas:
                aroma_lines = "\n".join(aromas)
                self.result_aroma_label.setText("Ароматизаторы:\n" + aroma_lines)
            else:
                self.result_aroma_label.setText("Ароматизаторы: отсутствуют")
            
        except Exception as e: # обработка ошибок
            QMessageBox.critical(self, "Ошибка", str(e)) # вывод сообщения об ошибке 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    FONT_FAMILIES = load_custom_fonts()
    window = sa_vape()
    window.show()
    sys.exit(app.exec_())
