import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="India Air Quality Dashboard Final",
    page_icon="💨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Cleaning ---
@st.cache_data
def load_data():
    """Loads, cleans, and prepares the pollution data."""
    df = pd.read_csv('pollution_data.csv')
    df.dropna(subset=['avg_value', 'latitude', 'longitude'], inplace=True)
    df['last_update'] = pd.to_datetime(df['last_update'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
    df['state'] = df['state'].str.strip().str.title()
    df['city'] = df['city'].str.strip().str.title()
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.title('Dashboard Controls')
states = sorted(df['state'].unique())
selected_state = st.sidebar.selectbox('Select a State', states)
cities_in_state = sorted(df[df['state'] == selected_state]['city'].unique())
selected_city = st.sidebar.selectbox('Select a City', cities_in_state)

# --- Main Dashboard ---
st.title("🇮🇳 Final Air Quality Dashboard")
latest_update = df['last_update'].max().strftime('%B %d, %Y at %I:%M %p')
st.markdown(f"*Last data update: **{latest_update}***")
st.markdown("---")

# --- National & State-Level Analysis (MOVED TO TOP) ---
st.header("🌎 National & State Comparison")
pollutants = sorted(df['pollutant_id'].unique())
selected_pollutant = st.selectbox('Select a Pollutant for Comparison', pollutants, index=pollutants.index('PM2.5'))
filtered_df = df[df['pollutant_id'] == selected_pollutant]

# --- Enhanced KPIs ---
if not filtered_df.empty:
    station_count = filtered_df['station'].nunique()
    national_avg = filtered_df['avg_value'].mean()
    most_polluted_city_row = filtered_df.loc[filtered_df['avg_value'].idxmax()]
    most_polluted_city = f"{most_polluted_city_row['city']} ({most_polluted_city_row['avg_value']:.2f})"
    least_polluted_city_row = filtered_df.loc[filtered_df['avg_value'].idxmin()]
    least_polluted_city = f"{least_polluted_city_row['city']} ({least_polluted_city_row['avg_value']:.2f})"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stations Reporting", f"{station_count}")
    col2.metric(f"National Average ({selected_pollutant})", f"{national_avg:.2f}")
    col3.metric("Most Polluted City", most_polluted_city)
    col4.metric("Least Polluted City", least_polluted_city)
else:
    st.warning("No data available for the selected filters.")

# --- Colorful Visualizations ---
if not filtered_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Top 10 Most Polluted Cities ({selected_pollutant})")
        top_cities = filtered_df.groupby('city')['avg_value'].mean().nlargest(10).sort_values()
        fig_bar_cities = go.Figure(go.Bar(
            x=top_cities.values, y=top_cities.index, orientation='h',
            marker=dict(color=top_cities.values, colorscale='Plasma')))
        fig_bar_cities.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_cities, use_container_width=True)
    with col2:
        st.subheader(f"State-wise Average Pollution ({selected_pollutant})")