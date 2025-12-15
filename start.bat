@echo off
setlocal enabledelayedexpansion

if exist src\config.py (
    echo Config file found, starting the bot...
) else (
    echo Config file not found, please enter required info.

    :: Ask for Bot Token
    set /p token=Please enter your Discord Bot Token: 

    :: Ask for Log Channel ID
    set /p logid=Please enter your Log Channel ID: 

    :: Create src folder if it doesn't exist
    if not exist src (
        mkdir src
    )

    :: Write the config.py inside src folder
    (
    echo TOKEN = "!token!"
    echo LOG_CHANNEL_ID = !logid!
    ) > src\config.py

    echo.
    echo Config file created inside src folder with your inputs.
)

echo Starting the bot...

:: Run the bot (adjust if needed)
python src\bot.py

pause