# main.py
import streamlit as st
import plotly.express as px
from src.services import DataService

# Configurazione Pagina
st.set_page_config(page_title="Dashboard Spese", layout="wide")

def main():
    st.title("📊 Dashboard Spese")
    
    # Istanziamo il servizio
    service = DataService()

    with st.spinner('Caricamento dati...'):
        df = service.fetch_and_process_data()

    if df.empty:
        st.warning("Nessun dato disponibile.")
        return

    # --- SIDEBAR ---
    st.sidebar.header("Filtri")
    df['AnnoMese'] = df['data'].dt.strftime('%Y-%m')
    unique_months = sorted(df['AnnoMese'].unique())
    
    if not unique_months:
        st.stop()
        
    selected_month = st.sidebar.selectbox("Periodo", unique_months, index=len(unique_months)-1)
    filtered_df = df[df['AnnoMese'] == selected_month].copy()

    # --- KPI ---
    tot = filtered_df['totale'].sum()
    days = filtered_df['data'].dt.day.nunique()
    avg = tot / days if days else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Totale", f"€ {tot:,.2f}")
    c2.metric("Giorni", days)
    c3.metric("Media/Giorno", f"€ {avg:,.2f}")

    # --- GRAFICO ---
    chart_data = filtered_df.groupby(['data', 'tipo'])['totale'].sum().reset_index()
    
    fig = px.bar(
        chart_data, x='data', y='totale', color='tipo',
        title=f"Spese {selected_month}", height=500,
        text_auto='.2s'
    )
    fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Budget 30€")
    fig.update_xaxes(dtick="D1", tickformat="%d %b")
    
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELLA ---
    with st.expander("Dati Dettagliati"):
        st.dataframe(
            filtered_df.sort_values('data'),
            column_config={
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "totale": st.column_config.NumberColumn("Totale", format="€ %.2f")
            },
            use_container_width=True
        )

if __name__ == "__main__":
    main()