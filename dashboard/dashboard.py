import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import glob
import os

# Konfigurasi Halaman 
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Data 
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "main_data.csv"))

# Sidebar 
with st.sidebar:
    st.title("Beijing Air Quality")
    st.markdown("**Dataset:** PRSA 2013–2017  \n**12 Monitoring Stations**")
    st.markdown("---")
    
    all_stations = sorted(df['station'].unique())
    selected_stations = st.multiselect(
        "Pilih Stasiun:", all_stations, default=all_stations
    )
    
    year_range = st.slider(
        "Rentang Tahun:", 2013, 2017, (2013, 2017)
    )
    

# Filter data
df_filtered = df[
    (df['station'].isin(selected_stations)) &
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1])
]


# Header 
st.title("Dashboard Kualitas Udara Beijing (2013–2017)")
st.markdown("Analisis konsentrasi polutan PM2.5 berdasarkan tren waktu dan distribusi antar stasiun pemantauan.")

if df_filtered.empty:
    st.info("Silakan pilih setidaknya satu stasiun di sidebar.")
    st.stop()

# KPI Cards 
avg_pm25 = df_filtered['PM2.5'].mean()
max_pm25 = df_filtered['PM2.5'].max()
worst_station = df_filtered.groupby('station')['PM2.5'].mean().idxmax()
pct_unhealthy = (df_filtered['PM2.5'] > 55.4).mean() * 100

def custom_metric(label, value, unit, help_text,):
    st.markdown(
        f"""
        <div style="
            background-color: #262730; 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 10px;">
            <p style="margin: 0; font-size: 14px; color: #FAFAFA; opacity: 0.8;">{label}</p>
            <h2 style="margin: 0; padding: 0; font-size: 28px; font-weight: bold; color: white;">{value}</h2>
            <p style="margin: 0; font-size: 13px; color: #FAFAFA; font-weight: bold;">{unit}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.markdown("### Ringkasan Parameter Utama")
col1, col2, col3, col4 = st.columns(4)

with col1:
    custom_metric("Rata-rata PM2.5", f"{avg_pm25:.1f}", "mikrogram/m³", "Rata-rata seluruh data terfilter")
with col2:
    custom_metric("PM2.5 Tertinggi", f"{max_pm25:.0f}", "mikrogram/m³", "Nilai maksimum yang tercatat")
with col3:
    custom_metric("Stasiun Terburuk", worst_station, "Lokasi", "Stasiun dengan rata-rata tertinggi")
with col4:
    custom_metric("Jam 'Unhealthy+'", f"{pct_unhealthy:.1f}%", "Persentase Durasi", "Persentase jam dengan PM2.5 > 55.4")


# TAB 
tab1, tab2, tab3 = st.tabs(["Tren Temporal", "Perbandingan Stasiun", "Korelasi Antar Polutan"])

# TAB 1: Tren Temporal
with tab1:
    st.subheader("Pertanyaan 1: Bagaimana tren PM2.5 bulanan dan pola musiman di Beijing?")
    
    col_l, col_r = st.columns([3, 1])
    
    with col_l:
        # Monthly trend
        monthly_avg = df_filtered.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
        monthly_avg['year_month'] = pd.to_datetime(monthly_avg[['year', 'month']].assign(day=1))
        monthly_avg = monthly_avg.sort_values('year_month')
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(monthly_avg['year_month'], monthly_avg['PM2.5'],
                color='#E74C3C', linewidth=2, marker='o', markersize=3)
        ax.fill_between(monthly_avg['year_month'], monthly_avg['PM2.5'], alpha=0.15, color='#E74C3C')
        ax.set_title("Tren Rata-rata PM2.5 Bulanan", fontsize=13, fontweight='bold')
        ax.set_ylabel("PM2.5 (mikrogram/m\u00B3)")
        ax.legend(fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='x', rotation=30)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_r:
        # Seasonal averages
        season_order = ['Winter (Des-Feb)', 'Spring (Mar-Mei)', 
                       'Summer (Jun-Agu)', 'Autumn (Sep-Nov)']
        seasonal = df_filtered.groupby('season')['PM2.5'].mean().reindex(season_order)
        season_colors = {'Winter': '#2C3E50', 'Spring': '#27AE60',
                         'Summer': '#F39C12', 'Autumn': '#E67E22'}
        season_labels = [s.replace(' (', '\n(') for s in seasonal.index]

        fig2, ax2 = plt.subplots(figsize=(4, 4))
        bars = ax2.bar(season_labels, seasonal.values,
                       color=[season_colors[s.split(' ')[0]] for s in season_order],
               edgecolor='white', width=0.6)
        for bar, val in zip(bars, seasonal.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{val:.1f}', ha='center', fontsize=10, fontweight='bold')
        ax2.set_title("Rata-rata PM2.5\nper Musim", fontsize=11, fontweight='bold')
        ax2.set_ylabel("PM2.5 (mikrogram/m\u00B3)")
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, seasonal.max() + 25)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
    
    # Insight
    worst_season = seasonal.idxmax()
    best_season = seasonal.idxmin()
    peak_month = monthly_avg.loc[monthly_avg['PM2.5'].idxmax()]
    peak_date = peak_month['year_month'].strftime('%B %Y')
    peak_value = peak_month['PM2.5']

    st.info(
        f"**Insight:** "
        f"Grafik tren menunjukkan volatilitas tinggi setiap tahunnya. Lonjakan polusi paling ekstrem tercatat pada {peak_date} mencapai {peak_value:.1f} mikrogram/m\u00B3. "
        f"Secara musiman, rata-rata PM2.5 tertinggi terjadi pada Musim **{worst_season}** memiliki rata-rata PM2.5 tertinggi"
        f"({seasonal[worst_season]:.1f} mikrogram/m\u00B3), sedangkan **{best_season}** adalah yang terendah "
        f"({seasonal[best_season]:.1f} mikrogram/m\u00B3)."
    )

# TAB 2: Perbandingan Stasiun
with tab2:
    st.subheader("Pertanyaan 2: Stasiun mana yang memiliki PM2.5 tertinggi dan terendah?")
    
    station_stats = df_filtered.groupby('station')['PM2.5'].mean().sort_values(ascending=True)
    overall_mean = df_filtered['PM2.5'].mean()
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = ['#C0392B' if v > overall_mean else '#2980B9' for v in station_stats.values]
        bars = ax.barh(station_stats.index, station_stats.values,
                       color=colors, edgecolor='white', height=0.7)
        ax.axvline(overall_mean, color='black', ls='--', lw=1.5,
                   label=f'Rata-rata ({overall_mean:.1f})')
        for bar, val in zip(bars, station_stats.values):
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}', va='center', fontsize=8.5, fontweight='bold')
        ax.set_title("Rata-rata PM2.5 per Stasiun", fontsize=12, fontweight='bold')
        ax.set_xlabel("PM2.5 (mikrogram/m\u00B3)")
        ax.legend(fontsize=9)
        ax.grid(axis='x', alpha=0.3)
        
        red_patch = mpatches.Patch(color='#C0392B', label='Di atas rata-rata')
        blue_patch = mpatches.Patch(color='#2980B9', label='Di bawah rata-rata')
        ax.legend(handles=[red_patch, blue_patch], fontsize=8.5)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col_b:
        # Stacked bar AQI categories
        cat_order = ['Good', 'Moderate', 'Unhealthy (Sensitive)', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
        cat_colors = {
            'Good': '#27AE60', 'Moderate': '#F1C40F',
            'Unhealthy (Sensitive)': '#E67E22', 'Unhealthy': '#E74C3C',
            'Very Unhealthy': '#8E44AD', 'Hazardous': '#2C3E50'
        }
        
        cat_dist = df_filtered.groupby(['station', 'PM25_category']).size().unstack(fill_value=0)
        # Ensure all categories present
        for c in cat_order:
            if c not in cat_dist.columns:
                cat_dist[c] = 0
        cat_pct = cat_dist[cat_order].div(cat_dist.sum(axis=1), axis=0) * 100
        station_order_desc = df_filtered.groupby('station')['PM2.5'].mean().sort_values(ascending=False).index
        cat_pct = cat_pct.reindex(station_order_desc)
        
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        bottom = np.zeros(len(cat_pct))
        for cat in cat_order:
            if cat in cat_pct.columns:
                ax2.barh(range(len(cat_pct)), cat_pct[cat].values,
                         left=bottom, color=cat_colors[cat], label=cat, height=0.7)
                bottom += cat_pct[cat].values
        
        ax2.set_yticks(range(len(cat_pct)))
        ax2.set_yticklabels(cat_pct.index, fontsize=9)
        ax2.set_xlabel("Persentase Jam (%)")
        ax2.set_title("Distribusi Kategori AQI per Stasiun", fontsize=12, fontweight='bold')
        ax2.legend(loc='lower right', fontsize=7, title='Kategori PM2.5')
        ax2.grid(axis='x', alpha=0.3)
        ax2.set_xlim(0, 100)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
    
    best_s = station_stats.idxmin()
    worst_s = station_stats.idxmax()
    st.info(
        f"**Insight:** **{worst_s}** memiliki rata-rata PM2.5 tertinggi ({station_stats[worst_s]:.1f} mikrogram/m\u00B3), "
        f"sedangkan **{best_s}** terendah ({station_stats[best_s]:.1f} mikrogram/m\u00B3). "
        f"Perbedaan mencapai {station_stats[worst_s]-station_stats[best_s]:.1f} mikrogram/m\u00B3, "
        f"menunjukkan pentingnya faktor lokasi urban dengan suburban."
    )

# TAB 3: Korelasi
with tab3:
    
    # Correlation heatmap
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'WSPM']
    corr = df_filtered[pollutants].corr()
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, ax=ax2,
                linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax2.set_title("Korelasi Antar Polutan & Meteorologi", fontsize=12, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()
    
    st.info(
        "**Insight:** PM2.5 berkorelasi positif kuat dengan PM10 dan CO (sumber pembakaran), "
        "serta berkorelasi negatif dengan O3 dan kecepatan angin (WSPM). "
        "Korelasi negatif antara PM2.5 dan WSPM menunjukkan bahwa angin kencang "
        "membantu dispersi polutan."
    )

# Footer 
st.markdown("---")
st.markdown(
    "**Sumber Data:** [Air Quality Dataset](https://github.com/marceloreis/HTI) | "
    "12 Stasiun Pemantauan Beijing | Maret 2013 – Februari 2017"
)
