# VacancyStats

This tool allows to automatically collect and view vacancy statistics from headhunter and superjob.

## How to install

### Requirements 

Python3 should already be installed. 
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Environment variables

Superjob developer token is required to use this tool.

After gaining access to the token, you must create a new file called **tokens.env** in the project folder, and store the token inside of it as `SJ_ACCESS_TOKEN`.

## How to use

Run `main.py` in the terminal.