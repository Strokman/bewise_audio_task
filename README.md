# Audio service. Task 2

Сервис предназначен для конвертации файлов из формата `.wav` в `.mp3`, 
сохранения файла в базу данных и отдаче его пользователю по ссылке.
Для использования необходима базовая авторизация.
Для установки сервиса необходимы docker, docker compose, git, аккаунт на Github

Сервис использует фреймворк Flask (backend), PostgreSQL (БД), gunicorn (HTTP server).
В `.mp3` файлы конвертируются утилитой `lame`
(python-библиотека `pydub` использует `ffmpeg`, с которым контейнер весит около 2 gb, 
что явно чрезмерно для такого функционала)

## Запуск сервиса

Клонируйте репозиторий:

```
git clone https://github.com/Strokman/bewise_audio_task
```

Перейдите в созданную директорию:

```
cd bewise_audio_task
```

Внутри этой директории сделайте файл скрипта `create_service.sh` исполняемым и запустите его при помощи следующих команд:

```
chmod +x create_service.sh
./create_service.sh
```

В случае каких-либо ошибок в процессе установки - выполните запуск скрипта с правами суперпользователя (sudo)

После этого к сервису можно обратиться по ссылке вида `http://<host>:<port>/<route>`

По умолчанию это будет ссылка вида (http://localhost:5100/). В дальнейшем в инструкции будет использоваться этот формат.
В конфигурации используютcя нестандартные порты (5600 для postgres и 5100 для web-сервиса), так как предполагаю,
что стандартные могут быть уже заняты, в том числе чтобы исключить конфликты с контейнерами из первого задания.
Если и эти порты заняты - в файле `docker-compose.yml` необходимо прописать в обоих сервисах другие, свободные,
порты хост-машины

    ports:
      - 5600:5432

(первый номер порта - до двоеточия). В адресе запроса необходимо будет использовать тот порт, 
который будет указан в `.yml` файле для web-сервиса.

### Использование сервиса

Обращаться к сервису можно через командную строку утилитой `curl`, а также любым подходящим софтом (Postman и т.д.).

Методом POST в форме передается имя пользователя:

```
curl -iX POST -F username=<username> http://localhost:5100/api/register
```

После этого сервис сгенерирует ответ в формате json, в котором пользователю будут сообщены его uuid и токен доступа:

```
{"token":"<token>","uuid":"<uuid>"}
```

Эту информацию нужно сохранить для загрузки файла, которая происходит при помощи выполнения следующего запроса
(вставляем в формы путь к файлу, а также полученные в прошлом пункте регистрационные данные)

```
curl -i -X POST -F file=@/path/to/file -F uuid=<uuid> -F token=<token> "http://localhost:5100/api/file"
```

Можно указать абсолютный путь или только имя файла, если он находится в текущей директории.
В репозитории в папке `audio/static/FILE_SAMPLES` для удобства сохранены несколько файлов,
которые можно использовать в качестве образца. Сервис принимает только `.wav` файлы, поэтому также приложены
файлы с недопустимыми расширениями и именами для проверки.

После загрузки, если файл соответствует всем требованиям (формат, не пустое имя файла), сервис конвертирует его в `.mp3`,
генерирует `uuid` для файла, сохраняет в базу данных и отдает ссылку для скачивания файл,
которая содержит `uuid` файла и `id` пользователя:

```
Please save the download link for your file - http://localhost:5100/api/record?id=<file_uuid>&user=<id>
```

Получить файл можно просто перейдя по ссылке (см. выше), тогда файл будет скачан автоматически через браузер,
либо также обратиться по ссылке утилитой `curl`

```
curl 'http://localhost:5100/api/record?id=<file_uuid>&user=<id>' --output <filename>.mp3
```

Имя файла формируется из `uuid` пользователя и `uuid` файла для избежания конфликтов и дублирования имени файла.
При использовании `curl` имя сохраняемого файла нужно указать самому в аргументе `--output`

Обратите внимание - если в ссылке будут предоставлены неверные данные, то curl не выдаст ошибок и
просто сохранит пустой файл. Необходимо повторить процедуру с корректными данными.
