from vk_api.keyboard import VkKeyboard, VkKeyboardColor

KEY_DICT = {
            'Start search': 'начать поиск пользователей ВК',
            'Stop': 'завершить работу с ботом',
            'Search': 'запустить поиск пользователей ВК по выбранным критериям',
            'Check database': 'посмотреть выбранных пользователей ВК',
            'Next': 'следующая запись',
            'Prev': 'предыдущая запись',
            'Delete': 'удалить пользователя из базы данных',
            'Show next': 'показать анкету следующего пользователя ВК',
            'Add': 'добавить пользователя в базу данных',
            'Male': 'Пол мужской',
            'Female': 'Пол женский',
            'Any gender': 'Пол не важен',
            'PrevUser': 'Предыдущий пользователь',
            'NextUser': 'Следующий пользователь',
            'BanUser': 'Забанить пользователя',
}

class Keyboard(VkKeyboard):
    """
    Класс Keyboard для создания кнопок меню бота
    """
    def __init__(self, buttons: list = [], one_time: bool = False, inline: bool = False):
        self.buttons = buttons
        self.one_time = one_time
        self.inline = inline
        self.keyboard = VkKeyboard(self.one_time, self.inline)
        if buttons:
            if len(buttons) > 3:
                lines = int(len(buttons) // 2)
                for ind in range(lines):
                    self.keyboard.add_button(label=buttons[ind * 2][0], color=buttons[ind * 2][1])
                    self.keyboard.add_button(label=buttons[ind * 2 + 1][0], color=buttons[ind * 2 + 1][1])
                    if ind < lines - 1:
                        self.keyboard.add_line()
                if int(len(buttons) % 2) == 1:
                    self.keyboard.add_line()
                    self.keyboard.add_button(label=buttons[-1][0], color=buttons[-1][1])
            else:
                for button in buttons:
                    self.keyboard.add_button(label=button[0], color=button[1])

    def __str__(self):
        """
        Строка подсказка по работе с клавиатурой
        """
        kb_string = ''
        if self.buttons:
            for button in self.buttons:
                if button[0] in KEY_DICT.keys():
                    kb_string += f'"{button[0]}" - {KEY_DICT[button[0]]}\n'
        return kb_string