import os
import sys

Reset = "\033[0m"
Red = "\033[31m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
Purple = "\033[35m"
Cyan = "\033[36m"
Orange = "\033[33m"
Gray = "\033[37m"
White = "\033[97m"

i = 1

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TARGET_DIR = CURRENT_DIR
SERVICE_FILE_ADDR = "/etc/systemd/system/explorer.service"


def print_started_action(started_text: str):
    global i
    print(f"\n{i} {Green}==={Reset} {Blue}{started_text}{Reset} {Green}==={Reset}")
    i += 1


def print_failed_action(failed_text: str):
    print(f"{Orange}==={Reset} {Red}{failed_text}{Reset} {Orange}==={Reset}")
    print(
        f"\n{Orange}==={Reset} {Red}Whole Installation Process Failed{Reset} {Orange}==={Reset}"
    )
    sys.exit(1)


def print_final_success_print():
    print(f"\n{Green}=== Installation finished successfully ==={Reset}")
    print(
        f"\n{White}Start Service: \t\t{Green}systemctl start explorer.service{Reset}"
    )
    print(
        f"{White}Restart Service: \t{White}systemctl restart explorer.service{Reset}"
    )
    print(f"{White}Stop Service: \t\t{Red}systemctl stop explorer.service{Reset}")
    print(
        f"{White}Check Service Status: \t{Yellow}systemctl status explorer.service{Reset}"
    )


def main():
    if os.geteuid() != 0: # type: ignore
        print_failed_action("We need root access, run with 'sudo' please")

    print_started_action("Create Virtual Environment")
    if os.system("python3 -m venv env") != 0:
        print_failed_action("Failed to Create env folder")

    print_started_action("Install Requirements")
    if (
        os.system(
            f"{CURRENT_DIR}/env/bin/pip install -r {CURRENT_DIR}/requirements.txt"
        )
        != 0
    ):
        print_failed_action("Failed to Install Requirements")

    print_started_action("Create The Service")
    content = ""
    with open("service.service", "r") as file:
        lines = file.readlines()
        for line in lines:
            content += line
        content = content.replace("DESC", "explorer")
        content = content.replace("PYTHONDIR", f"{TARGET_DIR}/env/bin/python")
        content = content.replace("EXECDIR", f"{TARGET_DIR}/main.py")
        content = content.replace("DIR", TARGET_DIR)

    # Create SERVICE_FILE_ADDR from the content variable
    if not os.path.exists(SERVICE_FILE_ADDR):
        with open(SERVICE_FILE_ADDR, "w") as file:
            file.write(content)
    else:
        os.remove(SERVICE_FILE_ADDR)
        with open(SERVICE_FILE_ADDR, "w") as file:
            file.write(content)

    print_started_action("Start And Activate The Service")
    os.system("systemctl daemon-reload")
    os.system("systemctl enable explorer.service")
    os.system("systemctl start explorer.service")

    print_final_success_print()


if __name__ == "__main__":
    main()
