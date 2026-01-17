import tkinter as tk
from tkinter import ttk
import random

class WordleKeys(tk.Canvas):
    def __init__(self, master):
        tk.Canvas.__init__(self, master, bg="white", highlightthickness=0, width=420, height=170)
        self.master = master
        self.grid(row=3, column=1, sticky=tk.N)

        self.sequences = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        size = 35
        height = 1.3
        buffer = size / 6
        self.coordDic = {}

        BUTTONCOLOR = "#d3d6da"

        for i, seq in enumerate(self.sequences):
            for char in seq:
                x = int(self["width"]) / 2 + (size + buffer) * (seq.find(char) - (len(seq) - 1) / 2)
                y = height * size / 2 + i * (height * size + buffer) + buffer

                self.create_rectangle(
                    int(x - size / 2), int(y - height * size / 2),
                    int(x + size / 2), int(y + height * size / 2),
                    width=0, fill=BUTTONCOLOR, tags=("key_" + char, "letter")
                )
                self.create_text(
                    int(x), int(y), text=char.upper(), font=("Helvetica", 13, "bold"),
                    tags=("letter", "label_" + char.upper())
                )
                self.coordDic["key_" + char] = (x - size / 2, y - height * size / 2, x + size / 2, y + height * size / 2)

        buttonWidth = (3 * size + buffer) / 2
        x, y = (10 * size + 9 * buffer) / 2, height * size / 2 + 2 * (height * size + buffer) + buffer

        # Enter
        self.create_rectangle(
            int(self["width"]) / 2 - x, y - height * size / 2,
            int(self["width"]) / 2 - x + buttonWidth, y + height * size / 2,
            width=0, fill=BUTTONCOLOR, tags=("enter", "key_enter")
        )
        self.create_text(
            int(self["width"]) / 2 - x + buttonWidth / 2, y, text="ENTER", font=("Helvetica", 9, "bold"),
            tags=("enter", "label_enter")
        )

        # Back
        self.create_rectangle(
            int(self["width"]) / 2 + x - buttonWidth, y - height * size / 2,
            int(self["width"]) / 2 + x, y + height * size / 2,
            width=0, fill=BUTTONCOLOR, tags=("back", "key_back")
        )
        self.create_text(
            int(self["width"]) / 2 + x - buttonWidth / 2, y, text="BACK", font=("Helvetica", 9, "bold"),
            tags=("back", "label_back")
        )

        self.tag_bind("letter", "<Button>", self.push_button)
        self.tag_bind("enter", "<Button>", lambda e: self.master.submit())
        self.tag_bind("back", "<Button>", lambda e: self.master.back())

    def push_button(self, key=None):
        for tag, (x0, y0, x1, y1) in self.coordDic.items():
            if x0 <= key.x <= x1 and y0 <= key.y <= y1:
                self.master.type_letter(tag[-1])
                return

class WordleFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="white")
        self.master = master
        self.grid()

        top = 60
        self.canvas = tk.Canvas(self, bg="white", width=370, height=415 + top, highlightthickness=0)
        self.canvas.grid(row=2, column=1)
        self.canvas.create_text(370 / 2, top / 2 - 10, text="Wordle", font=("Helvetica", 30, "italic", "bold"))

        self.keyboard = WordleKeys(self)

        # Spacers
        tk.Canvas(self, bg="white", width=50, height=10, highlightthickness=0).grid(row=1, column=0)
        tk.Canvas(self, bg="white", width=50, height=10, highlightthickness=0).grid(row=1, column=2)
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=0, column=0, columnspan=3, sticky=tk.E + tk.W)

        # words
        with open("words.txt") as f:
            self.words = [word.strip().lower() for word in f]

        self.textField = ""
        self.entered = 0
        self.frozen = False

        # grid
        self.cells = {}
        for x in range(5):
            for y in range(6):
                rect = self.canvas.create_rectangle(
                    x * 68 + 20, y * 68 + top, x * 68 + 80, y * 68 + 60 + top, outline="black"
                )
                text = self.canvas.create_text(
                    x * 68 + 50, y * 68 + 30 + top, text="", font=("Helvetica", 32, "bold")
                )
                self.cells[(x, y)] = text

        # Random word guess
        self.word = random.choice(self.words)

        self.GRAY = "#7c7c7c"
        self.YELLOW = "#c9b458"
        self.GREEN = "#6aaa64"

        # Binds keyboard
        self.bind_all("<BackSpace>", self.back)
        self.bind_all("<Return>", self.submit)
        self.bind_all("<Key>", self.type_letter)

    def back(self, event=None):
        if len(self.textField) == 0:
            return
        self.textField = self.textField[:-1]
        x = len(self.textField)
        y = self.entered
        self.canvas.itemconfigure(self.cells[(x, y)], text="")

    def submit(self, event=None):
        word_guess = self.textField.lower()
        if len(word_guess) != 5 or word_guess not in self.words:
            self.invalid_word_show()
            return
        if self.entered >= 6:
            return

        letterCount = {char: 0 for char in word_guess}
        colored = [False] * 5

        # Green letters
        for i in range(5):
            if word_guess[i] == self.word[i]:
                self.canvas.itemconfigure(self.cells[(i, self.entered)], fill=self.GREEN)
                self.keyboard.itemconfigure(f"key_{word_guess[i]}", fill=self.GREEN)
                letterCount[word_guess[i]] += 1
                colored[i] = True

        # Yellow Gray letters
        for i in range(5):
            char = word_guess[i]
            if not colored[i]:
                if char in self.word and letterCount[char] < self.word.count(char):
                    self.canvas.itemconfigure(self.cells[(i, self.entered)], fill=self.YELLOW)
                    self.keyboard.itemconfigure(f"key_{char}", fill=self.YELLOW)
                    letterCount[char] += 1
                else:
                    self.canvas.itemconfigure(self.cells[(i, self.entered)], fill=self.GRAY)
                    self.keyboard.itemconfigure(f"key_{char}", fill=self.GRAY)

        # Check win/lose
        if word_guess == self.word:
            self.frozen = True
            self.win_display()
        elif self.entered == 5:
            self.lose_display()

        self.entered += 1
        self.textField = ""

    def type_letter(self, event):
        if self.frozen or len(self.textField) >= 5:
            return
        letter = event if isinstance(event, str) else event.char.lower()
        if not letter.isalpha():
            return
        x = len(self.textField)
        y = self.entered
        self.canvas.itemconfigure(self.cells[(x, y)], text=letter.upper())
        self.textField += letter

    def invalid_word_show(self):
        self.canvas.create_rectangle(105, 17, 265, 53, fill="#a00", tags="invalid", width=0)
        self.canvas.create_text(185, 35, text="Invalid word.", font=("Helvetica", 12), fill="white", tags="invalid")
        self.after(1500, self.invalid_word_hide)

    def invalid_word_hide(self):
        self.canvas.delete("invalid")

    def win_display(self):
        x, y = 185, 260
        self.canvas.create_rectangle(x - 150, y - 50, x + 150, y + 50, fill="#fff")
        self.canvas.create_text(x - 140, y - 20,
            text=f"Congratulations! You guessed '{self.word.upper()}' in {self.entered + 1} tries.",
            font=("Helvetica", 12), anchor=tk.W)
        self.button = tk.Button(text="New Wordle", relief=tk.FLAT, font=("Helvetica", 10, "bold"),
                                command=self.restart_game, bg=self.GREEN, fg="white")
        self.canvas.create_window(x, y + 23, window=self.button)

    def lose_display(self):
        x, y = 185, 260
        self.canvas.create_rectangle(x - 150, y - 50, x + 150, y + 50, fill="#fff")
        self.canvas.create_text(x - 140, y - 20,
            text=f"Sorry, you ran out of tries. The word was '{self.word.upper()}'.",
            font=("Helvetica", 12), anchor=tk.W)
        self.button = tk.Button(text="New Wordle", relief=tk.FLAT, font=("Helvetica", 10, "bold"),
                                command=self.restart_game, bg="red", fg="white")
        self.canvas.create_window(x, y + 23, window=self.button)

    def restart_game(self):
        self.grid_remove()
        self.__init__(self.master)


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="white")
    root.title("Wordle")
    WordleFrame(root)
    root.mainloop()
