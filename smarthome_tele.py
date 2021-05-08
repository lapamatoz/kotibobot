from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import eq3_functions as eq3

#exec("/home/lowpaw/Downloads/kotibobot/eq3_functions.py", globals, locals)

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

def remove_spaces_from_front(text):
  if text == "":
    return text
  while text[0] == " ":
    text = text[1:]
    if text == "":
      return text
  return text
  
def authorize(update, context):
  id = update.message.id
  if id in koodit["lowpaw-teleIDt"]:
    res = "olet inessä"
  else:
    res = "et ole inessä"
  update.message.reply(res)

def start(update, context):
  text = "Hieno botti hermanni" + "\nhttps://github.com/Heckie75/eQ-3-radiator-thermostat"
  return update.message.reply_text(text)

def direct_eq3_command(update, context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = eq3.human_to_machine(str)
  for res in res_array:
    update.message.reply_text(res)

def main():
  # Create Updater object and attach dispatcher to it
  updater = Updater(koodit["kotibobot"])
  dispatcher = updater.dispatcher
  print("Bot started")

  # Add command handler to dispatcher
  start_handler = CommandHandler('start', start)
  eq3_handler = CommandHandler('eq3', direct_eq3_command)
  auth_handler = CommandHandler('authorize', authorize)
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(auth_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()