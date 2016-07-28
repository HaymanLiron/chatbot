"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request, response
import json
import random
import datetime
import urllib.request


WEATHER_APIKEY = "f788fb5757f2400068af4d33c24173df"
CURSE_WORDS = ["fuck", "shit"]


funny_jokes = [
    "What kind of bees make milk? Boobees!",
    "What do you call a cheap circumcision? A rip off.",
    "How did the dentist become a brain surgeon? His hand slipped.",
    "Never trust an atom, they make up everything.",
    "Wanna hear two short jokes and a long joke? Joke joke jooooke.",
    "This dyslexic man walks into a bra.",
    "What’s the best thing about living in Switzerland? I don't know, but the flag is a big plus."
]


def get_weather():
    weather_URL = "http://api.openweathermap.org/data/2.5/forecast/city?id=524901&units=metric&APPID=" + WEATHER_APIKEY
    API_info = urllib.request.urlopen(weather_URL).read().decode('utf-8')
    weather_data = json.loads(API_info)['list'][0]  # converts to dictionary
    date = weather_data["dt_txt"]
    weather = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    return "The weather prediction for: " + date + " is " + weather + \
           "\nThe temperature is: " + str(temperature) + " degrees"


botomem = {"user_name":"gilad","age":36}


def injectMemory(msg):
    for key in botomem:
        if "**"+key+"**" in msg:
            msg = msg.replace(key,botomem.get(key, ""))


def get_time():
    now = datetime.datetime.now()
    return str(now.hour) + ":" + str(now.minute).zfill(2)


def parse_question(words_in_message):
    # function that is called when we know the sentence ends in a question mark
    if "time" in words_in_message:
        return "The time is: " + get_time()
    if "date" in words_in_message:
        now = datetime.datetime.now()
        return "The date is: " + str(now.day) + "/" + str(now.month) + "/" + str(now.year)
    if "weather" in words_in_message:
        return get_weather()


def calc_response(user_message):
    response.set_cookie("name", "gilad")
    user_message = user_message.lower()
    # make punctuation separate from the word, to assist with parsing
    user_message = user_message.replace("?", " ?")
    words_in_message = user_message.split(" ")
    # check for curse words
    if set(CURSE_WORDS).intersection(words_in_message):
        return "Please do not curse in front of me."
    if set(["joke", "jokes"]).intersection(words_in_message):
        return "I have a joke!\n" + funny_jokes[random.randint(0, len(funny_jokes) - 1)]
    if "name" in words_in_message and user_message.endswith("?"):
        return "My name is Boto!"
    if "name" in words_in_message and "is" in words_in_message:
        return "Welcome " + words_in_message[words_in_message.index("is") + 1]
    if user_message.endswith("?"):
        return parse_question(words_in_message)
    elif user_message.endswith("!"):
        return "You sound excited, please tell me more."
    else:
        return "I'm sorry, I did not understand you."


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    boto_response = calc_response(user_message)
    return json.dumps({"animation": "inlove", "msg": boto_response})


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()
