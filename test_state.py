from game.engine import Game
# Создаём новую партию.
original = Game()
# Немного изменяем состояние.
original.move(1) 
original.step()
# Получаем снимок состояния.
state = original.get_state()
# Восстанавливаем партию в новый объект.
restored = Game.load_state(state)
# Проверяем, что все сохранённые данные совпадают.
assert restored.get_state() == state
# Проверяем, что генераторы выдают одинаковую следующую фигуру.
assert original._draw_kind() == restored._draw_kind()
print("Все проверки пройдены!")