import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from pathlib import Path

class ParametersEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор Parameters.json")
        self.root.geometry("1200x800")
        
        # Пути к файлам
        self.default_path = Path("Loot/Items/Default/Parameters.json")
        self.override_path = Path("Loot/Items/Override/Parameters.json")  # Читаем Parameters.json
        self.save_path = Path("Loot/Items/Override/Parameters_moded.json")  # Сохраняем как Parameters_moded.json
        
        # Данные CooldownGroups
        self.cooldown_groups = {}
        
        # Данные
        self.default_data = {}
        self.override_data = {}
        self.current_item = None
        
        self.create_widgets()
        self.load_cooldown_groups()
        self.load_data()
        self.create_footer()
        
    def load_cooldown_groups(self):
        """Загрузка данных о группах отката"""
        cooldown_dir = Path("Loot/CooldownGroups/Override")
        if cooldown_dir.exists():
            try:
                # Ищем первый JSON файл в папке
                json_files = list(cooldown_dir.glob("*.json"))
                if json_files:
                    cooldown_file = json_files[0]  # Берем первый найденный файл
                    with open(cooldown_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Загружаем группы отката
                    for group in data.get('CooldownGroups', []):
                        name = group.get('Name', '')
                        if name:
                            self.cooldown_groups[name] = {
                                'CooldownMin': group.get('CooldownMin', 0),
                                'CooldownMax': group.get('CooldownMax', 0),
                                'IsAffectedByLowerGroups': group.get('IsAffectedByLowerGroups', True),
                                '_comment': group.get('_comment', '')
                            }
                    print(f"Загружено групп отката: {len(self.cooldown_groups)}")
                    
            except Exception as e:
                print(f"Ошибка загрузки CooldownGroups: {str(e)}")
    
    def get_cooldown_group_info(self, group_name):
        """Получение информации о группе отката"""
        if group_name in self.cooldown_groups:
            group = self.cooldown_groups[group_name]
            min_val = group['CooldownMin']
            max_val = group['CooldownMax']
            comment = group['_comment']
            
            info = f"{min_val} - {max_val}"
            if comment:
                info += f" ({comment})"
            return info
        return ""
        
    def create_widgets(self):
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка "Предметы по умолчанию"
        self.default_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.default_frame, text="Предметы по умолчанию")
        self.create_default_tab()
        
        # Вкладка "Override"
        self.override_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.override_frame, text="Override")
        self.create_override_tab()
        
    def create_footer(self):
        """Создание нижнего колонтитула"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill='x', side='bottom', pady=5)
        
        footer_label = ttk.Label(footer_frame, text="Made for SCUM from AndreyGL", 
                               foreground='gray', font=('Arial', 8))
        footer_label.pack(side='right', padx=10)
    
    def create_default_tab(self):
        # Поиск
        search_frame = ttk.Frame(self.default_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск по ID:").pack(side='left')
        self.default_search_var = tk.StringVar()
        self.default_search_entry = ttk.Entry(search_frame, textvariable=self.default_search_var)
        self.default_search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.default_search_entry.bind('<KeyRelease>', self.filter_default_items)
        
        # Список предметов
        list_frame = ttk.Frame(self.default_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Счётчик записей
        self.default_counter_label = ttk.Label(self.default_frame, text="Всего записей: 0")
        self.default_counter_label.pack(anchor='e', padx=5, pady=2)
        
        ttk.Label(list_frame, text="Список предметов:").pack(anchor='w')
        
        self.default_listbox = tk.Listbox(list_frame)
        self.default_listbox.pack(fill='both', expand=True)
        self.default_listbox.bind('<<ListboxSelect>>', self.on_default_select)
        
        # Блок характеристик
        self.create_details_frame(self.default_frame)
        
    def create_override_tab(self):
        main_frame = ttk.Frame(self.override_frame)
        main_frame.pack(fill='both', expand=True)
        
        # Левая панель - редактирование Override
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        
        # Поиск в Override
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="Поиск по ID:").pack(side='left')
        self.override_search_var = tk.StringVar()
        self.override_search_entry = ttk.Entry(search_frame, textvariable=self.override_search_var)
        self.override_search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.override_search_entry.bind('<KeyRelease>', self.filter_override_items)
        
        # Список Override
        ttk.Label(left_frame, text="Предметы в Override:").pack(anchor='w')
        
        self.override_listbox = tk.Listbox(left_frame)
        self.override_listbox.pack(fill='both', expand=True)
        self.override_listbox.bind('<<ListboxSelect>>', self.on_override_select)
        
        # Счётчик записей Override
        self.override_counter_label = ttk.Label(left_frame, text="Записей в Override: 0")
        self.override_counter_label.pack(anchor='e', padx=5, pady=2)
        
        # Кнопки управления Override
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Удалить выбранный предмет", 
                  command=self.delete_from_override).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Очистить все", 
                  command=self.clear_all_override).pack(side='left', padx=5)
                
        # Блок характеристик для редактирования
        self.create_edit_frame(left_frame)
        
        # Кнопка сохранения
        ttk.Button(left_frame, text="Сохранить изменения", 
                  command=self.save_override).pack(pady=10)
        
        # Правая панель - добавление из Defaults
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(right_frame, text="Добавить из Defaults:").pack(anchor='w')
        
        # Поиск в Defaults для добавления
        add_search_frame = ttk.Frame(right_frame)
        add_search_frame.pack(fill='x', pady=5)
        
        ttk.Label(add_search_frame, text="Поиск:").pack(side='left')
        self.add_search_var = tk.StringVar()
        self.add_search_entry = ttk.Entry(add_search_frame, textvariable=self.add_search_var)
        self.add_search_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.add_search_entry.bind('<KeyRelease>', self.filter_add_items)
        
        # Список для добавления
        self.add_listbox = tk.Listbox(right_frame)
        self.add_listbox.pack(fill='both', expand=True)
        
        # Кнопка добавления
        ttk.Button(right_frame, text="Добавить выбранный предмет", 
                  command=self.add_from_default).pack(pady=10)
        
    def create_details_frame(self, parent):
        self.details_frame = ttk.LabelFrame(parent, text="Характеристики предмета")
        self.details_frame.pack(fill='x', padx=5, pady=5)
        
        # ID
        ttk.Label(self.details_frame, text="ID:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.id_label = ttk.Label(self.details_frame, text="")
        self.id_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # IsDisabledForSpawning
        ttk.Label(self.details_frame, text="Отключен спавн:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.spawn_label = ttk.Label(self.details_frame, text="")
        self.spawn_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # AllowedLocations
        ttk.Label(self.details_frame, text="Допустимые локации:").grid(row=2, column=0, sticky='nw', padx=5, pady=2)
        self.locations_text = scrolledtext.ScrolledText(self.details_frame, height=3, width=40, state='disabled')
        self.locations_text.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        
        # Cooldown values
        ttk.Label(self.details_frame, text="Откат респавна (мин/макс):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.cooldown_label = ttk.Label(self.details_frame, text="")
        self.cooldown_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)
        
        # CooldownGroup
        ttk.Label(self.details_frame, text="Группа отката:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.cooldown_group_label = ttk.Label(self.details_frame, text="")
        self.cooldown_group_label.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        
        # CooldownGroup Info
        ttk.Label(self.details_frame, text="Инфо группы отката:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        self.cooldown_group_info_label = ttk.Label(self.details_frame, text="", foreground='blue')
        self.cooldown_group_info_label.grid(row=5, column=1, sticky='w', padx=5, pady=2)
        
        # Variations
        ttk.Label(self.details_frame, text="Варианты:").grid(row=6, column=0, sticky='nw', padx=5, pady=2)
        self.variations_text = scrolledtext.ScrolledText(self.details_frame, height=3, width=40, state='disabled')
        self.variations_text.grid(row=6, column=1, sticky='w', padx=5, pady=2)
        
        # Usage settings
        ttk.Label(self.details_frame, text="Исп. предопр. при спавне:").grid(row=7, column=0, sticky='w', padx=5, pady=2)
        self.override_usage_label = ttk.Label(self.details_frame, text="")
        self.override_usage_label.grid(row=7, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(self.details_frame, text="Предопр. использование:").grid(row=8, column=0, sticky='w', padx=5, pady=2)
        self.initial_usage_label = ttk.Label(self.details_frame, text="")
        self.initial_usage_label.grid(row=8, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(self.details_frame, text="Случ. предопр. использований:").grid(row=9, column=0, sticky='w', padx=5, pady=2)
        self.random_usage_label = ttk.Label(self.details_frame, text="")
        self.random_usage_label.grid(row=9, column=1, sticky='w', padx=5, pady=2)
        
    def create_edit_frame(self, parent):
        self.edit_frame = ttk.LabelFrame(parent, text="Редактирование характеристик")
        self.edit_frame.pack(fill='x', padx=5, pady=5)
        
        # ID (только чтение)
        ttk.Label(self.edit_frame, text="ID:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.edit_id_var = tk.StringVar()
        self.edit_id_entry = ttk.Entry(self.edit_frame, textvariable=self.edit_id_var, state='readonly')
        self.edit_id_entry.grid(row=0, column=1, sticky='we', padx=5, pady=2)
        
        # IsDisabledForSpawning
        ttk.Label(self.edit_frame, text="Отключен спавн:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.edit_spawn_var = tk.BooleanVar()
        self.edit_spawn_check = ttk.Checkbutton(self.edit_frame, variable=self.edit_spawn_var)
        self.edit_spawn_check.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # AllowedLocations
        ttk.Label(self.edit_frame, text="Допустимые локации:").grid(row=2, column=0, sticky='nw', padx=5, pady=2)
        self.locations_frame = ttk.Frame(self.edit_frame)
        self.locations_frame.grid(row=2, column=1, sticky='we', padx=5, pady=2)
        
        self.location_vars = {}
        locations = ["Coastal", "Continental", "Mountain", "Urban", "Rural", "Industrial"]
        for i, location in enumerate(locations):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.locations_frame, text=location, variable=var)
            cb.grid(row=i//2, column=i%2, sticky='w', padx=5)
            self.location_vars[location] = var
        
        # Cooldown values
        ttk.Label(self.edit_frame, text="Откат респавна (мин):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.edit_cooldown_min_var = tk.StringVar()
        self.edit_cooldown_min_entry = ttk.Entry(self.edit_frame, textvariable=self.edit_cooldown_min_var)
        self.edit_cooldown_min_entry.grid(row=3, column=1, sticky='we', padx=5, pady=2)
        
        ttk.Label(self.edit_frame, text="Откат респавна (макс):").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.edit_cooldown_max_var = tk.StringVar()
        self.edit_cooldown_max_entry = ttk.Entry(self.edit_frame, textvariable=self.edit_cooldown_max_var)
        self.edit_cooldown_max_entry.grid(row=4, column=1, sticky='we', padx=5, pady=2)
        
        # CooldownGroup
        ttk.Label(self.edit_frame, text="Группа отката:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        
        cooldown_group_frame = ttk.Frame(self.edit_frame)
        cooldown_group_frame.grid(row=5, column=1, sticky='we', padx=5, pady=2)
        
        self.edit_cooldown_group_var = tk.StringVar()
        self.edit_cooldown_group_combobox = ttk.Combobox(cooldown_group_frame, 
                                                        textvariable=self.edit_cooldown_group_var,
                                                        values=[""] + sorted(self.cooldown_groups.keys()))
        self.edit_cooldown_group_combobox.pack(side='left', fill='x', expand=True)
        self.edit_cooldown_group_combobox.bind('<<ComboboxSelected>>', self.on_cooldown_group_selected)
        self.edit_cooldown_group_combobox.bind('<KeyRelease>', self.on_cooldown_group_typed)
        
        # Info label for cooldown group
        self.cooldown_group_edit_info = ttk.Label(self.edit_frame, text="", foreground='blue')
        self.cooldown_group_edit_info.grid(row=6, column=1, sticky='w', padx=5, pady=2)
        
        # Variations
        ttk.Label(self.edit_frame, text="Варианты (JSON):").grid(row=7, column=0, sticky='nw', padx=5, pady=2)
        self.edit_variations_text = scrolledtext.ScrolledText(self.edit_frame, height=3, width=40)
        self.edit_variations_text.grid(row=7, column=1, sticky='we', padx=5, pady=2)
        
        # Usage settings
        ttk.Label(self.edit_frame, text="Исп. предопр. при спавне:").grid(row=8, column=0, sticky='w', padx=5, pady=2)
        self.edit_override_usage_var = tk.BooleanVar()
        self.edit_override_usage_check = ttk.Checkbutton(self.edit_frame, variable=self.edit_override_usage_var)
        self.edit_override_usage_check.grid(row=8, column=1, sticky='w', padx=5, pady=2)
        
        ttk.Label(self.edit_frame, text="Предопр. использование:").grid(row=9, column=0, sticky='w', padx=5, pady=2)
        self.edit_initial_usage_var = tk.StringVar()
        self.edit_initial_usage_entry = ttk.Entry(self.edit_frame, textvariable=self.edit_initial_usage_var)
        self.edit_initial_usage_entry.grid(row=9, column=1, sticky='we', padx=5, pady=2)
        
        ttk.Label(self.edit_frame, text="Случ. предопр. использований:").grid(row=10, column=0, sticky='w', padx=5, pady=2)
        self.edit_random_usage_var = tk.StringVar()
        self.edit_random_usage_entry = ttk.Entry(self.edit_frame, textvariable=self.edit_random_usage_var)
        self.edit_random_usage_entry.grid(row=10, column=1, sticky='we', padx=5, pady=2)
        
        self.edit_frame.columnconfigure(1, weight=1)
    
    def on_cooldown_group_selected(self, event):
        """Обработчик выбора группы отката из комбобокса"""
        group_name = self.edit_cooldown_group_var.get()
        self.update_cooldown_group_info(group_name)
    
    def on_cooldown_group_typed(self, event):
        """Обработчик ручного ввода группы отката"""
        group_name = self.edit_cooldown_group_var.get()
        self.update_cooldown_group_info(group_name)
    
    def update_cooldown_group_info(self, group_name):
        """Обновление информации о группе отката"""
        if group_name in self.cooldown_groups:
            info = self.get_cooldown_group_info(group_name)
            self.cooldown_group_edit_info.config(text=info)
        else:
            self.cooldown_group_edit_info.config(text="")
        
    def load_data(self):
        # Загрузка данных по умолчанию
        if not self.default_path.exists():
            messagebox.showerror("Ошибка", "Необходимо экспортировать файл Parameters.json")
            return
        
        try:
            with open(self.default_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.default_data = {item['Id']: item for item in data.get('Parameters', [])}
            
            # Обновление списков
            self.update_default_list()
            self.update_add_list()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")
        
        # Загрузка данных override (читаем Parameters.json)
        if self.override_path.exists():
            try:
                with open(self.override_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.override_data = {item['Id']: item for item in data.get('Parameters', [])}
                
                self.update_override_list()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки override файла: {str(e)}")
        else:
            # Создаем пустую структуру если файла нет
            self.override_data = {}
    
    def update_default_list(self, filter_text=""):
        self.default_listbox.delete(0, tk.END)
        items = [id for id in self.default_data.keys() 
                if filter_text.lower() in id.lower()]
        for item in sorted(items):
            self.default_listbox.insert(tk.END, item)
        
        # Обновляем счётчик
        total_count = len(self.default_data.keys())
        filtered_count = len(items)
        if filter_text:
            self.default_counter_label.config(text=f"Записей: {filtered_count} (отфильтровано из {total_count})")
        else:
            self.default_counter_label.config(text=f"Всего записей: {total_count}")
    
    def update_override_list(self, filter_text=""):
        self.override_listbox.delete(0, tk.END)
        items = [id for id in self.override_data.keys() 
                if filter_text.lower() in id.lower()]
        for item in sorted(items):
            self.override_listbox.insert(tk.END, item)
        
        # Обновляем счётчик
        total_count = len(self.override_data.keys())
        filtered_count = len(items)
        if filter_text:
            self.override_counter_label.config(text=f"Записей: {filtered_count} (отфильтровано из {total_count})")
        else:
            self.override_counter_label.config(text=f"Записей в Override: {total_count}")
    
    def update_add_list(self, filter_text=""):
        self.add_listbox.delete(0, tk.END)
        items = [id for id in self.default_data.keys() 
                if filter_text.lower() in id.lower()]
        for item in sorted(items):
            self.add_listbox.insert(tk.END, item)
    
    def filter_default_items(self, event):
        self.update_default_list(self.default_search_var.get())
    
    def filter_override_items(self, event):
        self.update_override_list(self.override_search_var.get())
    
    def filter_add_items(self, event):
        self.update_add_list(self.add_search_var.get())
    
    def on_default_select(self, event):
        selection = self.default_listbox.curselection()
        if selection:
            item_id = self.default_listbox.get(selection[0])
            self.display_item_details(item_id, self.default_data[item_id])
    
    def on_override_select(self, event):
        selection = self.override_listbox.curselection()
        if selection:
            item_id = self.override_listbox.get(selection[0])
            self.display_edit_item(item_id, self.override_data[item_id])
    
    def display_item_details(self, item_id, item_data):
        self.id_label.config(text=item_id)
        self.spawn_label.config(text=str(item_data.get('IsDisabledForSpawning', False)))
        
        # Locations
        self.locations_text.config(state='normal')
        self.locations_text.delete(1.0, tk.END)
        locations = item_data.get('AllowedLocations', [])
        self.locations_text.insert(tk.END, ', '.join(locations))
        self.locations_text.config(state='disabled')
        
        # Cooldown
        cooldown_min = item_data.get('CooldownPerSquadMemberMin', 0)
        cooldown_max = item_data.get('CooldownPerSquadMemberMax', 0)
        self.cooldown_label.config(text=f"{cooldown_min} / {cooldown_max}")
        
        cooldown_group = item_data.get('CooldownGroup', '')
        self.cooldown_group_label.config(text=cooldown_group)
        
        # Cooldown group info
        group_info = self.get_cooldown_group_info(cooldown_group)
        self.cooldown_group_info_label.config(text=group_info)
        
        # Variations
        self.variations_text.config(state='normal')
        self.variations_text.delete(1.0, tk.END)
        variations = item_data.get('Variations', [])
        self.variations_text.insert(tk.END, json.dumps(variations, indent=2, ensure_ascii=False))
        self.variations_text.config(state='disabled')
        
        # Usage
        self.override_usage_label.config(text=str(item_data.get('ShouldOverrideInitialAndRandomUsage', False)))
        self.initial_usage_label.config(text=str(item_data.get('InitialUsageOverride', 0)))
        self.random_usage_label.config(text=str(item_data.get('RandomUsageOverrideUsage', 0)))
    
    def display_edit_item(self, item_id, item_data):
        """Отображение данных предмета для редактирования"""
        self.current_item = item_id
        
        self.edit_id_var.set(item_id)
        self.edit_spawn_var.set(item_data.get('IsDisabledForSpawning', False))
        
        # Locations
        locations = item_data.get('AllowedLocations', [])
        for location, var in self.location_vars.items():
            var.set(location in locations)
        
        # Cooldown
        self.edit_cooldown_min_var.set(str(item_data.get('CooldownPerSquadMemberMin', 0)))
        self.edit_cooldown_max_var.set(str(item_data.get('CooldownPerSquadMemberMax', 0)))
        
        # CooldownGroup
        cooldown_group = item_data.get('CooldownGroup', '')
        self.edit_cooldown_group_var.set(cooldown_group)
        self.update_cooldown_group_info(cooldown_group)
        
        # Variations
        self.edit_variations_text.delete(1.0, tk.END)
        variations = item_data.get('Variations', [])
        self.edit_variations_text.insert(tk.END, json.dumps(variations, indent=2, ensure_ascii=False))
        
        # Usage
        self.edit_override_usage_var.set(item_data.get('ShouldOverrideInitialAndRandomUsage', False))
        self.edit_initial_usage_var.set(str(item_data.get('InitialUsageOverride', 0)))
        self.edit_random_usage_var.set(str(item_data.get('RandomUsageOverrideUsage', 0)))
    
    def add_from_default(self):
        selection = self.add_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите предмет для добавления")
            return
        
        item_id = self.add_listbox.get(selection[0])
        
        if item_id in self.override_data:
            messagebox.showwarning("Предупреждение", f"Предмет с ID '{item_id}' уже существует в Override")
            return
        
        # Копируем данные из default
        self.override_data[item_id] = self.default_data[item_id].copy()
        self.update_override_list()
        messagebox.showinfo("Успех", f"Предмет '{item_id}' добавлен в Override")
    
    def save_override(self):
        if not self.current_item:
            messagebox.showwarning("Предупреждение", "Выберите предмет для сохранения")
            return
        
        try:
            # Обновляем текущий элемент
            item_data = self.override_data[self.current_item]
            
            item_data['IsDisabledForSpawning'] = self.edit_spawn_var.get()
            
            # Locations
            item_data['AllowedLocations'] = [loc for loc, var in self.location_vars.items() if var.get()]
            
            # Cooldown
            item_data['CooldownPerSquadMemberMin'] = float(self.edit_cooldown_min_var.get() or 0)
            item_data['CooldownPerSquadMemberMax'] = float(self.edit_cooldown_max_var.get() or 0)
            item_data['CooldownGroup'] = self.edit_cooldown_group_var.get()
            
            # Variations
            variations_text = self.edit_variations_text.get(1.0, tk.END).strip()
            if variations_text:
                item_data['Variations'] = json.loads(variations_text)
            else:
                item_data['Variations'] = []
            
            # Usage
            item_data['ShouldOverrideInitialAndRandomUsage'] = self.edit_override_usage_var.get()
            item_data['InitialUsageOverride'] = float(self.edit_initial_usage_var.get() or 0)
            item_data['RandomUsageOverrideUsage'] = float(self.edit_random_usage_var.get() or 0)
            
            # Сохраняем в файл Parameters_moded.json
            output_data = {
                "Parameters": list(self.override_data.values())
            }
            
            # Создаем папку если не существует
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Успех", f"Файл сохранен: {self.save_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def delete_from_override(self):
        """Удаление выбранного предмета из Override"""
        selection = self.override_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите предмет для удаления")
            return
        
        item_id = self.override_listbox.get(selection[0])
        
        # Подтверждение удаления
        result = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить предмет '{item_id}' из Override?",
            icon='warning'
        )
        
        if result:
            # Удаляем запись
            if item_id in self.override_data:
                del self.override_data[item_id]
                
                # Если удаляемый предмет был текущим, сбрасываем форму редактирования
                if self.current_item == item_id:
                    self.current_item = None
                    self.clear_edit_form()
                
                # Обновляем список
                self.update_override_list(self.override_search_var.get())
                messagebox.showinfo("Успех", f"Предмет '{item_id}' удален из Override")
            else:
                messagebox.showerror("Ошибка", f"Предмет '{item_id}' не найден в Override")

    def clear_all_override(self):
        """Очистка всех записей из Override"""
        if not self.override_data:
            messagebox.showinfo("Информация", "Override уже пуст")
            return
        
        # Подтверждение очистки
        result = messagebox.askyesno(
            "Подтверждение очистки", 
            f"Вы уверены, что хотите удалить ВСЕ записи из Override? ({len(self.override_data)} записей)",
            icon='warning'
        )
        
        if result:
            # Очищаем все данные
            self.override_data.clear()
            self.current_item = None
            self.clear_edit_form()
            
            # Обновляем список
            self.update_override_list()
            messagebox.showinfo("Успех", "Все записи удалены из Override")

    def clear_edit_form(self):
        """Очистка формы редактирования"""
        self.edit_id_var.set("")
        self.edit_spawn_var.set(False)
        
        # Сбрасываем чекбоксы локаций
        for var in self.location_vars.values():
            var.set(False)
        
        # Сбрасываем остальные поля
        self.edit_cooldown_min_var.set("0")
        self.edit_cooldown_max_var.set("0")
        self.edit_cooldown_group_var.set("")
        self.cooldown_group_edit_info.config(text="")
        
        # Очищаем текстовые поля
        self.edit_variations_text.delete(1.0, tk.END)
        
        # Сбрасываем usage настройки
        self.edit_override_usage_var.set(False)
        self.edit_initial_usage_var.set("0")
        self.edit_random_usage_var.set("0")

def main():
    root = tk.Tk()
    app = ParametersEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()