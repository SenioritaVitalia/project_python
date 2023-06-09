# Анализ фильмов с Кинопоиска
Проект в рамках курса по анализу данных
Небольшое описание структуры работы:

# Фильм на вечер 🎞
### Шаг 1
В качестве темы проекта мы выбрали анализ данных о фильмах с Кинопоиска.

### Шаг 2
Для начала спарсили данные о 4000 фильмах с Кинопоиска. Это была нетривиалиная задача, поэтому параллельно мы парсили Golden Apple и Booking Com. В конечном итоге, получилось спарсить Кинопоиск, мы остановились на полученном датасете.

### Шаг 3
Предварительныя обработка данных.
На этом шаге, мы описали переменные, удалили нерепрезентативные, пропуски, в некоторых местах заменили пропуски на средние значения. Убрали аномальные наблюдения (выбросы).

После этого шага мы подключились все к гитхабу и работали через консоль.

### Шаг 4
Визуализация данных. Полученные графики помогли сформулировать гипотезы и заметить интересные вещи.

### Шаг 5
Тут мы добавили новые признаки, которые потенциально влияют на количество сборов фильма: дата выходна - выходной или нет, а также был ли в год выхода внешний шок (кризис или другое мировое событие)

### Шаг 6
Тестирование гипотез
Мы рассмотрели три блока гипотез, связанных с различными переменными: дата выхода, бюджет фильма и длина фильма.
Для тестирования гипотез использовались различные методы, исходя из особенностей данных и формулировки гипотезы:
- t-тест
- бутстрап
- перестановочный тест
- z-тест
- U-тест Манна-Уитни

### Шаг 7
В данной части мы построили модель линейной регрессии, Lasso регресси, градиентого бустинга и усовершенствовали следующими методами:
- нормирование данных
- one hot encoding
- подбор гиперпараметров для Lasso регрессии
- подбор гиперпараметров для градиентного бустинга
