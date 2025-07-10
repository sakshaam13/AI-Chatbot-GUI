import traceback

try:
    import customtkinter as ctk
    import random
    import re
    from PIL import Image, ImageTk
    from datetime import datetime
    from tkinter import messagebox
    import webbrowser
    import time
    import wikipedia
    import requests
    import json
    import os



    # Safe writable location
    APP_DATA_FOLDER = os.path.join(os.path.expanduser("~"), "ChatbotAppData")
    os.makedirs(APP_DATA_FOLDER, exist_ok=True)
    DATA_FILE = os.path.join(APP_DATA_FOLDER, "chatbot_data.json")


    def load_data():
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({"users": [], "history": {}}, f)
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    data = load_data()



    # === AI Logic ===

    # Store context like name, last intent
    chat_context = {
        "username": None,
        "last_intent": None,
        "last_search_url":None,
        "last_search_query": None
    }

    INTENTS = [
         {
            "name": "online_query",
            "keywords": ["what is", "who is", "define", "how to", "where is", "search"],
            "responses": []
        },
        {
            "name": "bye",
            "keywords": ["bye", "goodbye", "see you", "exit"],
            "responses": ["Goodbye!", "Take care!", "See you soon!"]
        },
        {
            "name": "thanks",
            "keywords": ["thanks", "thank you"],
            "responses": ["You're welcome!", "No problem!", "Anytime!"]
        },
        {
            "name": "time",
            "keywords": ["time"],
            "responses": [lambda: f"The time is {datetime.now().strftime('%H:%M:%S')}."]
        },
        {
            "name": "weather",
            "keywords": ["whats the weather", "how's the weather", "weather","weather today"],
            "responses": ["I am a local Chat Bot, I cannot access weather forcast info.", "The weather is hot just like you."]
        },
        {
            "name": "date",
            "keywords": ["date", "day", "today"],
            "responses": [lambda: f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."]
        },
        {
            "name": "how are you",
            "keywords": ["how are you", "are you fine", "whats up","how is all going","are you ok","how are you doing"],
            "responses": ["I'm fine sir.", "Doing great sir.","I'm Aabsolutly fine sir.","Having a wonderful time sir."]
        },
        {
            "name": "identity",
            "keywords": ["who are you", "your name", "what are you"],
            "responses": ["I'm your AI assistant with access to the web!", "Just a helpful chatbot."]
        },
        {
            "name": "name",
            "keywords": ["my name is", "call me", "i am"],
            "responses": []
        },
         {
            "name": "greeting",
            "keywords": ["hello", "hi", "hey"],
            "responses": ["Hello!", "Hi there!", "Hey! How can I help you today?"]
        }
    ]


    def get_bot_response(user_input: str) -> str:
        user_input = user_input.lower().strip()

        # === Special case: user asks for full result
        if user_input == "full" and chat_context.get("last_search_query"):
            try:
                full_content = wikipedia.page(chat_context["last_search_query"]).content
                return full_content[:3000] + "..." if len(full_content) > 3000 else full_content
            except Exception as e:
                return f"Couldn't fetch full content: {e}"

        # === Handle: My name is X
        name_match = re.match(r"(my name is|call me|i am) (\w+)", user_input)
        if name_match:
            name = name_match.group(2).capitalize()
            chat_context["username"] = name
            return f"Nice to meet you, {name}!"

        # === Intent Matching
        for intent in INTENTS:
            if intent["name"] == "name":
                continue

            if any(keyword in user_input for keyword in intent["keywords"]):
                chat_context["last_intent"] = intent["name"]

                if intent["name"] == "online_query":
                    return search_online(user_input)

                if intent["responses"]:
                    response = random.choice(intent["responses"])
                    return response() if callable(response) else response

        # === Fallback
        if any(x in user_input for x in ["what is", "who is", "define", "how to", "search", "where is"]):
            return search_online(user_input)

        return "I'm not sure how to respond to that. Want me to look it up online? (use [search] before your query.)"


    # === Online Search Logic ===
    def search_online(query: str) -> str:
        try:
            chat_context["last_search_query"] = query  # ✅ Save for "full" command
            summary = wikipedia.summary(query, sentences=2)
            page = wikipedia.page(query)
            chat_context["last_search_url"] = page.url
            return f"{summary}\n\n🔗 Read more: {page.url}\n\n(✅Reply with 'full' to see the complete article from wikipedia\nSome content provided by Wikipedia, licensed under CC BY-SA 4.0.)"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Your query is ambiguous. Try one of these:\n- " + "\n- ".join(e.options[:5])
        except wikipedia.exceptions.PageError:
            return "I couldn't find anything on Wikipedia for that topic."
        except Exception as e:
            return f"Error: {str(e)}"


    # === Splash screen Window ===
    class SplashScreen(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("")
            self.geometry("400x300")
            self.overrideredirect(True)  # Hide window controls
            self.configure(fg_color="#eeeeee")

            try:
                self.iconbitmap("chat_icon.ico")
            except:
                pass

            image = Image.open("icon.png")
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
            image_label = ctk.CTkLabel(self, image=photo, text="")
            image_label.pack(pady=10)

            
            label = ctk.CTkLabel(self, text="Welcome to ChatBot!", font=("Segoe UI", 20), text_color="black")
            label.pack(expand=True)

            self.eval('tk::PlaceWindow . center')

            self.after(2500, self.start_main_app)  # Show for 2.5 seconds

        def start_main_app(self):
            self.destroy()
            self.after(100, lambda: LoginWindow().mainloop())



    # === Login/Register Window ===
    class LoginWindow(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Login")
            self.geometry("400x350")
            ctk.set_appearance_mode("Dark")
            self.iconbitmap("chat_icon.ico")

            self.attribution_label = ctk.CTkLabel(self, text="*Powered by Chatbot by Saksham Rao Chaturvedi", font=("Segoe UI", 12))
            self.attribution_label.place(x=10, y=300)
                    
            self.label = ctk.CTkLabel(self, text="Login to Chatbot", font=("Segoe UI", 20))
            self.label.pack(pady=30)

            self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
            self.username_entry.pack(pady=10)

            self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
            self.password_entry.pack(pady=10)

            self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
            self.login_button.pack(pady=10)

            self.register_button = ctk.CTkButton(self, text="Register", command=self.register)
            self.register_button.pack(pady=5)

            self.eval('tk::PlaceWindow . center')

        def login(self):
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            for user in data["users"]:
                if user["username"] == username and user["password"] == password:
                    self.withdraw()
                    ChatbotApp(username=username)
                    self.destroy()
                    return

            messagebox.showerror("Login Failed", "Incorrect username or password")


        def register(self):
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()

            if any(user["username"] == username for user in data["users"]):
                messagebox.showerror("Error", "Username already exists")
                return
            if username != '' and password != '' and  len(password)>=8:
                data["users"].append({
                    "username": username,
                    "password": password,
                    "theme": "dark"
                })
                save_data(data)
                messagebox.showinfo("Success", "Account created. Please login.")
            else:
                messagebox.showerror("Registration Failed", "password must be atleast 8 characters big\n(no field should be empty)")
            data["history"][username] = []
            



    # === Chatbot Application ===
    class ChatbotApp(ctk.CTk):
        def __init__(self, username):
            super().__init__()
            self.username = username

            self.title(f"Chatbot - Logged in as {username}")
            self.geometry("600x650")
            self.iconbitmap("chat_icon.ico")
            ctk.set_appearance_mode("System")
            ctk.set_default_color_theme("blue")

            # Fetch theme preference from DB
            user_theme = next(user["theme"] for user in data["users"] if user["username"] == self.username)
            ctk.set_appearance_mode(user_theme.capitalize())

            # Top utility bar (for About button)
            self.topbar = ctk.CTkFrame(self)
            self.topbar.pack(fill="x", pady=(5, 0), padx=5, anchor="nw")

            self.about_button = ctk.CTkButton(self.topbar, text="ℹ", command=self.show_about, width=15)
            self.about_button.pack(side="left", padx=5, pady=5)

            # Chat display
            self.chat_display = ctk.CTkTextbox(self, width=580, height=480, font=("Segoe UI", 14))
            self.chat_display.pack(pady=10, padx=10, expand=True, fill="y")
            self.chat_display.configure(state="disabled")

            # Input frame
            self.input_frame = ctk.CTkFrame(self)
            self.input_frame.pack(padx=10, pady=10)

            self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...", width=400)
            self.user_input.pack(side="left", padx=(0, 10), expand=False, fill="x")

            self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
            self.send_button.pack(side="right")

            # Button Frame
            self.button_frame = ctk.CTkFrame(self)
            self.button_frame.pack(pady=5)

            self.clear_button = ctk.CTkButton(self.button_frame, text="🗑 Clear History", fg_color="black", command=self.clear_chat)
            self.clear_button.pack(side = "left", padx=5)

            self.logout_button = ctk.CTkButton(self.button_frame, text="🔒 Logout", fg_color="black", command=self.logout)
            self.logout_button.pack(side = "left", padx=5)

            self.delete_button = ctk.CTkButton(self.button_frame, text="❌ Delete Account", fg_color="black", command=self.delete_account)
            self.delete_button.pack(side="left", padx=5)

            # Theme switch
            self.theme_switch = ctk.CTkSwitch(self.button_frame, text=f"{user_theme.capitalize()} Mode", command=self.toggle_theme)
            self.theme_switch.pack(side="left", padx=5)


            # Set the toggle position
            if user_theme == "dark":
                self.theme_switch.select()
            else:
                self.theme_switch.deselect()

            self.bind('<Return>', lambda event: self.send_message())

            self.load_chat_history()
            self.mainloop()

        def load_chat_history(self):
            history = data["history"].get(self.username, [])
            self.chat_display.configure(state="normal")
            for sender, message in history:
                self.chat_display.insert("end", f"{sender}: {message}\n\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")


        def toggle_theme(self):
            new_theme = "dark" if self.theme_switch.get() == 1 else "light"
            ctk.set_appearance_mode(new_theme.capitalize())
            self.theme_switch.configure(text=f"{new_theme.capitalize()} Mode")

            for user in data["users"]:
                if user["username"] == self.username:
                    user["theme"] = new_theme
                    break
            save_data(data)


        def send_message(self):
            user_text = self.user_input.get().strip()
            if not user_text:
                return

            self.append_message("You", user_text)
            self.save_message("You", user_text)

            bot_response = get_bot_response(user_text)
            self.append_message("Bot", bot_response)
            self.save_message("Bot", bot_response)

            # 🔗 Ask user to open full article (if it was an online search)
            if chat_context.get("last_search_url"):
                if messagebox.askyesno("Open Full Result", "Do you want to open the full article in your browser?"):
                    webbrowser.open(chat_context["last_search_url"])
                chat_context["last_search_url"] = None  # Clear after use

            self.user_input.delete(0, 'end')


        def append_message(self, sender, message):
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"{sender}: {message}\n\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")

        def save_message(self, sender, message):
            data["history"].setdefault(self.username, []).append((sender, message))
            save_data(data)


        def clear_chat(self):
            confirm = messagebox.askyesno("Clear History", "Are you sure?")
            if confirm:
                data["history"][self.username] = []
                save_data(data)
                self.chat_display.configure(state="normal")
                self.chat_display.delete("1.0", "end")
                self.chat_display.configure(state="disabled")
                messagebox.showinfo("Success", "Chat history cleared.")


        def logout(self):
            confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
            if confirm:
                self.destroy()
                self.after(100, lambda: LoginWindow().mainloop())

        def delete_account(self):
            confirm = messagebox.askyesno("Delete Account", "Are you sure?")
            if confirm:
                data["users"] = [u for u in data["users"] if u["username"] != self.username]
                data["history"].pop(self.username, None)
                save_data(data)
                messagebox.showinfo("Deleted", "Your account has been deleted.")
                self.destroy()
                self.after(100, lambda: LoginWindow().mainloop())

        def show_about(self):
            legal_text = (
                "🤖 Chatbot Assistant\n"
                "Version: 1.0\n"
                "Author: Saksham Rao Chaturvedi\n\n"
                "📜 This app uses open-source libraries:\n"
                "- customtkinter (MIT License)\n"
                "- wikipedia (MIT License)\n"
                "- Pillow (HPND License)\n"
                "- pywebview (BSD License)\n\n"
                "📚 Some content is sourced from Wikipedia.org\n"
                "and is licensed under CC BY-SA 4.0\n"
                "(https://creativecommons.org/licenses/by-sa/4.0/)\n\n"
                "This app is provided as-is, with no warranty."
            )
            messagebox.showinfo("About & Legal Notice", legal_text)


    import traceback

    if __name__ == "__main__":
        try:
            splash = SplashScreen()
            splash.mainloop()
        except Exception as e:
            with open("error_log.txt", "w") as f:
                f.write(traceback.format_exc())
            raise


except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(traceback.format_exc())

