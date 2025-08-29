import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="India Air Quality Dashboard",
    page_icon="💨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Cleaning ---
@st.cache_data
def load_data():
    """Loads, cleans, and prepares the pollution data."""
    df = pd.read_csv('pollution_data.csv')
    
    # Drop rows with missing essential data
    df.dropna(subset=['avg_value', 'latitude', 'longitude'], inplace=True)
    
    # Convert 'last_update' to datetime objects for proper sorting
    df['last_update'] = pd.to_datetime(df['last_update'])
    
    # Clean up city and state names
    df['state'] = df['state'].str.strip().str.title()
    df['city'] = df['city'].str.strip().str.title()
    
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header('Dashboard Filters')

# Get lists for filters
pollutants = sorted(df['pollutant_id'].unique())
states = sorted(df['state'].unique())

# Primary filter: Pollutant
selected_pollutant = st.sidebar.selectbox('Select a Pollutant', pollutants, index=pollutants.index('PM2.5'))

# Secondary filter: States (multiselect)
selected_states = st.sidebar.multiselect('Select States', states, default=states)

# Filter data based on selections
if selected_states:
    filtered_df = df[(df['pollutant_id'] == selected_pollutant) & (df['state'].isin(selected_states))]
else:
    # If no state is selected, show all data for the chosen pollutant
    filtered_df = df[df['pollutant_id'] == selected_pollutant]

# --- Main Dashboard ---
st.title("🇮🇳 India Real-Time Air Quality Dashboard")

# Show the latest update time from the data
latest_update = df['last_update'].max().strftime('%B %d, %Y at %I:%M %p')
st.markdown(f"*Last data update: **{latest_update}***")

st.markdown("---")

# --- Key Performance Indicators (KPIs) ---
if not filtered_df.empty:
    # Calculate KPIs
    station_count = filtered_df['station'].nunique()
    national_avg = filtered_df['avg_value'].mean()
    most_polluted_city_row = filtered_df.loc[filtered_df['avg_value'].idxmax()]
    most_polluted_city = f"{most_polluted_city_row['city']} ({most_polluted_city_row['avg_value']:.2f})"

    # Display KPIs in columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Stations Reporting", f"{station_count}")
    col2.metric(f"National Average ({selected_pollutant})", f"{national_avg:.2f}")
    col3.metric("Most Polluted City", most_polluted_city)
else:
    st.warning("No data available for the selected filters.")

st.markdown("---")

# --- Visualizations ---
if not filtered_df.empty:
    col1, col2 = st.columns((1, 1))

    with col1:
        # MAP VISUALIZATION
        st.subheader(f"Station Map for {selected_pollutant}")
        # Rename columns for st.map to understand
        map_df = filtered_df[['latitude', 'longitude']].copy()
        map_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        st.map(map_df, zoom=4)

    with col2:
        # TOP 10 CITIES BAR CHART
        st.subheader(f"Top 10 Most Polluted Cities ({selected_pollutant})")
        top_cities = filtered_df.groupby('city')['avg_value'].mean().nlargest(10).sort_values()
        st.bar_chart(top_cities)

    # STATE-WISE AVERAGE BAR CHART
    st.subheader(f"State-wise Average Pollution ({selected_pollutant})")
    state_avg = filtered_df.groupby('state')['avg_value'].mean().sort_values(ascending=False)
    st.bar_chart(state_avg)

# --- Detailed Data View ---
with st.expander("View Detailed Data Table"):
    st.dataframe(filtered_df)