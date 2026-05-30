import sys
import json
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QListWidget, QTextEdit, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

STYLE = """
QMainWindow { background-color: #121212; }
QWidget { background-color: #121212; color: #FFFFFF; font-family: Arial; }
QPushButton {
    background-color: #6200EA; color: white; border-radius: 8px;
    padding: 8px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background-color: #9D4EDD; }
QPushButton:disabled { background-color: #4A4A4A; color: #888888; }
QComboBox, QListWidget, QTextEdit, QLineEdit {
    background-color: #1E1E1E; border: 1px solid #333333;
    border-radius: 5px; padding: 5px; font-size: 14px; color: #FFFFFF;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #6200EA; }
QListWidget::item:selected { background-color: #6200EA; color: white; }
"""

class KitchenApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PsinaRecept")
        self.resize(950, 600) 
        self.setStyleSheet(STYLE)

        # Данные
        self.all_recipes = []
        self.favorites = []
        self.found_recipes = []
        self.current_dish = None

        #загрузка базы
        try:
            with open('recipes.json', 'r', encoding='utf-8') as f:
                self.all_recipes = json.load(f)
        except FileNotFoundError:
            print("⚠️ Файл recipes.json не найден. Приложение запущено без рецептов.")
        except json.JSONDecodeError:
            print("⚠️ Ошибка чтения JSON. Проверьте формат файла.")

        #глав конт.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        #просмотр рецепта
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("🍽️ Название блюда:"))
        self.title_field = QLineEdit()
        self.title_field.setReadOnly(True)
        self.title_field.setFont(QFont("Arial", 18, QFont.Bold))
        left_layout.addWidget(self.title_field)

        left_layout.addWidget(QLabel("📝 Ингредиенты и шаги:"))
        self.content_field = QTextEdit()
        self.content_field.setReadOnly(True)
        self.content_field.setFont(QFont("Arial", 12))
        left_layout.addWidget(self.content_field)

        self.btn_add_fav = QPushButton("❤️ В избранное")
        self.btn_add_fav.clicked.connect(self.add_favorite)
        left_layout.addWidget(self.btn_add_fav)

        #фильтр список кнопки
        right_layout = QVBoxLayout()

        #фильтры
        right_layout.addWidget(QLabel("🔍 Фильтры:"))
        filter_layout = QHBoxLayout()
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(["Все", "Завтрак", "Обед", "Ужин", "Десерты"])
        self.combo_diff = QComboBox()
        self.combo_diff.addItems(["Все", "Легко", "Средне", "Сложно"])
        btn_search = QPushButton("Найти")
        btn_search.clicked.connect(self.search_recipes)

        filter_layout.addWidget(QLabel("Категория:"))
        filter_layout.addWidget(self.combo_cat)
        filter_layout.addWidget(QLabel("Сложность:"))
        filter_layout.addWidget(self.combo_diff)
        filter_layout.addWidget(btn_search)
        right_layout.addLayout(filter_layout)

        #список рецептов
        right_layout.addWidget(QLabel("📖 Каталог рецептов:"))
        self.recipes_list = QListWidget()
        self.recipes_list.itemClicked.connect(self.show_selected_recipe)
        right_layout.addWidget(self.recipes_list)

        #кнопки управления
        btn_random = QPushButton("🎲 Случайное блюдо")
        btn_random.clicked.connect(self.show_random)
        btn_favorites = QPushButton("❤️ Мое избранное")
        btn_favorites.clicked.connect(self.show_favorites)
        btn_exit = QPushButton("🚪 Выход")
        btn_exit.clicked.connect(self.close)

        right_layout.addWidget(btn_random)
        right_layout.addWidget(btn_favorites)
        right_layout.addWidget(btn_exit)

        #сборка основного макета
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        #инициализация списка при запуске
        self.search_recipes()

    def search_recipes(self):
        self.recipes_list.clear()
        self.found_recipes.clear()

        cat = self.combo_cat.currentText()
        diff = self.combo_diff.currentText()

        for recipe in self.all_recipes:
            if (cat == "Все" or recipe.get("category") == cat):
                if (diff == "Все" or recipe.get("difficulty") == diff):
                    self.found_recipes.append(recipe)
                    self.recipes_list.addItem(recipe["name"])

    def show_selected_recipe(self, item):
        row = self.recipes_list.row(item)
        if 0 <= row < len(self.found_recipes):
            self.current_dish = self.found_recipes[row]
            self.fill_recipe_text()

    def show_random(self):
        if not self.all_recipes:
            return
        self.current_dish = random.choice(self.all_recipes)
        #случайное блюдо
        self.recipes_list.clear()
        self.found_recipes = [self.current_dish]
        self.recipes_list.addItem(self.current_dish["name"])
        self.recipes_list.setCurrentRow(0)
        self.fill_recipe_text()

    def show_favorites(self):
        self.recipes_list.clear()
        self.found_recipes.clear()
        for recipe in self.all_recipes:
            if recipe["name"] in self.favorites:
                self.found_recipes.append(recipe)
                self.recipes_list.addItem(recipe["name"])
        
        if self.found_recipes:
            self.recipes_list.setCurrentRow(0)
            self.show_selected_recipe(self.recipes_list.currentItem())
        else:
            self.title_field.clear()
            self.content_field.clear()
            self.btn_add_fav.setText("❤️ В избранное")
            self.btn_add_fav.setEnabled(True)

    def fill_recipe_text(self):
        self.title_field.setText(self.current_dish["name"])
        
        text = f"Категория: {self.current_dish.get('category', '-')} | Сложность: {self.current_dish.get('difficulty', '-')} | Время: {self.current_dish.get('time', '-')}\n\n"
        text += "🛒 ИНГРЕДИЕНТЫ:\n"
        for ing in self.current_dish.get("ingredients", []):
            text += f"- {ing}\n"
            
        text += "\n👨‍🍳 ШАГИ:\n"
        steps = self.current_dish.get("steps", "")
        text += steps.replace("\\n", "\n")
        
        self.content_field.setText(text)

        #обновления состояние кнопки избранного
        if self.current_dish["name"] in self.favorites:
            self.btn_add_fav.setText("✅ В избранном")
            self.btn_add_fav.setEnabled(False)
        else:
            self.btn_add_fav.setText("❤️ В избранное")
            self.btn_add_fav.setEnabled(True)

    def add_favorite(self):
        if self.current_dish:
            name = self.current_dish["name"]
            if name not in self.favorites:
                self.favorites.append(name)
                self.btn_add_fav.setText("✅ В избранном")
                self.btn_add_fav.setEnabled(False)
                print(f"✅ Добавлено в избранное: {name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KitchenApp()
    window.show()
    sys.exit(app.exec_())
