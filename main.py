# main.py
import streamlit as st
import plotly.graph_objects as go
from src.services import DataService
from src.config import MAPPA_CATEGORIE

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
    # Aggiungi macrocategoria
    filtered_df['macrocategoria'] = filtered_df['tipo'].map(MAPPA_CATEGORIE).fillna('Altro')

    # Raggruppa per data, tipo e macrocategoria
    chart_data = filtered_df.groupby(['data', 'tipo', 'macrocategoria'])['totale'].sum().reset_index()
    chart_data['totale'] = chart_data['totale'].round(1)

    # Calcola totale per macrocategoria per ogni giorno e prepara dettaglio tipi
    macro_totals = chart_data.groupby(['data', 'macrocategoria']).agg(
        totale_macro=('totale', 'sum'),
        dettaglio=('tipo', lambda x: list(x)),
        valori=('totale', lambda x: list(x))
    ).reset_index()

    # Crea hover text personalizzato
    macro_totals['hover_text'] = macro_totals.apply(
        lambda row: f"<b>Totale: {row['totale_macro']:.1f} €</b><br>" +
                    "<br>".join([f"{t}: {v:.1f} €" for t, v in zip(row['dettaglio'], row['valori'])]),
        axis=1
    )

    fig = go.Figure()

    # Colori per macrocategorie
    colori = {
        'Trasporti': '#636EFA',
        'Cibo': '#EF553B',
        'Alloggio': '#00CC96',
        'Attività': '#AB63FA',
        'Acquisti': '#FFA15A',
        'Salute': '#19D3F3',
        'Extra': '#FF6692',
        'Altro': '#B6E880'
    }

    for macro in macro_totals['macrocategoria'].unique():
        df_macro = macro_totals[macro_totals['macrocategoria'] == macro]
        fig.add_trace(go.Bar(
            x=df_macro['data'],
            y=df_macro['totale_macro'],
            name=macro,
            marker_color=colori.get(macro, '#888888'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=df_macro['hover_text']
        ))

    fig.update_layout(
        barmode='stack',
        title=f"Spese {selected_month}",
        height=500,
        xaxis_title="",
        yaxis_title="Totale (€)",
        legend_title="Categoria"
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