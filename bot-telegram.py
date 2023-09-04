import telebot
from telebot import types
import random
import matplotlib.pyplot as plt
from io import BytesIO

name_event = None
participant_numbers = 1
Max_participants = 10
name_game = None
Max_points = 1
player_name = None
points = 1
chat_id = None
gstatus = None
ev_status = None

messages = [
    "Je n'ai pas compris ce que vous voulez dire.",
    "Pouvez-vous reformuler votre demande ?",
    "Je suis désolé, je ne comprends pas.",
    "Je ne sais pas comment vous aider.",
    "Je n'arrive pas à comprendre ce que vous voulez dire.",
]

bot = telebot.TeleBot("AAFAPmWaytjJjPM-LTjuHDtxF8k0ND9NRYQ")
counter = {}

users = {"player_name": player_name, "scores": points}
game = {
    "game_name": name_game,
    "participant_numbers": participant_numbers,
    "Max_participants": Max_participants,
    "points_max": Max_points,
}
games = [game]
events = {
    "name_event": name_event,
    "participant_numbers": participant_numbers,
    "Max_participants": Max_participants,
    "games": games,
    "IDDECHAT": chat_id,
    "players": users,
}


# Here you can define your command handlers and message handlers
# For example:


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Bonjour, je suis votre bot Organisateur. \n Les Commandes disponibles sont: \n -/creer un évènement et ses participants ( jeu inclus) \n -/ajouter une activité ou jeu secondaire \n -/inclure un participant \n -/arreter le jeu secondaire \n -/stopper l'activité principale \n /donner des points, \n /afficher le resultat du jeu \n /tutoriel ",
    )
    bot.send_message(message.chat.id, "Entrez le nom de votre activité:")


# -------------------------------------------------------- la c'est mon message acceuillant--------------------------------------------------------#


@bot.message_handler(commands=["creer"])
def create_event(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is an admin of the group
    chat_member = bot.get_chat_member(chat_id, user_id)
    if not chat_member.status == "administrator":
        bot.send_message(
            chat_id, "Vous n'avez pas les droits d'accéder à cette commande."
        )
        return

    # Get the event name from the command
    args = message.text.split()[1:]
    if len(args) < 1:
        bot.send_message(chat_id, "Usage: /creer <nom de l'événement>")
        return
    name_event = args[0]

    # Check if the event already exists
    if not events.get(chat_id):
        events[chat_id] = {}
    if events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} existe déjà.")
        return

    # Ask for the maximum number of participants for the event
    msg = bot.send_message(
        chat_id, "Combien de participants maximum peut accueillir cet événement ?"
    )
    bot.register_next_step_handler(msg, get_max_participants, name_event=name_event)


# -------------------------------------------------------- la commande creer evenement faite------------------------------------------------------------#
def get_max_participants(message, name_event):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Get the maximum number of participants from the user input
    try:
        Max_participants = int(message.text)
    except ValueError:
        bot.send_message(chat_id, "Veuillez entrer un nombre valide.")
        return

    # Check if the event already exists
    if not events.get(chat_id):
        events[chat_id] = {}
    if events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} existe déjà.")
        return

    # Create a new event dictionary
    event = {}
    event["name_event"] = name_event
    event["participant_numbers"] = 0
    event["Max_participants"] = Max_participants
    event["games"] = {}
    event["IDDECHAT"] = chat_id

    # Add the new event to the events dictionary for this group
    events[chat_id][name_event] = event

    # Confirm that the event was created successfully
    bot.send_message(chat_id, f"L'événement {name_event} a été créé avec succès.")


# -------------------------------------------------------- la commande de limite maximale de joueur evenement faite------------------------------------------------------------#


@bot.message_handler(func=lambda message: True)
def pas_compris(message):
    if message.from_user.id not in counter:
        message_text = random.choice(messages)
        bot.send_message(message.chat.id, message_text)
        counter[message.from_user.id] = {"message": message_text, "count": 1}
    else:
        counter[message.from_user.id]["count"] += 1
    if counter[message.from_user.id]["count"] == 5:
        message_text = "en depit de votre manque de communication je ne puis vous aider plus que cela adieux, cretin"
        bot.send_message(message.chat.id, message_text)
    else:
        message_text = random.choice(
            [m for m in messages if m != counter[message.from_user.id]["message"]]
        )
        bot.send_message(message.chat.id, message_text)
        counter[message.from_user.id] = message_text


@bot.message_handler(commands=["ajouter"])
def add_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is an admin of the group
    chat_member = bot.get_chat_member(chat_id, user_id)
    if not chat_member.status == "administrator":
        bot.send_message(
            chat_id, "Vous n'avez pas les droits d'accéder à cette commande."
        )
        return

    # Get the event name and game name from the command
    args = message.text.split()[1:]
    if len(args) < 2:
        bot.send_message(chat_id, "Usage: /add_game <nom de l'événement> <nom du jeu>")
        return
    name_event = args[0]
    name_game = args[1]

    # Check if the event exists
    if not events.get(chat_id) or not events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_game} n'existe pas.")
        return

    # Check if the game already exists
    if events[chat_id][name_event].get("games") and events[chat_id][name_event][
        "games"
    ].get(name_game):
        bot.send_message(
            chat_id, f"Le jeu {name_game} existe déjà dans l'événement {name_event}."
        )
        return

    # Get the max points for the game
    msg = bot.send_message(
        chat_id, f"Quel est le nombre maximum de points pour le jeu {name_game} ?"
    )
    bot.register_next_step_handler(
        msg, get_Max_points_add_game, name_event=name_event, name_game=name_game
    )


def get_Max_points_add_game(message, name_event, name_game):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Get the max points for the game from the user input
    try:
        Max_points = int(message.text)
    except ValueError:
        bot.send_message(chat_id, "Veuillez entrer un nombre valide.")
        return

    # Add the new game to the event dictionary
    if not events[chat_id][name_event].get("games"):
        events[chat_id][name_event]["games"] = {}
    events[chat_id][name_event]["games"][name_game] = {"points_max": Max_points}

    # Confirm that the game was added successfully
    bot.send_message(
        chat_id,
        f"Le jeu {name_game} a été ajouté à l'événement {name_event} avec succès.",
    )


@bot.message_handler(commands=["inclure"])
def add_player(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Get the event name, game name, and player name from the command
    args = message.text.split()[1:]
    if len(args) < 3:
        bot.send_message(
            chat_id,
            "Usage: /add_player <nom de l'événement> <nom du jeu> <nom du joueur>",
        )
        return
    name_event = args[0]
    name_game = args[1]
    player_name = args[2]

    # Check if the event exists
    if not events.get(chat_id) or not events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} n'existe pas.")
        return

    # Check if the game exists
    if not events[chat_id][name_event].get("games") or not events[chat_id][name_event][
        "games"
    ].get(name_game):
        bot.send_message(
            chat_id, f"Le jeu {name_game} n'existe pas dans l'événement {name_event}."
        )
        return

    # Check if the player already exists in the game
    if (
        events[chat_id][name_event]["games"][name_game].get("players")
        and player_name in events[chat_id][name_event]["games"][name_game]["players"]
    ):
        bot.send_message(
            chat_id,
            f"Le joueur {player_name} est déjà inscrit dans le jeu {name_game}.",
        )
        return

    # Add the player to the game
    if not events[chat_id][name_event]["games"][name_game].get("players"):
        events[chat_id][name_event]["games"][name_game]["players"] = []
    events[chat_id][name_event]["games"][name_game]["players"].append(player_name)

    # Reply with success message
    bot.send_message(
        chat_id,
        f"Le joueur {player_name} a été ajouté au jeu {name_game} de l'événement {name_event}.",
    )


# -------------------------------------------------------- fonction pour ajouter un joueur -------------------------------------------------------#
@bot.message_handler(commands=["donner"])
def add_points(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    args = message.text.split()[1:]
    if len(args) < 4:
        bot.send_message(
            chat_id,
            "Usage: /add_points <nom de l'événement> <nom du jeu> <nom du joueur> <nombre de points>",
        )
        return
    name_event = args[0]
    name_game = args[1]
    player_name = args[2]
    points = int(args[3])

    if not events.get(chat_id) or not events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} n'existe pas.")
        return

    if not events[chat_id][name_event].get("games") or not events[chat_id][name_event][
        "games"
    ].get(name_game):
        bot.send_message(
            chat_id, f"Le jeu {name_game} n'existe pas dans l'événement {name_game}."
        )
        return

    if (
        not events[chat_id][name_event]["games"][name_game].get("players")
        or player_name not in events[chat_id][name_event]["games"][name_game]["players"]
    ):
        bot.send_message(
            chat_id,
            f"Le joueur {player_name} n'existe pas dans le jeu {name_game} de l'événement {name_event}.",
        )
        return

    if not events[chat_id][name_event]["games"][name_game].get("scores"):
        events[chat_id][name_event]["games"][name_game]["scores"] = {}
    if not events[chat_id][name_event]["games"][name_game]["scores"].get(player_name):
        events[chat_id][name_event]["games"][name_game]["scores"][player_name] = 0
    events[chat_id][name_event]["games"][name_game]["scores"][player_name] += points

    bot.send_message(
        chat_id,
        f"{points} points ont été ajoutés au score de {player_name} dans le jeu {name_game} de l'événement {name_event}.",
    )


@bot.message_handler(commands=["arreter"])
def stop_game(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    args = message.text.split()[1:]
    if len(args) < 2:
        bot.send_message(chat_id, "Usage: /stop_game <nom de l'événement> <nom du jeu>")
        return
    name_event = args[0]
    name_game = args[1]

    if not events.get(chat_id) or not events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} n'existe pas.")
        return

    if not events[chat_id][name_event].get("games") or not events[chat_id][name_event][
        "games"
    ].get(name_game):
        bot.send_message(
            chat_id, f"Le jeu {name_game} n'existe pas dans l'événement {name_event}."
        )
        return

    del events[chat_id][name_event]["games"][name_game]
    bot.send_message(
        chat_id, f"Le jeu {name_game} a été supprimé de l'événement {name_event}."
    )


@bot.message_handler(commands=["stopper"])
def stop_event(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    args = message.text.split()[1:]
    if len(args) < 1:
        bot.send_message(chat_id, "Usage: /stop_event <nom de l'événement>")
        return
    name_event = args[0]

    if not events.get(chat_id) or not events[chat_id].get(name_event):
        bot.send_message(chat_id, f"L'événement {name_event} n'existe pas.")
        return

    del events[chat_id][name_event]
    bot.send_message(chat_id, f"l'événement {name_event} a été supprimé.")


def get_name_event_from_message(message):
    # Extract the name of the event from the message text
    name_event = message.text.split()[1]
    return name_event


def get_name_game_from_message(message):
    # Extract the name of the event from the message text
    name_game = message.text.split()[1]
    return name_game


def get_player_name_from_message(message):
    # Extract the name of the event from the message text
    player_name = message.text.split()[1]
    return player_name


def auto_delete_game(message):
    chat_id = message.chat.id
    name_event = get_name_event_from_message(message)
    name_game = get_name_game_from_message(message)
    player_name = get_player_name_from_message(message)

    # Check if the player has reached the maximum number of points
    max_points = get_Max_points_add_game(chat_id, name_event, name_game)
    if (
        events[chat_id][name_event]["games"][name_game]["players"][name_game]
        >= max_points
    ):
        # Delete the game
        del events[chat_id][name_event]["games"][name_game]
        bot.reply_to(
            message,
            f"Le joueur {player_name} a atteint la limite de points et le jeu {name_game} a été supprimé.",
        )
    else:
        bot.reply_to(
            message,
            f"Le joueur {player_name} a maintenant {events[chat_id][name_event]['games'][name_game]['players'][player_name]} points dans le jeu {name_event}.",
        )


def see_result(message):
    chat_id = message.chat.id
    name_event = get_name_event_from_message(message)
    name_game = get_name_game_from_message(message)

    # Check if the game exists
    if not events[chat_id][name_event]["games"].get(name_game):
        return []

    # Get the maximum number of points
    max_points = get_Max_points_add_game(chat_id, name_event, name_game)

    # Get the results for each player
    results = []
    for player in events[chat_id][name_event]["games"][name_game]["players"]:
        points = events[chat_id][name_event]["games"][name_game]["players"][player]
        result = (player, points)
        results.append(result)

    # Sort the results by score
    results.sort(key=lambda x: x[1], reverse=True)

    # Add a message for the winner
    if results and results[0][1] >= max_points:
        winner = results[0][0]
        results.insert(
            0,
            (
                f"👑 {winner}",
                events[chat_id][name_event]["games"][name_game]["players"][winner],
            ),
        )

    # Create the bar chart
    fig, ax = plt.subplots()
    y_pos = range(len(results))
    scores = [result[1] for result in results]
    labels = [result[0] for result in results]
    ax.barh(y_pos, scores)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Score")
    ax.set_title(f"Résultats pour {name_game}")

    # Save the bar chart to a BytesIO object
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    # Construct the message with the bar chart and the results
    message = f"Résultats pour {name_game} :\n"
    for i, result in enumerate(results):
        message += f"{i+1}. {result[0]} : {result[1]} points\n"
    message += "\n"

    bot.send_photo(chat_id, photo=buffer, caption=message)


bot.polling()
