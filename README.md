# Audio service. Task 2

Сервис предназначен для конвертации файлов из формата wav в mp3, сохранения файла в базу данных и отдаче его пользователю по ссылке.
Для использования необходима базовая авторизация.
Методом POST в форме передается имя пользователя
curl -iX POST -F username="strokman" http://127.0.0.1:5000/register


curl -i -X POST -F file=@/Users/antonstrokov/PycharmProjects/bewise_audio_task/FILE_SAMPLES/file_example_WAV_1MG.wav -F uuid='strokman-UjSuByUk' -F token='712d4818-0b55-4fe7-8da6-76e8b1060117' "http://strokman.synology.me:5100/file"


Please save the download link for your file - http://strokman.synology.me:5100/record?id=b0df28f6-db4c-44cc-ad43-64ab2898e4b5&user=1


curl 'http://localhost:5100/record?id=6b01ec35-637d-4dbd-88cd-9920c3b7992e&user=strokman-OiUkHqSy' --output kekek.mp3




curl -i -X POST -F file=@file_example_WAV_10MG.wav -F uuid='strokman-MpSoAeSa' -F token='6a61207d-608f-411a-849e-8d65417c7d1a' "http://localhost:5100/file"
