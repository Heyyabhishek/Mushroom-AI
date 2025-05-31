from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt

# Load language preference
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

# HTML for mic input
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head><title>Speech Recognition</title></head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + ' ';
            }};

            recognition.onerror = function(event) {{
                console.error("Speech recognition error:", event.error);
            }};
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>
'''

# Save the HTML file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# Set the path to HTML
current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/Voice.html".replace("\\", "/")

# Chrome setup
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # keep browser open
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Start Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Prepare status output
TempDirPath = os.path.join(current_dir, "Frontend/Files")
os.makedirs(TempDirPath, exist_ok=True)

def setAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as f:
        f.write(Status)

def QueryModifier(Query):
    query = Query.strip().lower()
    question_words = ["how", "what", "who", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(query.startswith(q) for q in question_words):
        query = query.rstrip(".?!") + "?"
    else:
        query = query.rstrip(".?!") + "."
    return query[0].upper() + query[1:]

def UniversalTranslator(text):
    return mt.translate(text, "en", "auto").capitalize()

def SpeechRecognition():
    driver.get(Link)
    time.sleep(1)
    driver.find_element(By.ID, "start").click()
    print("🎙️ Listening...")

    collected = ""
    for _ in range(30):  # wait ~15s
        try:
            time.sleep(0.5)
            result = driver.find_element(By.ID, "output").text.strip()
            if result and result != collected:
                collected = result
                print(f"📝 Heard: {result}")
        except:
            continue

    driver.find_element(By.ID, "end").click()
    print("🛑 Stopped Listening.")

    if not collected:
        return "I couldn't hear anything."

    if "en" in InputLanguage.lower():
        return QueryModifier(collected)
    else:
        setAssistantStatus("Translating...")
        translated = UniversalTranslator(collected)
        return QueryModifier(translated)

# Run continuously
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print("✅ Final Output:", Text)
