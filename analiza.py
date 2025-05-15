import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.signal import correlate

plt.rcParams.update({
    'axes.facecolor': '#0e1117',  # Background color for the plot area
    'axes.edgecolor': 'white',   # Edge color for the plot area
    'axes.labelcolor': 'white',  # Label color for axes
    'xtick.color': 'white',      # Tick color for x-axis
    'ytick.color': 'white',      # Tick color for y-axis
    'figure.facecolor': '#0e1117',  # Background color for the figure
    'figure.edgecolor': '#0e1117',  # Edge color for the figure
    'text.color': 'white',       # Text color
    'grid.color': 'grey',        # Grid line color
    'grid.alpha': 0.8            # Grid line transparency
})

# Calea către experiment
base_path = 'Dataset'

# Toți subiecții
subjects = sorted([d for d in os.listdir(base_path)
                  if os.path.isdir(os.path.join(base_path, d))])

st.title("🔬 Analiza posturii somnului")

# Selectare subiect și fișier
selected_subject = st.selectbox("Alege experiment: ", subjects)
subject_path = os.path.join(base_path, selected_subject)

# Listăm fișierele .txt
data_files = []
for root, _, files in os.walk(subject_path):
    for file in files:
        if file.endswith('.txt'):
            data_files.append(os.path.join(root, file))

if data_files:
    selected_file = st.selectbox("Alege fisier: ", data_files)

    try:
        data = np.loadtxt(selected_file)
        if len(data.shape) > 1:
            data = data.flatten()

        st.subheader("📊 Semnal brut")
        fig, ax = plt.subplots()
        ax.plot(data, label="Semnal brut", color="cyan", linewidth=1.5)
        ax.set_title("Semnal brut", fontsize=14, fontweight='bold')
        ax.set_xlabel("Timp", fontsize=12)
        ax.set_ylabel("Amplitudine", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc="upper right", fontsize=10)
        ax.axhline(y=np.mean(data), color='red', linestyle='--', label="Media")
        ax.legend()
        st.pyplot(fig)

        # Statistici
        st.write("**Media:**", float(np.mean(data)))
        st.write("**Varianța:**", float(np.var(data)))

        # Autocorelație
        st.subheader("🔁 Autocorelație")
        autocor = correlate(data, data, mode='full') / len(data)
        fig1, ax1 = plt.subplots()
        ax1.plot(autocor, label="Autocorelație", color="magenta", linewidth=1.5)
        ax1.set_title("Autocorelație", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Lag", fontsize=12)
        ax1.set_ylabel("Corelație", fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend(loc="upper right", fontsize=10)
        st.pyplot(fig1)

        # FFT
        st.subheader("📈 Transformata Fourier (FFT)")
        Y = fft(data)
        f = np.fft.fftfreq(len(data), d=1)
        fig2, ax2 = plt.subplots()
        ax2.plot(f[:len(data)//2], np.abs(Y[:len(data)//2]), label="Spectru FFT", color="lime", linewidth=1.5)
        ax2.set_title("Spectru FFT", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Frecvență (Hz)", fontsize=12)
        ax2.set_ylabel("Amplitudine", fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend(loc="upper right", fontsize=10)
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Eroare la citirea fișierului: {e}")
else:
    st.warning("Nu s-au găsit fișiere .txt pentru acest subiect.")

st.markdown(
    """
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" rel="stylesheet">
    <style>
        .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0A0C11;
        color: white;
        text-align: center;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .footer a {
        color: white;
        text-decoration: none;
        margin: 0 10px;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="footer">
        <p>
            <a href="https://github.com/Vladeigthteen" target="_blank">
                <i class="fa-brands fa-github"></i> Vlad Fraticiu
            </a>
            <a href="https://github.com/t0ry003" target="_blank">
                <i class="fa-brands fa-github"></i> Rares Olteanu
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)