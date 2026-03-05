import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
from wordlist import word_list
from emojis import emojis

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

the_word = str(input("wuts da wurd bossss? ")).upper()
if the_word:
    print(f"word set as {the_word}")
else:
    the_word = random.choice(word_list)
    print("word randomly selected")

def log(string: str):
    print(string, end="")
    try:
        with open("log2.txt", "a") as file:
            file.write(string)
    except:
        print("it didnt open")

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready! :D")

class Wordle():
    def __init__(self, author):
        self.author = author
        self.message: str = ""
        self.secret_word = the_word
        self.field: dict = [[" ", " ", " ", " ", " "],
                            [" ", " ", " ", " ", " "],
                            [" ", " ", " ", " ", " "],
                            [" ", " ", " ", " ", " "],
                            [" ", " ", " ", " ", " "],
                            [" ", " ", " ", " ", " "]]
        
    async def startgame(self):
        await self.print_field(self.field, "amogus")
        self.round = 0
        await self.sendmessage("\n\namount of guesses left: 6\nGuess a word:")
    
    async def sendmessage(self, override_message: str):
        if override_message:
            await self.author.send(override_message)
        else:
            await self.author.send(self.message)
            self.message = ""
    
    @staticmethod
    def special_case(word: list, secret_word: str, l: int) -> bool:
        if word[l] is secret_word[l]:
            return False
        apearance_in_given: int = 0
        correct_letters: int = 0
        apearance_in_sec: int = 0
        j: int = 0
        for letter in word:
            if letter is word[l]:
                apearance_in_given += 1
                if letter is secret_word[j]:
                    correct_letters += 1
            if word[l] is secret_word[j]:
                apearance_in_sec += 1
            j += 1
        if apearance_in_given < 2 or apearance_in_given == correct_letters:
            return False
        apearance_in_sec -= correct_letters
        j = 0
        for letter in word:
            if apearance_in_sec < 1:
                return True
            if letter is word[l] and letter is not secret_word[j]:
                apearance_in_sec -= 1
            if j == l:
                return False
            j += 1

    async def print_field(self, field: list, secret_word: str) -> bool:
        correct: int
        word_correct: bool = False
        self.message += "\n"
        for word in field:
            l = 0
            correct = 0
            for letter in word:
                if letter == " ":
                    self.message += ":white_large_square:"
                elif letter in secret_word and self.special_case(word, secret_word, l):
                    self.message += f"<:grey_{letter}:{emojis.get("grey").get(letter)}>"
                elif letter is secret_word[l]:
                    self.message += f"<:green_{letter}:{emojis.get("green").get(letter)}>"
                    correct += 1
                elif letter in secret_word:
                    self.message += f"<:yellow_{letter}:{emojis.get("yellow").get(letter)}>"
                else:
                    self.message += f"<:grey_{letter}:{emojis.get("grey").get(letter)}>"
                l += 1
            self.message += "\n"
            if correct == 5:
                word_correct = True
        await self.sendmessage(None)
        return word_correct

    async def wordle(self, guess: str):
        log(f"player: {self.author} | guess {self.round + 1}: {guess}")
        valid = False
        valid = await self.validity_check(guess, word_list, self.secret_word)
        if not valid:
            await self.sendmessage(f"amount of guesses left: {6 - self.round}")
            await self.sendmessage("Guess a word:")
            log(" (not valid)\n")
            return
        self.field[self.round] = [guess[0], guess[1], guess[2], guess[3], guess[4]]
        if await self.print_field(self.field, self.secret_word):
            await self.sendmessage(f"Correct! the word was '{self.secret_word}'")
            players[str(self.author)] = "already played"
            log(" (winning word)\n" + f"player: {self.author} won the game\n")
            return
        else:
            self.round += 1
            await self.sendmessage(f"amount of guesses left: {6 - self.round}")
            log(" (success)\n")
        if 6 - self.round == 0:
            await self.sendmessage(f"You Lost! No more guesses left! The word was: '{self.secret_word}'")
            players[str(self.author)] = "already played"
            log(f"player: {self.author} lost the game\n")
        else:
            await self.sendmessage("Guess a word:")


    async def validity_check(self, word: str, lst: list, cheat_word: str) -> bool:
        if (word == "gimme the awnser plzzz" or word == "/?") and (str(self.author) == "kleinegeitje"):
            await self.sendmessage(f"you are a dirty cheater... anyway, the word is '{cheat_word}'")
            return False
        if len(word) != 5:
            await self.sendmessage("WORD MUST BE 5 LETTERS")
            return False
        if word not in lst and word != self.secret_word:
            await self.sendmessage("NOT A WORD")
            return False
        return True


players: dict = {}

@bot.command()
async def wordle(ctx):
    if players.get(str(ctx.author)) == "already played":
        await ctx.reply(f"you have already played this session")
        return
    if players.get(str(ctx.author)):
        return
    await ctx.author.send("Starting a game of wordle")
    newgame = Wordle(ctx.author)
    players[str(ctx.author)] = newgame
    await newgame.startgame()
    log(f"{ctx.author} started playing!\n")

# @bot.command()
# async def letter(ctx, *, arg: str):
#     args = arg.split()
#     emoji = f"<:{args[0]}_{args[1]}:{emojis.get(args[0]).get(args[1])}>"
#     await ctx.author.send(emoji)
    

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "Direct" in str(message.channel).split() and "Message" in str(message.channel).split():
        if players.get(str(message.author)) and players.get(str(message.author)) != "already played":
            await players.get(str(message.author)).wordle(str(message.content).upper())
    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
