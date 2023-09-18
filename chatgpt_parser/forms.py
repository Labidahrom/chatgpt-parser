from django import forms


class CreateTextForm(forms.Form):
    set_name = forms.CharField(
        label='Введите название для набора',
        widget=forms.TextInput(
            attrs={'placeholder': 'Название набора'})
    )
    temperature = forms.FloatField(
        label='Температура (от 0 до 1)',
        initial=0,
        min_value=0,
        max_value=1,
        widget=forms.TextInput(
            attrs={'placeholder': 'Дробное число от 0 до 1'})
    )
    text_len = forms.IntegerField(
        label='Минимальная длина текста в символах. Если поставить '
              'больше 0, будет включена проверка длины текста указанному'
              ' значению. Допустимый диапазон: от 1 до 3000',
        initial=0,
        min_value=0,
        max_value=3000,
        widget=forms.TextInput(
            attrs={'placeholder': 'от 0 до 3000'})
    )
    tasks_strings = forms.CharField(
        label='Введите список значений',
        widget=forms.Textarea(
            attrs={'placeholder': 'запрос к ChatGPT||тема текста'})
    )
    rewriting_task = forms.CharField(
        label='Запрос к ChatGPT если у текста будет низкая уникальность'
              ' (по умолчанию будет текст ниже)',
        initial='Нужно сделать следующий текст не похожим ни на '
                'какой другой текст существующий на момент твоего '
                'создания, добавить новые детали, факты:'
    )
    required_uniqueness = forms.IntegerField(
        label='Требуемый процент уникальности. Если процент уникальности'
              ' ниже указанного значения, текст будет переписан',
        initial=80,
        min_value=0,
        max_value=100,
    )
