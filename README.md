# bewise_audio_task



curl -iX POST -H "Content-Type: application/json" -d '{"username": "strokman"}' http://127.0.0.1:5000/register


curl -i -X POST -F file=@/Users/antonstrokov/PycharmProjects/bewise_audio_task/file_example_WAV_5MG.wav "http://localhost:5000/file"

curl -i -X POST -F file=@/Users/antonstrokov/PycharmProjects/bewise_audio_task/file_example_WAV_5MG.wav -F uuid="strokman-~86unye3" -F token="a60cd2ae-a228-4d4c-8733-1c7e53e7789f" "http://localhost:5000/file"
