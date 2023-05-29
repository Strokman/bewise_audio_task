# bewise_audio_task



curl -iX POST -H "Content-Type: application/json" -d '{"username": "strokman"}' http://127.0.0.1:5000/register


curl -i -X POST -F file=@/Users/antonstrokov/PycharmProjects/bewise_audio_task/file_example_WAV_5MG.wav -F uuid="strokman-~93sutn10" -F token="5eaeb59a-97ea-4081-a688-8b09a69a139c" "http://localhost:5000/file"
