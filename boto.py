"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request, response
import json
import random
import datetime  # needed for getting the date and time if user asks
import urllib.request  # needed for sending the HTTP request to the openweather API


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
    weather_url = "http://api.openweathermap.org/data/2.5/forecast/city?id=524901&units=metric&APPID=" + WEATHER_APIKEY
    API_info = urllib.request.urlopen(weather_url).read().decode('utf-8')
    weather_data = json.loads(API_info)['list'][0]  # converts to dictionary
    date = weather_data["dt_txt"]
    weather = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    return "The weather prediction for: " + date + " is " + weather + \
           "\nThe temperature is: " + str(temperature) + " degrees"


# cookie storage works as follows: there's no method to iterate over all cookies
# so you have to keep a cookie which keeps the names of all the relevant cookies
# it needs to be converted to a string when saved as a cookie,
# and then converted back to a JSON object when you actually want to use it
# TODO: reset this cookie when cookies are reset
def inject_cookie_memory(msg):
    cookies = request.get_cookie("stored_cookie_keys", [])
    if cookies:
        cookies = json.loads(cookies)["cookies"]
        for key in cookies:
            if "**"+key+"**" in msg:
                msg = msg.replace("**"+key+"**", request.get_cookie(key))
    return msg


def add_to_stored_cookie_keys(key):
    current_cookies = request.get_cookie("stored_cookie_keys", [])
    if current_cookies:  # meaning that this cookie has already been set
        # we want to access the list of relevant cookies
        current_cookies = json.loads(current_cookies)["cookies"]
    if key not in current_cookies:
        current_cookies.append(key)
    response.set_cookie("stored_cookie_keys", json.dumps({"cookies": current_cookies}))
    return None


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
    return "Good question, I don't know the answer, sorry."


def calc_response(user_message):
    user_message = user_message.lower()
    # make punctuation separate from the word, to assist with parsing
    user_message = user_message.replace("?", " ?")
    # convert the string into a list of words to assist with parsing
    words_in_message = user_message.split(" ")
    # check for curse words
    if set(CURSE_WORDS).intersection(words_in_message):
        return "Please do not curse in front of me."
    # check if user wants a joke
    if set(["joke", "jokes"]).intersection(words_in_message):
        return "I have a joke!\n" + funny_jokes[random.randint(0, len(funny_jokes) - 1)]
    if "name" in words_in_message and user_message.endswith("?"):
        return "My name is Boto!"
    if user_message.endswith("?"):
        return parse_question(words_in_message)
    if "name" in words_in_message and "is" in words_in_message[words_in_message.index("name"):]:
        output = ""
        # assume the user name is right after the word "is", only if "is" follows "name"
        # this differentiates between "My name is Liron" and "What is your name?"
        user_name = words_in_message[words_in_message.index("is") + 1]
        response.set_cookie("user_name", user_name)
        add_to_stored_cookie_keys("user_name")
        if request.get_cookie("user_name"):
            output += "Your old username was: " + request.get_cookie("user_name") + ".\n"
        return output + "Welcome " + user_name
    elif user_message.endswith("!"):
        return "You sound excited, please tell me more."
    else:
        return "I'm sorry, I did not understand you."


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    response.headers['Access-Control-Allow-Origin'] = '*'  # added in case other classmates want to use my server
    user_message = request.POST.get('msg')
    boto_response = inject_cookie_memory(calc_response(user_message))
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
