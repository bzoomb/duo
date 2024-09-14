import json
import base64
import requests
from datetime import datetime
import argparse
import os

# Set up argument parsing
parser = argparse.ArgumentParser(description="Duolingo XP Gainer")
parser.add_argument("lessons", type=int, help="Number of lessons to complete")
args = parser.parse_args()

# Get the JWT from the environment variables
DUOLINGO_JWT = os.getenv("DUOLINGO_JWT")

# Number of lessons from command-line argument
LESSONS = args.lessons

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DUOLINGO_JWT}",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

try:
    # Decode the JWT to extract the user ID (sub)
    payload = json.loads(base64.b64decode(DUOLINGO_JWT.split(".")[1] + "==").decode('utf-8'))
    sub = payload['sub']

    # Get the fromLanguage and learningLanguage for the user
    user_info_url = f"https://www.duolingo.com/2017-06-30/users/{sub}?fields=fromLanguage,learningLanguage"
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    from_language = user_info['fromLanguage']
    learning_language = user_info['learningLanguage']

    xp = 0

    # Loop through the lessons
    for lesson_num in range(LESSONS):
        # Start a new session
        session_url = "https://www.duolingo.com/2017-06-30/sessions"
        session_payload = {
            "challengeTypes": [
                "assist", "characterIntro", "characterMatch", "characterPuzzle", "characterSelect", "characterTrace",
                "characterWrite", "completeReverseTranslation", "definition", "dialogue", "extendedMatch", 
                "extendedListenMatch", "form", "freeResponse", "gapFill", "judge", "listen", "listenComplete",
                "listenMatch", "match", "name", "listenComprehension", "listenIsolation", "listenSpeak", "listenTap",
                "orderTapComplete", "partialListen", "partialReverseTranslate", "patternTapComplete", "radioBinary",
                "radioImageSelect", "radioListenMatch", "radioListenRecognize", "radioSelect", "readComprehension",
                "reverseAssist", "sameDifferent", "select", "selectPronunciation", "selectTranscription", "svgPuzzle",
                "syllableTap", "syllableListenTap", "speak", "tapCloze", "tapClozeTable", "tapComplete", "tapCompleteTable",
                "tapDescribe", "translate", "transliterate", "transliterationAssist", "typeCloze", "typeClozeTable",
                "typeComplete", "typeCompleteTable", "writeComprehension"
            ],
            "fromLanguage": from_language,
            "isFinalLevel": False,
            "isV2": True,
            "juicy": True,
            "learningLanguage": learning_language,
            "smartTipsVersion": 2,
            "type": "GLOBAL_PRACTICE"
        }
        session_response = requests.post(session_url, headers=headers, json=session_payload)
        session = session_response.json()

        # Update the session
        session_update_url = f"https://www.duolingo.com/2017-06-30/sessions/{session['id']}"
        session_update_payload = {
            **session,
            "heartsLeft": 0,
            "startTime": (datetime.now().timestamp() - 60),
            "enableBonusPoints": False,
            "endTime": datetime.now().timestamp(),
            "failed": False,
            "maxInLessonStreak": 9,
            "shouldLearnThings": True
        }
        update_response = requests.put(session_update_url, headers=headers, json=session_update_payload)
        response = update_response.json()

        # Get the XP gained for this lesson
        lesson_xp = response.get('xpGain', 0)
        xp += lesson_xp

        # Print XP gained for the current lesson
        print(f"Lesson {lesson_num + 1}: 🎉 You gained {lesson_xp} XP")

    # Print total XP at the end
    print(f"Total XP gained: 🎉 {xp} XP")
except Exception as error:
    print("❌ Something went wrong")
    print(str(error))
