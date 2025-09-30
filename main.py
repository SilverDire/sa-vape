# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGroupBox, QHBoxLayout, QDoubleSpinBox, QMessageBox, QSlider, QAbstractSpinBox)
import sys
from PyQt5.QtCore import Qt

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
        
        self.nic_base_input = QDoubleSpinBox() # поле ввода крепости никотиновой базы
        self.nic_base_input.setRange(0.0, 100.0) # диапазон значений
        self.nic_base_input.setSuffix(" мг/мл") # суффикс
        self.nic_base_input.setValue(100.0)
        
        self.pg_input = QDoubleSpinBox() # поле ввода PG
        self.pg_input.setRange(0.0, 100.0) # диапазон значений
        self.pg_input.setSuffix(" %") # суффикс
        
        self.vg_input = QDoubleSpinBox() # поле ввода VG
        self.vg_input.setRange(0.0, 100.0) # диапазон значений
        self.vg_input.setSuffix(" %") # суффикс
        
        self.nic_target_input = QDoubleSpinBox() # поле ввода желаемой крепости никотина
        self.nic_target_input.setRange(0.0, 100.0) # диапазон значений
        self.nic_target_input.setSuffix(" мг/мл") # суффикс

        self.pg_input.setDecimals(1) # точность PG до десятых
        self.pg_input.setSingleStep(0.5) # шаг изменения PG по умолчанию
        self.pg_input.setValue(50.0) # базовое значение PG

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
        self.aroma_widgets = [] # список виджетов ароматизаторов
        self.aroma_group = QGroupBox("Ароматизаторы") # группа для ароматизаторов

        # Кнопки
        self.btn_add = QPushButton("Добавить ароматизатор") # кнопка добавления ароматизатора
        self.btn_add.clicked.connect(self.add_aroma) # обработчик нажатия кнопки
        
        self.btn_calculate = QPushButton("Рассчитать") # кнопка расчета
        self.btn_calculate.clicked.connect(self.calculate) # обработчик нажатия кнопки
        
        self.btn_quit = QPushButton("&Закрыть") # кнопка закрытия
        self.btn_quit.clicked.connect(self.close) # обработчик нажатия кнопки

        self.result_label = QLabel("Результаты появятся здесь") # метка для вывода результатов

        # Основной лэйаут
        main_layout = QVBoxLayout() # вертикальный лэйаут
        main_layout.addWidget(QLabel("<center>Привет, мир! Пора варить стекло!</center>")) # метка приветствия
        
        # Группа основных параметров
        param_layout = QVBoxLayout() # вертикальный лэйаут для параметров
        param_layout.addWidget(QLabel("Общий объем жидкости")) # метка общего объема
        param_layout.addWidget(self.total_volume_input) # поле ввода общего объема
        param_layout.addWidget(QLabel("Крепость никотиновой базы")) # метка крепости никотиновой базы
        param_layout.addWidget(self.nic_base_input) # поле ввода крепости никотиновой базы
        param_layout.addWidget(QLabel("Соотношение PG/VG")) # метка соотношения PG/VG
        param_layout.addWidget(self.pg_slider) # ползунок регулировки соотношения

        ratio_values_layout = QHBoxLayout() # горизонтальный лэйаут для отображения значений PG/VG
        ratio_values_layout.addWidget(QLabel("PG")) # подпись для PG
        ratio_values_layout.addWidget(self.pg_input) # поле отображения PG
        ratio_values_layout.addWidget(QLabel("VG")) # подпись для VG
        ratio_values_layout.addWidget(self.vg_input) # поле отображения VG
        param_layout.addLayout(ratio_values_layout) # добавление значений PG/VG в параметры
        param_layout.addWidget(QLabel("Желаемая крепость никотина"))  # метка желаемой крепости никотина
        param_layout.addWidget(self.nic_target_input) # поле ввода желаемой крепости никотина
        
        # Группа ароматизаторов
        main_layout.addLayout(param_layout) # добавление параметров в основной лэйаут
        main_layout.addWidget(self.btn_add) # добавление кнопки добавления ароматизатора
        self.aroma_group.setLayout(self.aroma_section) # установка секции ароматизаторов в группу
        main_layout.addWidget(self.aroma_group) # добавление группы ароматизаторов в основной лэйаут

        # Группа кнопок
        main_layout.addWidget(self.btn_calculate) # добавление кнопки расчета
        main_layout.addWidget(self.result_label) # добавление метки результатов
        main_layout.addWidget(self.btn_quit) # добавление кнопки закрытия
        
        # Стили
        self.setLayout(main_layout) # установка основного лэйаута
        self.setWindowTitle("Расчет СТЕКЛА!") # заголовок окна
        self.resize(400, 600) # размер окна

    def add_aroma(self):
        """Добавление строки с ароматизатором"""
        row = QHBoxLayout() # вертикальный лэйаут для строки
        name = QLineEdit() # поле ввода названия ароматизатора
        name.setPlaceholderText("Название ароматизатора") # подсказка
        
        percent = QDoubleSpinBox() # поле ввода процента
        percent.setRange(0.0, 100.0) # диапазон значений
        percent.setSingleStep(0.5) # шаг
        percent.setSuffix(" %") # суффикс
        
        del_btn = QPushButton("×") # кнопка удаления
        del_btn.clicked.connect(lambda ch, w=row: self.remove_aroma(w)) # обработчик нажатия кнопки
        
        row.addWidget(name) # добавление названия в строку
        row.addWidget(percent) # добавление процента в строку
        row.addWidget(del_btn) # добавление кнопки удаления в строку
        
        self.aroma_section.addLayout(row) # добавление строки в секцию ароматизаторов
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
            
            # Проверка суммы процентов
#            total_percent = self.pg_input.value() + self.vg_input.value() # сумма процентов PG и VG
#            for _, percent, _ in self.aroma_widgets: # для каждого ароматизатора
#                total_percent += percent.value() # прибавить процент
                
#            if total_percent > 100: # если сумма процентов больше 100%
#                raise ValueError("Сумма процентов превышает 100%")
            
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
            
            result_text = (
                f"<b>Общий объем:</b> {total_volume:.1f} мл\n"
                f"<b>Никотиновая база:</b> {nic_needed:.2f} мл\n"
                f"<b>PG:</b> {pg_ml:.2f} мл\n"
                f"<b>VG:</b> {vg_ml:.2f} мл\n\n"
                f"<b>Ароматизаторы:</b>\n" + "\n".join(aromas)
            )
            
            self.result_label.setText(result_text) # установка текста метки результатов
            
        except Exception as e: # обработка ошибок
            QMessageBox.critical(self, "Ошибка", str(e)) # вывод сообщения об ошибке 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = sa_vape()
    window.show()
    sys.exit(app.exec_())
