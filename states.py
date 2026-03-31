from aiogram.fsm.state import State, StatesGroup

class ApplicationStates(StatesGroup):
    waiting_for_start = State()
    application_accepted = State()
    selecting_date = State()
    selecting_start_time = State()
    selecting_end_time = State()
    selecting_altitude = State()
    selecting_task_type = State()
    
    # Для полигона
    entering_polygon_coordinates = State()
    
    # Для радиуса
    selecting_radius = State()
    entering_radius_center = State()
    
    # Финальные состояния
    final_application = State()
    waiting_for_note = State()
