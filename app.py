import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="GA Energy Dashboard", layout="wide")
st.title("⚡ GA Energy Management - Load Profile Dashboard")

# 1. Building Hours Configuration
st.sidebar.header("Building Operating Hours")
open_time = st.sidebar.time_input("Opening Time", pd.to_datetime("08:00").time())
close_time = st.sidebar.time_input("Closing Time", pd.to_datetime("18:00").time())

# 2. File Upload Area
uploaded_file = st.file_uploader("Upload Supplier Half-Hourly CSV Data", type=["csv"])

if uploaded_file is not None:
    # Load and prepare data
    df = pd.read_csv(uploaded_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['DayOfWeek'] = df['Timestamp'].dt.day_name()
    df['Time'] = df['Timestamp'].dt.time
    
    # Calculate Day of Week Averages
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Graphs Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Electricity Load Profile (kWh)")
        elec_pivot = df.groupby(['Time', 'DayOfWeek'])['Electricity_kWh'].mean().unstack()
        fig_elec = px.line(elec_pivot, x=elec_pivot.index, y=days_order, 
                           labels={"value": "Avg kWh", "Time": "Time of Day"})
        st.plotly_chart(fig_elec, use_container_width=True)
        
    with col2:
        st.subheader("🔥 Gas Load Profile (kWh)")
        gas_pivot = df.groupby(['Time', 'DayOfWeek'])['Gas_kWh'].mean().unstack()
        fig_gas = px.line(gas_pivot, x=gas_pivot.index, y=days_order, 
                          labels={"value": "Avg kWh", "Time": "Time of Day"})
        st.plotly_chart(fig_gas, use_container_width=True)

    # 3. Out-of-Hours Consumption Calculator
    st.markdown("---")
    st.subheader("🚨 Out-of-Hours Energy Usage Analysis")
    
    ooh_mask = (df['Time'] < open_time) | (df['Time'] > close_time)
    ooh_elec = df[ooh_mask]['Electricity_kWh'].sum()
    ooh_gas = df[ooh_mask]['Gas_kWh'].sum()
    
    col_a, col_b = st.columns(2)
    col_a.metric("Out-of-Hours Electricity", f"{ooh_elec:,.1f} kWh")
    col_b.metric("Out-of-Hours Gas", f"{ooh_gas:,.1f} kWh")

else:
    st.info("Please upload a CSV file with columns: `Timestamp`, `Electricity_kWh`, `Gas_kWh`.")
