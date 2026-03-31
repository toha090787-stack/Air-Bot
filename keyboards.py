from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def get_start_keyboard():
    """Клавиатура с кнопкой Начать"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data="start_training")]
    ])
    return keyboard

def get_accept_decline_keyboard():
    """Клавиатура принять/отклонить заявку"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data="accept_application")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_application")]
    ])
    return keyboard

def get_application_menu_keyboard():
    """Меню после принятия заявки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔ Принято вами", callback_data="accepted_by_you")],
        [InlineKeyboardButton(text="🤦 Передумал", callback_data="changed_mind")],
        [InlineKeyboardButton(text="🔗 Ссылка на группу", callback_data="group_link")],
        [InlineKeyboardButton(text="📮 Сформировать заявку", callback_data="create_application")]
    ])
    return keyboard

def get_date_selection_keyboard():
    """Клавиатура выбора даты (14 дней)"""
    buttons = []
    today = datetime.now()
    
    days_ru = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    months_ru = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
                 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    
    for i in range(14):
        date = today + timedelta(days=i)
        day_name = days_ru[date.weekday()]
        month_name = months_ru[date.month - 1]
        
        button_text = f"{date.day} {month_name} ({day_name})"
        callback_data = f"date_{date.strftime('%d.%m.%Y')}"
        
        if i % 2 == 0:
            buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        else:
            buttons[-1].append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_time_selection_keyboard(back_callback="back_to_date"):
    """Клавиатура выбора времени (00:00 - 23:00)"""
    buttons = []
    row = []
    
    for hour in range(24):
        time_str = f"{hour:02d}:00"
        row.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))
        
        if len(row) == 5:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="◀️Назад", callback_data=back_callback)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_altitude_keyboard():
    """Клавиатура выбора высоты"""
    altitudes = [50, 70, 90, 100, 120, 150, 180, 200, 250, 300, 350, 400, 450, 500, 550, 600]
    buttons = []
    row = []
    
    for alt in altitudes:
        row.append(InlineKeyboardButton(text=f"{alt}м", callback_data=f"altitude_{alt}"))
        
        if len(row) == 4:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="◀️Назад к времени окончания", callback_data="back_to_end_time")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_task_type_keyboard():
    """Клавиатура выбора типа задачи"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Полигон", callback_data="task_polygon")],
        [InlineKeyboardButton(text="Радиус", callback_data="task_radius")],
        [InlineKeyboardButton(text="Коридор", callback_data="task_corridor")],
        [InlineKeyboardButton(text="◀️Назад к высоте", callback_data="back_to_altitude")]
    ])
    return keyboard

def get_polygon_coordinates_keyboard():
    """Клавиатура для ввода координат полигона"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌Ввести координаты заново", callback_data="polygon_reset")],
        [InlineKeyboardButton(text="✅Все точки полигона введены", callback_data="polygon_complete")]
    ])
    return keyboard

def get_radius_keyboard():
    """Клавиатура выбора радиуса"""
    radii = ["500м", "1000м", "1500м", "2000м", "2500м", "3000м", 
             "4км", "5км", "6км", "7км", "8км", "10км", "15км", "25км", "30км"]
    buttons = []
    row = []
    
    for radius in radii:
        row.append(InlineKeyboardButton(text=radius, callback_data=f"radius_{radius}"))
        
        if len(row) == 4:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="◀️Назад к выбору типа задачи", callback_data="back_to_task_type")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_radius_center_keyboard():
    """Клавиатура для координат центра радиуса"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌Ввести координаты заново", callback_data="radius_reset")],
        [InlineKeyboardButton(text="✅Координаты центра верны", callback_data="radius_confirm")]
    ])
    return keyboard

def get_final_keyboard():
    """Финальная клавиатура заявки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍Редактировать", callback_data="edit_application")],
        [InlineKeyboardButton(text="✅Отправить", callback_data="submit_application")],
        [InlineKeyboardButton(text="Добавить произвольную информацию для АК", callback_data="add_note")]
    ])
    return keyboard
