import os
import sys
import json
import requests

from to_room import XMPPBot

LIST_TRANSLATIONS_URL = "https://translate.yunohost.org/api/translations/"


def get_all_translations():
    result = []

    from_api = requests.get(LIST_TRANSLATIONS_URL).json()
    result += from_api["results"]

    while from_api["next"]:
        from_api = requests.get(from_api["next"]).json()
        result += from_api["results"]

    return result


def main():
    if not os.path.exists("password"):
        print "I need the xmpp bot password in a file called 'password'"
        sys.exit(1)

    password = open("password").read().strip()

    if os.path.exists("db.json"):
        db = json.load(open("db.json"))
    else:
        db = {}

    with XMPPBot(password) as bot:
        for i in get_all_translations():
            component = i["component"]["name"]
            if component not in db:
                db[component] = {}

            language = i["language_code"]
            if language not in db[component]:
                db[component][language] = {
                    "translated_percent": i["translated_percent"]
                }
            elif db[component][language]["translated_percent"] != i["translated_percent"]:
                old_percent = db[component][language]["translated_percent"]
                bot.sendToChatRoom("[%s] translation %s %s%% -> %s%%" % (language, component, old_percent, i["translated_percent"]))
                db[component][language]["translated_percent"] = i["translated_percent"]

    json.dump(db, open("db.json", "w"), indent=4)


if __name__ == '__main__':
    main()
