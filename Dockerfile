# установка базового образа (host OS)
FROM python:3.10.5
# установка рабочей директории в контейнере
WORKDIR /code
# копирование файла зависимостей в рабочую директорию
COPY requirements.txt .
# установка зависимостей
RUN pip install -r requirements.txt
# копирование содержимого локальной директории src в рабочую директорию
COPY main.py ./
COPY ./src/ src
COPY v9.dat ./
# команда, выполняемая при запуске контейнера
CMD [ "python", "main.py" ]