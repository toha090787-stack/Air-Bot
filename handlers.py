from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import re

from states import ApplicationStates
from keyboards import *

router = Router()

# Константы
APPLICATION_NUMBER = "1111"
MISSING_PERSON = "Потеряшкин Евлампий"
BIRTH_DATE = "01.01.2000 (26 лет)"
MISSING_DATE = "01.04.2026"
LOCATION = "(по заданию инструктора)"
COORDINATES = "(по заданию инструктора)"

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    text = "Это симулятор бота Air-Pilot-Bot. Нажмите кнопку «Начать», чтобы приступить к тренировке"
    
    await message.answer(text, reply_markup=get_start_keyboard())

@router.callback_query(F.data == "start_training")
async def start_training(callback: CallbackQuery, state: FSMContext):
    """Начало тренировки"""
    text = f"""Заявка №{APPLICATION_NUMBER}
БВП: {MISSING_PERSON}
Возраст: {BIRTH_DATE}
Пропал: {MISSING_DATE}
Место: {LOCATION}
Координаты места: {COORDINATES}
<a href="https://www.windy.com">Погода в месте ПСР</a>"""
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_accept_decline_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "decline_application")
async def decline_application(callback: CallbackQuery, state: FSMContext):
    """Отклонение заявки"""
    await callback.message.edit_text(
        "Заявка отклонена",
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "accept_application")
async def accept_application(callback: CallbackQuery, state: FSMContext):
    """Принятие заявки"""
    accept_time = datetime.now().strftime("%H.%M %d.%m")
    username = callback.from_user.username or callback.from_user.first_name
    
    await state.update_data(accept_time=accept_time, username=username, visited_group=False)
    
    text = f"""🍀🍀🍀Статус работы по заявке🍀🍀🍀
БВП: {MISSING_PERSON}
Возраст: {BIRTH_DATE}
Пропал: {MISSING_DATE}
Место: {LOCATION}
Координаты места: {COORDINATES}
<a href="https://www.windy.com">Погода в месте ПСР</a>

1. Заявка №{APPLICATION_NUMBER} принята пилотом @{username}"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_application_menu_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await state.set_state(ApplicationStates.application_accepted)
    await callback.answer()

@router.callback_query(F.data == "group_link")
async def group_link(callback: CallbackQuery, state: FSMContext):
    """Переход в группу"""
    await state.update_data(visited_group=True)
    
    text = "Вы перешли и вступили в группу. В этой группе необходимо изучить задачу, место полетов и погодные условия. Теперь можно заполнить Заявку"
    
    await callback.answer(text, show_alert=True)

@router.callback_query(F.data == "create_application")
async def create_application(callback: CallbackQuery, state: FSMContext):
    """Формирование заявки"""
    data = await state.get_data()
    accept_time = data.get('accept_time', '')
    username = data.get('username', '')
    
    text = f"""🍀🍀🍀Статус работы по заявке🍀🍀🍀
БВП: {MISSING_PERSON}
Возраст: {BIRTH_DATE}
Пропал: {MISSING_DATE}
Место: {LOCATION}
Координаты места: {COORDINATES}
<a href="https://www.windy.com">Погода в месте ПСР</a>
1. Заявка №{APPLICATION_NUMBER} принята пилотом @{username}
—————————————
Выбор дня полета:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_date_selection_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await state.set_state(ApplicationStates.selecting_date)
    await callback.answer()

@router.callback_query(F.data.startswith("date_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    """Выбор даты"""
    date_str = callback.data.split("_")[1]
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    
    months_ru = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
                 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    
    formatted_date = f"{date_obj.day} {months_ru[date_obj.month - 1]} {date_obj.year}"
    
    await state.update_data(flight_date=formatted_date, flight_date_obj=date_str)
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {formatted_date}
—————————————
<b>Укажите:</b> время <b>начала</b> полета (UTC)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_time_selection_keyboard("back_to_date"),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_start_time)
    await callback.answer()

@router.callback_query(F.data == "back_to_date")
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору даты"""
    await create_application(callback, state)

@router.callback_query(ApplicationStates.selecting_start_time, F.data.startswith("time_"))
async def select_start_time(callback: CallbackQuery, state: FSMContext):
    """Выбор времени начала"""
    time_str = callback.data.split("_")[1]
    await state.update_data(start_time=time_str)
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {time_str} (UTC) - 
—————————————
<b>Укажите:</b> время <b>завершения</b> полета (UTC)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_time_selection_keyboard("back_to_start_time"),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_end_time)
    await callback.answer()

@router.callback_query(F.data == "back_to_start_time")
async def back_to_start_time(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору времени начала"""
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
—————————————
<b>Укажите:</b> время <b>начала</b> полета (UTC)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_time_selection_keyboard("back_to_date"),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_start_time)
    await callback.answer()

@router.callback_query(ApplicationStates.selecting_end_time, F.data.startswith("time_"))
async def select_end_time(callback: CallbackQuery, state: FSMContext):
    """Выбор времени окончания"""
    time_str = callback.data.split("_")[1]
    await state.update_data(end_time=time_str)
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {time_str} (UTC)
—————————————
<b>Укажите:<b> Максимальную высоту работы (истинную)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_altitude_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_altitude)
    await callback.answer()

@router.callback_query(F.data == "back_to_end_time")
async def back_to_end_time(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору времени окончания"""
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} (UTC) - 
—————————————
<b>Укажите:</b> время <b>завершения</b> полета (UTC)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_time_selection_keyboard("back_to_start_time"),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_end_time)
    await callback.answer()

@router.callback_query(ApplicationStates.selecting_altitude, F.data.startswith("altitude_"))
async def select_altitude(callback: CallbackQuery, state: FSMContext):
    """Выбор высоты"""
    altitude = callback.data.split("_")[1]
    await state.update_data(altitude=altitude)
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
—————————————
<b>Укажите:<b> Тип задачи"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_task_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_task_type)
    await callback.answer()

@router.callback_query(F.data == "back_to_altitude")
async def back_to_altitude(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору высоты"""
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
—————————————
<b>Укажите:<b> Максимальную высоту работы (истинную)"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_altitude_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_altitude)
    await callback.answer()

# ============ ПОЛИГОН ============

@router.callback_query(F.data == "task_polygon")
async def task_polygon(callback: CallbackQuery, state: FSMContext):
    """Выбор типа задачи: Полигон"""
    await state.update_data(task_type="polygon", polygon_coords=[])
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
<b>Зона работ:<b>
—————————————
<b>Укажите:<b> точки полигона по одной в формате GEO=55.799682,37.701270 (широта, долгота):"""
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ApplicationStates.entering_polygon_coordinates)
    await callback.answer()

@router.message(ApplicationStates.entering_polygon_coordinates)
async def enter_polygon_coordinates(message: Message, state: FSMContext):
    """Ввод координат полигона"""
    text = message.text.strip()
    
    # Проверка формата
    match = re.match(r'GEO=(-?\d+\.?\d*),(-?\d+\.?\d*)$', text)
    if not match:
        await message.answer("❌ Неверный формат. Используйте формат: GEO=55.799682,37.701270")
        return
    
    lat = match.group(1)
    lon = match.group(2)
    
    data = await state.get_data()
    coords = data.get('polygon_coords', [])
    coords.append({'lat': lat, 'lon': lon, 'raw': text})
    await state.update_data(polygon_coords=coords)
    
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    # Формируем строку зоны работ
    zone_text = " ".join([f"{c['lat']}N,{c['lon']}E" for c in coords])
    
    # Формируем список добавленных координат
    coords_list = "\n".join([f"широта: {c['lat']} долгота {c['lon']}" for c in coords])
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
<b>Зона работ:<b> {zone_text}
—————————————
<b>Добавлены координаты:<b>
{coords_list}"""
    
    await message.answer(text, reply_markup=get_polygon_coordinates_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "polygon_reset")
async def polygon_reset(callback: CallbackQuery, state: FSMContext):
    """Сброс координат полигона"""
    await state.update_data(polygon_coords=[])
    await task_polygon(callback, state)

@router.callback_query(F.data == "polygon_complete")
async def polygon_complete(callback: CallbackQuery, state: FSMContext):
    """Завершение ввода координат полигона"""
    data = await state.get_data()
    coords = data.get('polygon_coords', [])
    
    if not coords:
        await callback.answer("❌ Введите хотя бы одну точку полигона", show_alert=True)
        return
    
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    username = data.get('username', '')
    
    # Вычисление времени работы
    start_hour = int(start_time.split(':')[0])
    end_hour = int(end_time.split(':')[0])
    work_hours = end_hour - start_hour if end_hour >= start_hour else 24 - start_hour + end_hour
    
    # Первая точка для старта/посадки
    first_coord = coords[0]
    gt_start = f"{first_coord['lat']},{first_coord['lon']}"
    
    # Короткие координаты (первые 4 цифры без точки)
    zone_short = "\n".join([
        f"{c['lat'][:5].replace('.', '')}N,{c['lon'][:5].replace('.', '')}E" 
        for c in coords
    ])
    
    # Полные координаты
    zone_full = "\n".join([f"{c['lat']}N,{c['lon']}E" for c in coords])
    
    final_text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Тип:<b> Mavic 2 pro, борт №05е1938
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Общее время работы:<b> {work_hours}ч
<b>ГТ старт/посадка:<b> {gt_start}
<b>Зона работ:<b>
{zone_full}
<b>Зона работ:<b>
{zone_short}
<b>Нист:<b> 0-{altitude}м <b>Набс:<b> 0-{altitude}м
<b>ФИО пилота:<b> Здесь будут указаны ваши ФИО и телефон
<b>ФИО инфорга:<b> Здесь будут указаны ФИО инфорга, его телефон и ник в ТГ
<b>ФИО БВП:<b> {MISSING_PERSON}
<b>Контакт для связи:<b> @{username}"""
    
    await state.update_data(final_text=final_text)
    
    await callback.message.edit_text(
        final_text,
        reply_markup=get_final_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.final_application)
    await callback.answer()

# ============ РАДИУС ============

@router.callback_query(F.data == "task_radius")
async def task_radius(callback: CallbackQuery, state: FSMContext):
    """Выбор типа задачи: Радиус"""
    await state.update_data(task_type="radius")
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
<b>Маршрут радиусом:<b>
—————————————
<b>Укажите:<b> Радиус работы:"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_radius_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_radius)
    await callback.answer()

@router.callback_query(F.data == "back_to_task_type")
async def back_to_task_type(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору типа задачи"""
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
—————————————
<b>Укажите:<b> Тип задачи"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_task_type_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.selecting_task_type)
    await callback.answer()

@router.callback_query(ApplicationStates.selecting_radius, F.data.startswith("radius_"))
async def select_radius(callback: CallbackQuery, state: FSMContext):
    """Выбор радиуса"""
    radius = callback.data.split("_", 1)[1]
    await state.update_data(radius=radius)
    
    data = await state.get_data()
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
<b>Маршрут радиусом:<b> {radius}
—————————————
<b>Укажите:<b> координаты центра зоны в формате GEO=55.799682,37.701270 (широта,долгота):"""
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ApplicationStates.entering_radius_center)
    await callback.answer()

@router.message(ApplicationStates.entering_radius_center)
async def enter_radius_center(message: Message, state: FSMContext):
    """Ввод координат центра радиуса"""
    text = message.text.strip()
    
    # Проверка формата
    match = re.match(r'GEO=(-?\d+\.?\d*),(-?\d+\.?\d*)$', text)
    if not match:
        await message.answer("❌ Неверный формат. Используйте формат: GEO=55.799682,37.701270")
        return
    
    lat = match.group(1)
    lon = match.group(2)
    
    await state.update_data(radius_lat=lat, radius_lon=lon)
    
    response_text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
—————————————
<b>Добавлены координаты:<b>
широта: {lat}
долгота {lon}"""
    
    await message.answer(response_text, reply_markup=get_radius_center_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "radius_reset")
async def radius_reset(callback: CallbackQuery, state: FSMContext):
    """Сброс координат радиуса"""
    data = await state.get_data()
    radius = data.get('radius', '')
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    
    text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Нист:<b> 0-{altitude}м
<b>Маршрут радиусом:<b> {radius}
—————————————
<b>Укажите:<b> координаты центра зоны в формате GEO=55.799682,37.701270 (широта,долгота):"""
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "radius_confirm")
async def radius_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение координат радиуса"""
    data = await state.get_data()
    
    if 'radius_lat' not in data or 'radius_lon' not in data:
        await callback.answer("❌ Сначала введите координаты", show_alert=True)
        return
    
    flight_date = data.get('flight_date', '')
    start_time = data.get('start_time', '')
    end_time = data.get('end_time', '')
    altitude = data.get('altitude', '')
    radius = data.get('radius', '')
    lat = data.get('radius_lat', '')
    lon = data.get('radius_lon', '')
    username = data.get('username', '')
    
    # Вычисление времени работы
    start_hour = int(start_time.split(':')[0])
    end_hour = int(end_time.split(':')[0])
    work_hours = end_hour - start_hour if end_hour >= start_hour else 24 - start_hour + end_hour
    
    # Короткие координаты
    lat_short = lat[:5].replace('.', '')
    lon_short = lon[:5].replace('.', '')
    
    final_text = f"""<b>Заявка №{APPLICATION_NUMBER}</b>
<b>Основной день:</b> {flight_date}
<b>Тип:<b> Mavic 2 pro, борт №05е1938
<b>Время:<b> {start_time} - {end_time} (UTC)
<b>Общее время работы:<b> {work_hours}ч
<b>ГТ старт/посадка:<b> {lat},{lon}
<b>ГТ старт/посадка:<b> {lat_short}N,{lon_short}E
<b>Маршрут радиусом:<b> {radius}
<b>Нист:<b> 0-{altitude}м <b>Набс:<b> 0-{altitude}м
<b>ФИО пилота:<b> Здесь будут указаны ваши ФИО и телефон
<b>ФИО инфорга:<b> Здесь будут указаны ФИО инфорга, его телефон и ник в ТГ
<b>ФИО БВП:<b> {MISSING_PERSON}
<b>Контакт для связи:<b> @{username}"""
    
    await state.update_data(final_text=final_text)
    
    await callback.message.edit_text(
        final_text,
        reply_markup=get_final_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.final_application)
    await callback.answer()

# ============ ФИНАЛЬНЫЕ ДЕЙСТВИЯ ============

@router.callback_query(F.data == "edit_application")
async def edit_application(callback: CallbackQuery, state: FSMContext):
    """Редактирование заявки"""
    await create_application(callback, state)

@router.callback_query(F.data == "submit_application")
async def submit_application(callback: CallbackQuery, state: FSMContext):
    """Отправка заявки"""
    data = await state.get_data()
    final_text = data.get('final_text', '')
    visited_group = data.get('visited_group', False)
    
    result = "✅ Тест сдан" if visited_group else "❌ Тест провален"
    
    await callback.message.edit_text(final_text, parse_mode="HTML")
    await callback.message.answer(f" {result}")
    await callback.answer()

@router.callback_query(F.data == "add_note")
async def add_note(callback: CallbackQuery, state: FSMContext):
    """Добавление примечания"""
    await callback.message.answer("Отправьте мне сообщение, которое нужно добавить для АвиаКоординатора")
    await state.set_state(ApplicationStates.waiting_for_note)
    await callback.answer()

@router.message(ApplicationStates.waiting_for_note)
async def receive_note(message: Message, state: FSMContext):
    """Получение примечания"""
    note_text = message.text.strip()
    
    data = await state.get_data()
    final_text = data.get('final_text', '')
    
    updated_text = f"{final_text}\nПримечание от пилота: {note_text}"
    await state.update_data(final_text=updated_text)
    
    await message.answer(
        updated_text,
        reply_markup=get_final_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.final_application)
