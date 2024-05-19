import requests
import pyttsx3
import pyaudio
import vosk

vosk_model = vosk.Model("vosk-model-ru-0.22")
vosk_wf = vosk.KaldiRecognizer(vosk_model, 16000)

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

commands = ["создать", "имя", "страна", "анкета", "сохранить"]

def create_user():
    try:
        response = requests.get("https://randomuser.me/api/")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        engine.say("Ошибка при запросе к серверу")
        engine.runAndWait()
        return
    data = response.json()
    user = data["results"][0]
    engine.say("Пользователь создан")
    engine.runAndWait()
    save_user_data(user)

def get_name(user):
    name = f"{user['name']['first']} {user['name']['last']}"
    engine.say(f"Ваше имя: {name}")
    engine.runAndWait()

def get_country(user):
    country = user["location"]["country"]
    engine.say(f"Ваша страна: {country}")
    engine.runAndWait()

def create_profile(user):
    info = [
        f"Имя: {user['name']['first']} {user['name']['last']}",
        f"Страна: {user['location']['country']}",
        f"Город: {user['location']['city']}",
        f"Дата рождения: {user['dob']['date']}",
        f"Пол: {user['gender']}"
    ]
    engine.say("Создаю анкету")
    engine.runAndWait()
    engine.say(" ".join(info))
    engine.runAndWait()

def save_photo(user):
    with open("photo.jpg", "wb") as f:
        response = requests.get(user['picture']['large'])
        f.write(response.content)
    engine.say("Фотография сохранена")
    engine.runAndWait()

def save_user_data(user):
    with open("user_data.txt", "w") as f:
        f.write(f"Имя: {user['name']['first']} {user['name']['last']}\n")
        f.write(f"Страна: {user['location']['country']}\n")
        f.write(f"Город: {user['location']['city']}\n")
        f.write(f"Дата рождения: {user['dob']['date']}\n")
        f.write(f"Пол: {user['gender']}\n")

engine.say("Привет, я ваш голосовой ассистент")
engine.runAndWait()

while True:
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    sound_data = []
    while True:
        data = stream.read(8000)
        sound_data.append(data)
        if vosk_wf.AcceptWaveform(data):
            result = vosk_wf.Result()
            if result:
                text = result.text.lower()
                break
        elif vosk_wf.PartialResult():
            result = vosk_wf.PartialResult()
            if result:
                text = result
                break
    stream.stop_stream()
    pa.terminate()

    if text in commands:
        if text == "создать":
            create_user()
        elif text == "имя":
            get_name(user)
        elif text == "страна":
            get_country(user)
        elif text == "анкета":
            create_profile(user)
        elif text == "сохранить":
            save_photo(user)
    else:
        engine.say("Неизвестная команда")
        engine.runAndWait()

    engine.say("Хотите продолжить?")
    engine.runAndWait()
    answer = input("Продолжить (да/нет): ")
    if answer == "нет":
        break

engine.say("До свидания")
engine.runAndWait()
