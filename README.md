# bewise_audio_task



curl -iX POST -F username="strokman" http://127.0.0.1:5000/register


curl -i -X POST -F file=@/Users/antonstrokov/PycharmProjects/bewise_audio_task/WAV_samples/file_example_WAV_10MG.wav -F uuid='strokman-7P6Y3s5v' -F token='086cccd7-c2f2-4606-9c1a-cdbf29dfdb31' "http://localhost:5000/file"

Please save the download link for your file - http://localhost:5000/record?id=d8c2b615-125e-468b-997e-6680c4ec1e1b&user=strokman-7P6Y3s5v



curl 'http://localhost:5000/record?id=d8c2b615-125e-468b-997e-6680c4ec1e1b&user=strokman-7P6Y3s5v' --output kekek.mp3
