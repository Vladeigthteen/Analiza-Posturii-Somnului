@echo off
echo Setting up the environment...

REM Check if the virtual environment exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
IF EXIST requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) ELSE (
    echo No requirements.txt file found. Skipping dependency installation.
)

REM Run the Streamlit app
echo Running Streamlit app...
streamlit run analiza.py

REM Keep the terminal open
pause