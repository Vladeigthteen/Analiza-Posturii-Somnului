import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.signal import correlate

# Calea către experiment
base_path = 'Dataset'

# Toți subiecții
subjects = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])

st.title("🔬 Analiza posturii somnului - Experiment I")

# Selectare subiect și fișier
selected_subject = st.selectbox("Alege subiect", subjects)
subject_path = os.path.join(base_path, selected_subject)

# Listăm fișierele .txt
data_files = []
for root, _, files in os.walk(subject_path):
    for file in files:
        if file.endswith('.txt'):
            data_files.append(os.path.join(root, file))

if data_files:
    selected_file = st.selectbox("Alege fișier", data_files)
    
    try:
        data = np.loadtxt(selected_file)
        if len(data.shape) > 1:
            data = data.flatten()

        st.subheader("📊 Semnal brut")
        st.line_chart(data)

        # Statistici
        st.write("**Media:**", float(np.mean(data)))
        st.write("**Varianța:**", float(np.var(data)))

        # Autocorelație
        st.subheader("🔁 Autocorelație")
        autocor = correlate(data, data, mode='full') / len(data)
        fig1, ax1 = plt.subplots()
        ax1.plot(autocor)
        ax1.set_title("Autocorelație")
        st.pyplot(fig1)

        # FFT
        st.subheader("📈 Transformata Fourier (FFT)")
        Y = fft(data)
        f = np.fft.fftfreq(len(data), d=1)
        fig2, ax2 = plt.subplots()
        ax2.plot(f[:len(data)//2], np.abs(Y[:len(data)//2]))
        ax2.set_title("Spectru FFT")
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Eroare la citirea fișierului: {e}")
else:
    st.warning("Nu s-au găsit fișiere .txt pentru acest subiect.")
