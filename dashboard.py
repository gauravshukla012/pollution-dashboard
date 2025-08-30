import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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

# --- KPIs ---
st.header("📊 National Snapshot")
pollutants = sorted(df['pollutant_id'].unique())
selected_pollutant = st.selectbox('Select a Pollutant for National KPIs & Comparison', pollutants, index=pollutants.index('PM2.5'))
filtered_df = df[df['pollutant_id'] == selected_pollutant]

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

st.markdown("---")

# --- City-Specific Analysis ---
st.header(f"📍 Deep Dive: {selected_city}, {selected_state}")
city_df = df[df['city'] == selected_city]
if not city_df.empty:
    pm25_data = city_df[city_df['pollutant_id'] == 'PM2.5'].iloc[0] if not city_df[city_df['pollutant_id'] == 'PM2.5'].empty else None
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("PM2.5 Level Gauge")
        if pm25_data is not None:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=pm25_data['avg_value'], title={'text': "PM2.5 (μg/m³)"},
                gauge={'axis': {'range': [None, 250]}, 'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 30], 'color': 'green'}, {'range': [30, 60], 'color': 'yellow'},
                                 {'range': [60, 90], 'color': 'orange'}, {'range': [90, 120], 'color': 'red'},
                                 {'range': [120, 250], 'color': 'purple'}]}))
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("No PM2.5 data available for this city.")
    with col2:
        st.subheader("Pollutant Mix")
        pollutant_mix = city_df[['pollutant_id', 'avg_value']].groupby('pollutant_id').mean().reset_index()
        fig_donut = go.Figure(data=[go.Pie(labels=pollutant_mix['pollutant_id'], values=pollutant_mix['avg_value'], hole=.4)])
        fig_donut.update_traces(textinfo='percent+label', hoverinfo='label+percent+value')
        st.plotly_chart(fig_donut, use_container_width=True)
else:
    st.warning("No data available for the selected city.")

st.markdown("---")

# --- National Comparison Visualizations ---
st.header("🌎 National Comparison Charts")
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
        state_avg = filtered_df.groupby('state')['avg_value'].mean().sort_values(ascending=False)
        fig_bar_states = go.Figure(go.Bar(
            x=state_avg.index, y=state_avg.values,
            marker=dict(color=state_avg.values, colorscale='Plasma')))
        st.plotly_chart(fig_bar_states, use_container_width=True)

# --- NATIONWIDE MAP ---
if not filtered_df.empty:
    st.header(f"🗺️ Nationwide Station Map for {selected_pollutant}")
    fig_map = px.scatter_mapbox(filtered_df,
                                lat="latitude", lon="longitude", color="avg_value",
                                size="avg_value", hover_name="station",
                                hover_data=["city", "state", "avg_value"],
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                size_max=15, zoom=4,
                                mapbox_style="carto-positron",
                                center={"lat": 20.5937, "lon": 78.9629})
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# --- Detailed Data View ---
with st.expander("View Detailed Data Table"):
    st.dataframe(filtered_df)