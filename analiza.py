import os
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.fft import fft
from scipy.signal import correlate
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


# ======== UI & Stilizare ========
plt.rcParams.update({
    'axes.facecolor': '#0e1117',
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'figure.facecolor': '#0e1117',
    'figure.edgecolor': '#0e1117',
    'text.color': 'white',
    'grid.color': 'grey',
    'grid.alpha': 0.8
})

# ======== CĂI BAZĂ ========
base_path = 'Dataset'
exp_path = os.path.join(base_path, 'experiment-i')
subject_info_path = os.path.join(exp_path, 'Date.xlsx')

frame_height = 32
frame_width = 64

# ======== INTERFAȚĂ ========
st.title("🔬 Analiza posturii somnului")

# ======== GRAFIC COMPARATIV ÎNTRE SUBIECȚI & POSTURI ========
if os.path.exists(subject_info_path):
   
    df_info = pd.read_excel(subject_info_path, engine='openpyxl')
    df_info.columns = df_info.columns.str.strip()  # elimină spațiile din capul de tabel

    df_info['S_ID'] = ['S' + str(i+1) for i in range(len(df_info))]

    posturi_map = {
        1: 'Supine (0°)',
        2: 'Right (0°)',
        3: 'Left (0°)',
        4: 'Right (30°)',
        5: 'Right (60°)',
        6: 'Left (30°)',
        7: 'Left (60°)',
        8: 'Supine',
        9: 'Supine',
        10: 'Supine',
        11: 'Supine',
        12: 'Supine',
        13: 'Right Fetus',
        14: 'Left Fetus',
        15: 'Supine (30° incline)',
        16: 'Supine (45° incline)',
        17: 'Supine (60° incline)',
    }

    results = []

    for sid in df_info['S_ID']:
        age = df_info[df_info['S_ID'] == sid]['Age'].values[0]
        subj_path = os.path.join(exp_path, sid)
        if not os.path.isdir(subj_path):
            continue

        for i in range(1, 18):
            fpath = os.path.join(subj_path, f"{i}.txt")
            if not os.path.isfile(fpath):
                continue
            try:
                data = np.loadtxt(fpath)
                frames = data.reshape((-1, frame_height, frame_width))
                results.append({
                    "Subiect": sid,
                    "Age": age,
                    "Postura": posturi_map[i],
                    "Media Presiunii": np.mean(frames),
                    "Varianță": np.var(frames),
                    "Presiune Totală": np.sum(frames)
                })
            except:
                continue

    df_results = pd.DataFrame(results)

    st.subheader("📊 Statistici pe toți subiecții din primul experiment")
    st.dataframe(df_results)

    sel_postura = st.selectbox("Selectează postură pentru grafic:", sorted(df_results['Postura'].unique()))
    df_filtrat = df_results[df_results['Postura'] == sel_postura]

    st.subheader(f"📈 Grafic interactiv: Media presiunii în funcție de vârstă - {sel_postura}")
    
    df_chart = df_filtrat[['Subiect', 'Age', 'Media Presiunii']].sort_values(by='Age')

    chart = alt.Chart(df_chart).mark_bar(color='deepskyblue').encode(
        x=alt.X('Subiect:N', title='Subiect'),
        y=alt.Y('Media Presiunii:Q', title='Media Presiunii'),
        tooltip=['Subiect', 'Age', 'Media Presiunii']
    ).properties(
        width=700,
        height=400,
        title=f'Media presiunii per subiect – Postură: {sel_postura}'
    )

    st.altair_chart(chart, use_container_width=True)



    st.subheader("📊 Media presiunii pentru fiecare postură")

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df_results, x='Postura', y='Media Presiunii', ax=ax)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)


    st.subheader("📊 Varianța presiunii pentru fiecare postură")

    fig_var, ax_var = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df_results, x='Postura', y='Varianță', ax=ax_var, palette='magma')
    ax_var.set_title("Varianța presiunii pe postură", fontsize=14)
    ax_var.set_xlabel("Postură")
    ax_var.set_ylabel("Varianță")
    plt.xticks(rotation=45, ha='right')
    ax_var.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig_var)



    st.subheader("🔁 Autocorelația presiunii în posturi Supine (Experiment 1)")

    supine_posturi = ['Supine (0°)', 'Supine', 'Supine (30° incline)', 'Supine (45° incline)', 'Supine (60° incline)']
    df_supine = df_results[df_results['Postura'].isin(supine_posturi)]

    selected_supine = st.selectbox("Alege subiect și postură Supine:", 
                                   df_supine[['Subiect', 'Postura']].drop_duplicates().apply(lambda x: f"{x['Subiect']} - {x['Postura']}", axis=1))

    sel_sid, sel_pos = selected_supine.split(" - ")
    index = list(posturi_map.values()).index(sel_pos) + 1  # găsim indexul fișierului (1.txt .. 17.txt)

    fpath = os.path.join(exp_path, sel_sid, f"{index}.txt")
    try:
        data = np.loadtxt(fpath)
        frames = data.reshape((-1, frame_height, frame_width))
        pressure_over_time = [np.sum(frame) for frame in frames]

        # autocorelație
        autocor = correlate(pressure_over_time, pressure_over_time, mode='full') / len(pressure_over_time)
        lags = np.arange(-len(pressure_over_time) + 1, len(pressure_over_time))

        fig_aut, ax_aut = plt.subplots()
        ax_aut.plot(lags, autocor, color='magenta')
        ax_aut.set_title(f"Autocorelație - {sel_sid} - {sel_pos}")
        ax_aut.set_xlabel("Lag (secunde)")
        ax_aut.set_ylabel("Corelație")
        ax_aut.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig_aut)

    except Exception as e:
        st.warning(f"Eroare la citire sau autocorelație: {e}")




    # ======== ANALIZĂ EXPERIMENTUL 2 (Air_Mat vs Sponge_Mat) ========
st.title("🛏️ Analiza comparativă - Saltele (Experimentul 2)")

exp2_path = os.path.join(base_path, 'experiment-ii')
frame_height, frame_width = 27, 64

if os.path.exists(exp2_path):
    results = []
    subjects = sorted([d for d in os.listdir(exp2_path) if os.path.isdir(os.path.join(exp2_path, d))])

    for subject in subjects:
        subject_path = os.path.join(exp2_path, subject)
        for mat_type in ["Air_Mat", "Sponge_Mat"]:
            mat_path = os.path.join(subject_path, mat_type)
            if not os.path.isdir(mat_path):
                continue
            for file in os.listdir(mat_path):
                if file.endswith(".txt") and "Matrix" in file:
                    posture = file.replace(".txt", "").split("_")[-1]  # B1, C2, etc.
                    full_path = os.path.join(mat_path, file)
                    try:
                        data = np.loadtxt(full_path)
                        frames = data.reshape(-1, frame_height, frame_width)
                        results.append({
                            "Subiect": subject,
                            "Saltea": mat_type.replace("_Mat", ""),
                            "Poziție": posture,
                            "Media Presiunii": np.mean(frames),
                            "Varianță": np.var(frames),
                            "Presiune Totală": np.sum(frames)
                        })
                    except Exception as e:
                        st.warning(f"Eroare la {full_path}: {e}")

    df_exp2 = pd.DataFrame(results)

    st.subheader("📋 Tabel - Presiune pe fiecare poziție și saltea")
    st.dataframe(df_exp2)

    st.subheader("📈 Compară media presiunii între saltele")
    sel_mat = st.selectbox("Selectează tip saltea:", sorted(df_exp2['Saltea'].unique()))
    df_sel = df_exp2[df_exp2['Saltea'] == sel_mat]

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    df_grouped = df_sel.groupby('Poziție')['Media Presiunii'].mean().reset_index()
    ax3.bar(df_grouped['Poziție'], df_grouped['Media Presiunii'], color='skyblue')
    ax3.set_title(f"Media presiunii per postură ({sel_mat})", fontsize=14)
    ax3.set_xlabel("Poziție")
    ax3.set_ylabel("Media presiunii")
    ax3.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig3)
     
    st.subheader("📊 Varianța presiunii pe poziții – comparativ între saltele")

    for saltea in sorted(df_exp2['Saltea'].unique()):
        df_saltea = df_exp2[df_exp2['Saltea'] == saltea]
        fig_var2, ax_var2 = plt.subplots(figsize=(10, 5))
        sns.barplot(data=df_saltea, x='Poziție', y='Varianță', ax=ax_var2, palette='coolwarm')
        ax_var2.set_title(f"Varianța presiunii – Saltea: {saltea}", fontsize=14)
        ax_var2.set_xlabel("Poziție")
        ax_var2.set_ylabel("Varianță")
        plt.xticks(rotation=45, ha='right')
        ax_var2.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig_var2)

else:
    st.warning("Folderul pentru experimentul 2 nu a fost găsit.")


   

# Codificăm poziția (ex: B1, C2...) ca număr
df_exp2['Poziție_Idx'] = LabelEncoder().fit_transform(df_exp2['Poziție'])

# Alegem saltea
saltea = 'Air'
df_saltea = df_exp2[df_exp2['Saltea'] == saltea]

# X = poziția (numeric), y = media presiunii
X = df_saltea[['Poziție_Idx']]
y = df_saltea['Media Presiunii']

model = LinearRegression().fit(X, y)
df_saltea['Pred'] = model.predict(X)

# Grafic
fig, ax = plt.subplots()
ax.scatter(X, y, color='cyan', label='Real')
ax.plot(X, df_saltea['Pred'], color='red', label='Regresie liniară')
ax.set_title(f"Regresie - Saltea {saltea}")
ax.set_xlabel("Poziție (index)")
ax.set_ylabel("Media presiunii")
ax.legend()
st.pyplot(fig)





# ======== ANALIZĂ FIȘIER INDIVIDUAL (CODUL TĂU ORIGINAL) ========
subjects = sorted([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))])
selected_subject = st.selectbox("Alege experiment:", subjects)
subject_path = os.path.join(base_path, selected_subject)

data_files = []
for root, _, files in os.walk(subject_path):
    for file in files:
        if file.endswith('.txt'):
            data_files.append(os.path.join(root, file))

if data_files:
    selected_file = st.selectbox("Alege fișier:", data_files)

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
        ax.axhline(y=np.mean(data), color='red', linestyle='--', label="Media")
        ax.legend()
        st.pyplot(fig)

        st.write("**Media:**", float(np.mean(data)))
        st.write("**Varianța:**", float(np.var(data)))

        st.subheader("🔁 Autocorelație")
        autocor = correlate(data, data, mode='full') / len(data)
        fig1, ax1 = plt.subplots()
        ax1.plot(autocor, label="Autocorelație", color="magenta", linewidth=1.5)
        ax1.set_title("Autocorelație", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Lag")
        ax1.set_ylabel("Corelație")
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend()
        st.pyplot(fig1)

        st.subheader("📈 Transformata Fourier (FFT)")
        Y = fft(data)
        f = np.fft.fftfreq(len(data), d=1)
        fig2, ax2 = plt.subplots()
        ax2.plot(f[:len(data)//2], np.abs(Y[:len(data)//2]), label="Spectru FFT", color="lime", linewidth=1.5)
        ax2.set_title("Spectru FFT", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Frecvență (Hz)")
        ax2.set_ylabel("Amplitudine")
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.legend()
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Eroare la citirea fișierului: {e}")
else:
    st.warning("Nu s-au găsit fișiere .txt pentru acest subiect.")

# ======== FOOTER ========
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
