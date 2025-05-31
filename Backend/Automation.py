from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not os.path.exists("Data"):
    os.makedirs("Data")

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
client = Groq(api_key=GroqAPIKey)
messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'AI Assistant')}, You're a content writer. You have to write content like letter"}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def content(Topic):
    def OpenNotepad(File):
        try:
            subprocess.Popen(['notepad.exe', File])
        except Exception as e:
            print(f"[red]Failed to open notepad:[/red] {e}")

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    if not os.path.exists("Data"):
        os.makedirs("Data")

    file_path = os.path.abspath(f"Data/{Topic.lower().replace(' ', '')}.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    print(f"File saved at: {file_path}, size: {os.path.getsize(file_path)} bytes")
    OpenNotepad(file_path)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        
        try:
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception as local_error:
            print(f"[yellow]Local app open failed:[/yellow] {local_error}")

        app_clean = app.lower().replace(" ", "")
        guessed_url = f"https://www.{app_clean}.com"
        try:
            response = sess.get(guessed_url, headers={"User-Agent": useragent}, timeout=5)
            if response.status_code == 200:
                webopen(guessed_url)
                return True
        except:
            pass  

        def search_google(query):
            url = f"https://www.google.com/search?q={query}+official+site"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers, timeout=5)
            return response.text if response.status_code == 200 else None

        def extract_links(html):
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            for a in soup.select('a[href^="http"]'):
                href = a['href']
                if "google.com" in href or "webcache" in href or "support.google.com" in href:
                    continue
                if "url?q=" in href:
                    clean_link = href.split("url?q=")[-1].split("&")[0]
                    links.append(clean_link)
                elif "https://" in href:
                    links.append(href)
            return links

        html = search_google(app)
        links = extract_links(html)

        if links:
            webopen(links[0])
            return True
        else:
            print(f"[red]No valid links found for:[/red] {app}")
            return False

    except Exception as e:
        print(f"[red]Error opening app:[/red] {e}")
        return False

OpenApp("jio hotstar")

def CloseApp(app):
    try:
        if "chrome" in app:
            pass
        else:
            close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Error closing app:[/red] {e}")
        return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")
    def unmute():
        keyboard.press_and_release("volume unmute")
    def volume_up():
        keyboard.press_and_release("volume up")
    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        cmd = command.lower().strip()

        if cmd.startswith("open "):
            app_name = cmd.removeprefix("open ")
            fun = asyncio.to_thread(OpenApp, app_name)
            funcs.append(fun)

        elif cmd.startswith("close "):
            app_name = cmd.removeprefix("close ")
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)

        elif cmd.startswith("play "):
            query = cmd.removeprefix("play ")
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)

        elif cmd.startswith("content "):
            topic = cmd.removeprefix("content ")
            fun = asyncio.to_thread(content, topic)
            funcs.append(fun)

        elif cmd.startswith("google search "):
            topic = cmd.removeprefix("google search ")
            fun = asyncio.to_thread(GoogleSearch, topic)
            funcs.append(fun)

        elif cmd.startswith("youtube search "):
            topic = cmd.removeprefix("youtube search ")
            fun = asyncio.to_thread(YouTubeSearch, topic)
            funcs.append(fun)

        elif cmd.startswith("system "):
            sys_cmd = cmd.removeprefix("system ")
            fun = asyncio.to_thread(System, sys_cmd)
            funcs.append(fun)

        else:
            print(f"[red]No Function Found for:[/red] {command}")

    results = await asyncio.gather(*funcs)
    return results
