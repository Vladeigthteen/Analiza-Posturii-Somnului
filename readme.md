# 🔬 Analiza Posturii Somnului

This project is a Streamlit-based application for analyzing sleep posture data. It processes `.txt` files containing experimental data, visualizes the raw signals, computes statistics, and performs advanced analyses like autocorrelation and Fourier Transform.

---

## 🚀 How to Run the App Automatically

### Prerequisites
- **Python 3.8 or higher** installed on your system.
- **No manual setup required**—the `run.bat` file will handle everything for you.

### Steps to Run the App
1. **Download or Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Analiza-Posturii-Somnului.git
   cd Analiza-Posturii-Somnului

2. **Run the App Automatically**:

    Simply double-click the `run.bat` file located in the project directory.  
    The script will:
    1. Create a virtual environment (`venv`) if it doesn't already exist.
    2. Install the required dependencies from `requirements.txt`.
    3. Launch the Streamlit app in your default web browser.

3. **What Happens in the Background**:

    The `run.bat` file automates the following steps:
    1. Checks if a virtual environment exists. If not, it creates one.
    2. Activates the virtual environment.
    3. Installs all required Python packages listed in `requirements.txt`.
    4. Runs the Streamlit app (`analiza.py`).

---

## 📝 Notes:
- Ensure that the `Dataset` folder contains subfolders with `.txt` files for the app to work.
- If you encounter any issues, check the terminal output for error messages.
- If you prefer manual setup, refer to the `README.md` in the repository for detailed instructions.