import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import folium 
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import altair as alt
import re
import base64
import datetime as dt


# Set page config to wide
st.set_page_config(layout="wide")

# --- Custom CSS for better spacing and full width ---
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 95%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .bin-card {
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .full { background-color:#ff4d4d; color:white; }
    .medium { background-color:#ffcc00; color:black; }
    .empty { background-color:#33cc33; color:white; }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar menu with logo
with st.sidebar:
    # Display your logo instead of menu title
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 15px;">
            <img src="data:image/png;base64,{base64.b64encode(open('C:/Users/user/OneDrive/Documents/FYP/logo_v3.png', 'rb').read()).decode()}"  
                alt="Logo" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Menu options
    selected = option_menu(
        menu_title=None,  # No text title, just the logo
        options=[
            "🗑️ Dashboard", 
            "📊 Report", 
            "⚙️ Device", 
            "👤 Account"
        ],
        menu_icon="💻",
        default_index=0,
    )


# --- PAGE CONTENT ---
if selected == "🗑️ Dashboard":
    st.title("🏙️ Smart Waste Management Dashboard")
    st.write("Welcome! Here's your latest update.")

    # Dropdown to choose subpage
    subpage = st.selectbox(
        "Select Page:",
        ["Dummy Data", "Real-time Data"]
    )

    # Divider
    st.markdown("---")

    if subpage == "Dummy Data":
        # KPI SECTION 
        st.markdown("### 📊 KPI Overview")
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQimwz3tpdodtv2xLKVIx5fVDx1SXaUGzfK6grHmYQSK-ug7Xe0qJsXQct6vyee50l5_AqBxug44E1-/pub?gid=628102932&single=true&output=csv"
        df = pd.read_csv(url)

        THRESHOLD = 70 

        total_bins = 10
        exceed_bins = 1
        resolved_bins = 2  # dummy value
        offline_bins = 1   # dummy value

        # Custom CSS for KPI boxes
        st.markdown("""
            <style>
            .kpi-box {
                background-color: rgba(240, 240, 240, 0.4);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .kpi-box:hover {
                transform: scale(1.02);
                background-color: #f1f3f5;
            }
            .kpi-value {
                font-size: 30px;
                font-weight: bold;
                color: #0a0a0a;
            }
            .kpi-label {
                font-size: 16px;
                color: #0a0a0a;
                margin-top: 5px;
            }
            </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-value'>🗑️ {total_bins}</div>
                    <div class='kpi-label'>Total Bins</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-value'>🔔 {exceed_bins}</div>
                    <div class='kpi-label'>Exceeded Threshold</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-value'>✅ {resolved_bins}</div>
                    <div class='kpi-label'>Resolved</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class='kpi-box'>
                    <div class='kpi-value'>📴 {offline_bins}</div>
                    <div class='kpi-label'>Offline Devices</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        .kpi-section {
            margin-bottom: 40px; /* Adjust space below KPI section */
        }
        </style>
        """, unsafe_allow_html=True)

        # Layout: Top row
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📍 Bin Locations & Status")

            # --- Create Map centered at TRX (approx lat/lon) ---
            trx_lat, trx_lon = 3.142844, 101.718299
            m = folium.Map(location=[trx_lat, trx_lon], zoom_start=17)

            # Caption under the map
            st.caption("Map showing bin locations in the TRX District area.")

            # Load bin data
            url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQimwz3tpdodtv2xLKVIx5fVDx1SXaUGzfK6grHmYQSK-ug7Xe0qJsXQct6vyee50l5_AqBxug44E1-/pub?gid=628102932&single=true&output=csv"
            try:
                df = pd.read_csv(url)
                df["Timestamp"] = pd.to_datetime(df["Timestamp"])

                # Latest row for each bin
                latest_df = (
                    df.sort_values("Timestamp")
                    .groupby("Bin_ID")
                    .tail(1)
                )

                # Example: Assume your sheet has 'Lat' and 'Lon' columns
                for _, row in latest_df.iterrows():
                    bin_id = row["Bin_ID"]
                    fill = row["Fill_Level(%)"]

                    # 🚨 Make sure you match your sheet column names here
                    lat = row["Lat"]
                    lon = row["Lon"]

                    # Color by fill level
                    if fill >= 70:
                        color = "red"
                    elif fill >= 50:
                        color = "orange"
                    else:
                        color = "green"

                    # Add marker
                    folium.CircleMarker(
                        location=[row["Lat"], row["Lon"]],
                        radius=10,
                        color=color,
                        fill=True,
                        fill_color=color,
                        popup=f"{row['Bin_ID']} – {fill}% full"
                    ).add_to(m)

            except Exception as e:
                st.error(f"❌ Failed to load Google Sheet: {e}")

            # Show the map inside Streamlit
            st_folium(m, width=900, height=400)

        with col2:
            st.subheader("🔔 Alerts")
            with st.expander("Today's Alerts", expanded=True):
                st.write("**Bin 2** – Status: ⚠️ Unresolved – Time: 12:30 PM")
                # col_alert1, col_alert2 = st.columns(2)
                # with col_alert1:
                #     st.button("✅ Resolve", key="resolve_bin2")
                # with col_alert2:
                #     st.button("❌ Remove", key="remove_bin2")

            with st.expander("Past Alerts"):
                st.write("✅ Bin 1 – Resolved at 10:15 AM")
                st.write("✅ Bin 3 – Resolved at 09:40 AM")

        # Divider
        st.markdown("---")

        # Bin status section
        st.subheader("🗑️ Bin Status Overview")

        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQimwz3tpdodtv2xLKVIx5fVDx1SXaUGzfK6grHmYQSK-ug7Xe0qJsXQct6vyee50l5_AqBxug44E1-/pub?gid=628102932&single=true&output=csv"

        try:
            df = pd.read_csv(url)

            # ✅ Ensure timestamp is datetime
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])

            # ✅ Get only the latest row for each Bin_ID
            latest_df = (
                    df.sort_values("Timestamp")
                        .groupby("Bin_ID")
                        .tail(1)
                        .assign(BinNum=lambda x: x["Bin_ID"].str.extract(r"(\d+)").astype(int))  # extract number
                        .sort_values("BinNum")  # sort numerically
            )

        # ✅ Arrange bins in rows (3 per row)
            cols = st.columns(3, gap="large")

            for i, (idx, row) in enumerate(latest_df.iterrows()):
                bin_id = row["Bin_ID"]
                fill = row["Fill_Level(%)"]
                last = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

                # Status color
                if fill >= 80:
                    status_color = "#ff4d4d"
                    status_text = "FULL"
                elif fill >= 50:
                    status_color = "#ffcc00"
                    status_text = f"{fill}%"
                else:
                    status_color = "#33cc33"
                    status_text = "EMPTY"

                # Card with margin-bottom for vertical spacing
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div style="background-color:{status_color}; color:white; 
                                    border-radius:10px; padding:20px; text-align:center;
                                    margin-bottom:20px;">   <!-- 👈 add vertical gap -->
                            <h3>{bin_id}</h3>
                            <h2>{status_text}</h2>
                            <p>{last}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        except Exception as e:
            st.error(f"❌ Failed to load Google Sheet: {e}")

    elif subpage == "Real-time Data":
        
        # 🔗 Google Sheet URL for live data
        url_realtime = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAiujqFGFtpOsWWhbfZ5mKoY2EpbNTTfjYIDOZaHA8SIGxBecHXmC6FXvQ-swgz3iG9FXNSBdC-WOY/pub?output=csv"

        try:
            df = pd.read_csv(url_realtime)
            # df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            # --- Auto-detect timestamp column ---
            time_col = next((c for c in df.columns if "time" in c.lower() or "stamp" in c.lower()), None)

            if not time_col:
                st.error(f"❌ No timestamp-like column found. Detected columns: {df.columns.tolist()}")
                st.stop()

            df["Timestamp"] = pd.to_datetime(df[time_col], errors="coerce")


            # --- KPI SECTION ---
            st.markdown("### 📊 Real-time KPI Overview")

            THRESHOLD = 70  # Customize alert threshold
            total_bins = 2  # Fixed (only two bins are being monitored)

            # Use latest record for each bin
            latest_df = df.sort_values("Timestamp").groupby("Bin_ID").tail(1)

            exceed_bins = len(latest_df[latest_df["Fill_Level(%)"] > THRESHOLD])
            resolved_bins = 0
            offline_bins = len(latest_df[latest_df["Status"].str.lower() == "offline"]) if "Status" in df.columns else 0

            # --- Custom KPI Box Styling ---
            st.markdown("""
                <style>
                .kpi-box {
                    background-color: rgba(240, 240, 240, 0.4);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .kpi-box:hover {
                    transform: scale(1.02);
                    background-color: #f1f3f5;
                }
                .kpi-value {
                    font-size: 30px;
                    font-weight: bold;
                    color: #0a0a0a;
                }
                .kpi-label {
                    font-size: 16px;
                    color: #0a0a0a;
                    margin-top: 5px;
                }
                .kpi-section {
                    margin-bottom: 40px; /* Add space below KPI section */
                }
                </style>
            """, unsafe_allow_html=True)

            # --- KPI Display Boxes ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-value'>🗑️ {total_bins}</div>
                        <div class='kpi-label'>Total Bins</div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-value'>🔔 {exceed_bins}</div>
                        <div class='kpi-label'>Exceeded Threshold</div>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-value'>✅ {resolved_bins}</div>
                        <div class='kpi-label'>Resolved</div>
                    </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                    <div class='kpi-box'>
                        <div class='kpi-value'>📴 {offline_bins}</div>
                        <div class='kpi-label'>Offline Devices</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Layout: Top row
            col1, col2 = st.columns([2, 1])

            with col1: 
                # --- MAP SECTION ---
                st.markdown("### 🗺️ Bin Location Map")

                # Define coordinates for each bin manually
                BIN_COORDS = {
                    "Bin_Selatan Terace": [3.141400, 101.717143],  #TRX Selatan Terace
                    "Bin_TRX DMO": [3.141428, 101.717250],  
                    "Bin_A": [3.143907, 101.716167]
                }

                # Center map at TRX
                trx_lat, trx_lon = 3.142844, 101.718299
                m = folium.Map(location=[trx_lat, trx_lon], zoom_start=17)

                # Plot each bin
                for _, row in latest_df.iterrows():
                    bin_id = row["Bin_ID"]
                    fill = row["Fill_Level(%)"]

                    # Pick coordinate based on Bin_ID
                    coords = BIN_COORDS.get(bin_id, [trx_lat, trx_lon])

                    # Color based on fill %
                    if fill >= 70:
                        color = "red"
                    elif fill >= 50:
                        color = "orange"
                    else:
                        color = "green"

                    folium.CircleMarker(
                        location=coords,
                        radius=10,
                        color=color,
                        fill=True,
                        fill_color=color,
                        popup=f"{bin_id}: {fill}% full"
                    ).add_to(m)

                st_folium(m, width=900, height=400)
                st.caption("Map showing each bin’s fixed location in TRX District.")

            with col2:
                # --- NOTIFICATION ALERT PANEL ---
                st.markdown("### 🔔 Real-time Alerts")

                alert_df = latest_df[latest_df["Fill_Level(%)"] >= THRESHOLD]

                if alert_df.empty:
                    st.info("✅ No alerts at the moment. All bins are under control.")
                else:
                    st.markdown("""
                        <style>
                        .alert-box {
                            background-color: rgba(255, 77, 77, 0.1);
                            border-left: 6px solid #ff4d4d;
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 10px;
                            box-shadow: 1px 1px 6px rgba(0,0,0,0.1);
                        }
                        .alert-header {
                            font-weight: bold;
                            color: #d63031;
                        }
                        .alert-time {
                            color: #636e72;
                            font-size: 13px;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    for _, row in alert_df.iterrows():
                        bin_id = row["Bin_ID"]
                        fill = row["Fill_Level(%)"]
                        time = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

                        st.markdown(f"""
                            <div class="alert-box">
                                <div class="alert-header">⚠️ {bin_id} Alert!</div>
                                <div>Fill Level: <b>{fill}%</b> (exceeded {THRESHOLD}%)</div>
                                <div class="alert-time">⏰ {time}</div>
                            </div>
                        """, unsafe_allow_html=True)

            # --- END OF MAP + ALERT PANEL LAYOUT ---
            # Move Bin Status Overview outside of the columns
            st.markdown("---")  # Divider line for clarity

            # --- BIN STATUS OVERVIEW SECTION (Full width below map + alerts) ---
            st.subheader("🗑️ Bin Status Overview")

            try:
                            # Reuse same Google Sheet
                            df = pd.read_csv(url_realtime)

                            # ✅ Ensure timestamp is datetime (supporting day-first format like 18/10/2025)
                            # df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)
                            # --- Auto-detect timestamp column ---
                            time_col = next((c for c in df.columns if "time" in c.lower() or "stamp" in c.lower()), None)

                            if not time_col:
                                st.error(f"❌ No timestamp-like column found. Detected columns: {df.columns.tolist()}")
                                st.stop()

                            df["Timestamp"] = pd.to_datetime(df[time_col], errors="coerce", dayfirst=True)


                            # ✅ Get only the latest row for each Bin_ID
                            latest_df = (
                                df.sort_values("Timestamp")
                                .groupby("Bin_ID")
                                .tail(1)
                                .assign(
                                    BinNum=lambda x: x["Bin_ID"]
                                    .str.extract(r"(\d+)")
                                    .fillna(0)           # Handle missing numbers safely
                                    .astype(int)
                                )
                                .sort_values("BinNum")
                            )

                            # ✅ Arrange bins in rows (3 per row)
                            cols = st.columns(3, gap="large")

                            for i, (idx, row) in enumerate(latest_df.iterrows()):
                                bin_id = row["Bin_ID"]
                                fill = row["Fill_Level(%)"]
                                last = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

                                # Status color
                                if fill >= 70:
                                    status_color = "#ff4d4d"
                                    status_text = "FULL"
                                elif fill >= 40:
                                    status_color = "#ffcc00"
                                    status_text = f"{fill}%"
                                else:
                                    status_color = "#33cc33"
                                    status_text = "EMPTY"

                                # Card with margin-bottom for vertical spacing
                                with cols[i % 3]:
                                    st.markdown(
                                        f"""
                                        <div style="background-color:{status_color}; color:white; 
                                                    border-radius:10px; padding:20px; text-align:center;
                                                    margin-bottom:20px;">
                                            <h3>{bin_id}</h3>
                                            <h2>{status_text}</h2>
                                            <p>{last}</p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

            except Exception as e:
                st.error(f"❌ Failed to load Bin Status Overview: {e}")


        except Exception as e:
            st.error(f"❌ Failed to load Real-time Google Sheet: {e}")
            st.info("Tip: Ensure your Google Sheet is published to web and accessible via CSV format.")


elif selected == "📊 Report":
    st.title("📊 Log Report")
    st.write("🔧 View reports and analyze bin data over time.")

    # Dropdown to choose dataset
    subpage = st.selectbox(
        "Choose Dataset:",
        ["Dummy Data", "Real-time Data"]
    )

    st.markdown("---")

    # --- Choose which Google Sheet ---
    if subpage == "Dummy Data":
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQimwz3tpdodtv2xLKVIx5fVDx1SXaUGzfK6grHmYQSK-ug7Xe0qJsXQct6vyee50l5_AqBxug44E1-/pub?gid=628102932&single=true&output=csv"
    else:
        # Real-time Data
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAiujqFGFtpOsWWhbfZ5mKoY2EpbNTTfjYIDOZaHA8SIGxBecHXmC6FXvQ-swgz3iG9FXNSBdC-WOY/pub?output=csv"

    # --- Common logic for both datasets ---
    try:
        df = pd.read_csv(url)

        # --- Identify key columns ---
        time_col = next((c for c in df.columns if "time" in c.lower() or "timestamp" in c.lower()), None)
        bin_col  = next((c for c in df.columns if "bin" in c.lower()), None)
        fill_col = next((c for c in df.columns if "fill" in c.lower()), None)

        if not (time_col and bin_col and fill_col):
            st.error("Sheet missing required columns. Expected columns containing: 'timestamp', 'bin', 'fill'.")
            st.write("Detected columns:", df.columns.tolist())
            st.stop()

        # --- Clean and format ---
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df["Fill"] = pd.to_numeric(df[fill_col].astype(str).str.replace("%", ""), errors="coerce")

        # --- Remove completely empty rows ---
        df = df.dropna(subset=[time_col, bin_col, "Fill"])

        # --- Build sorted bin list ---
        unique_bins = sorted(df[bin_col].dropna().unique(), key=lambda x: (
            int(re.search(r"(\d+)", str(x)).group(1)) if re.search(r"(\d+)", str(x)) else float("inf"),
            str(x)
        ))
        options = ["All Bins"] + unique_bins

        # --- User select bin ---
        bin_choice = st.selectbox("Choose a bin to view (or All Bins):", options)

        st.markdown("### 📈 Bin Fill Level Over Time")

        # --- Pivot safely using pivot_table (handles duplicates) ---
        pivot_df = (
            df.pivot_table(
                index=time_col, 
                columns=bin_col, 
                values="Fill", 
                aggfunc="mean"   # average duplicates by timestamp
            ).sort_index()
        )

        if not pivot_df.empty:
            pivot_df["Overall Avg"] = pivot_df.mean(axis=1)

        # --- Plot chart ---
        if bin_choice == "All Bins":
            if pivot_df.empty:
                st.info("No data available to plot.")
            else:
                st.line_chart(pivot_df, use_container_width=True)
        else:
            bin_data = df[df[bin_col] == bin_choice].sort_values(time_col)
            if bin_data.empty:
                st.info(f"No data for {bin_choice}.")
            else:
                THRESHOLD = 70  # threshold level
                max_fill = bin_data["Fill"].max(skipna=True)
                y_max = max(THRESHOLD + 10, max_fill + 5)

                # --- Main line chart ---
                chart = (
                    alt.Chart(bin_data)
                    .mark_line(point=True, color="#1f77b4")
                    .encode(
                        x=alt.X(f"{time_col}:T", title="Time"),
                        y=alt.Y("Fill:Q", title="Fill Level (%)", scale=alt.Scale(domain=[0, y_max])),
                        tooltip=[time_col, "Fill"]
                    )
                    .properties(
                        title=f"Fill Level Over Time - {bin_choice}",
                        width="container",
                        height=400
                    )
                )

                # --- Dotted threshold rule ---
                threshold_df = pd.DataFrame({"y": [THRESHOLD]})
                threshold_line = (
                    alt.Chart(threshold_df)
                    .mark_rule(color="orange", strokeDash=[6, 6], strokeWidth=2)
                    .encode(y=alt.Y("y:Q", scale=alt.Scale(domain=[0, y_max])))
                )

                # --- Label for threshold line ---
                label = (
                    alt.Chart(pd.DataFrame({"y": [THRESHOLD], "text": [f"Threshold ({THRESHOLD}%)"]}))
                    .mark_text(align="left", dx=5, dy=-5, color="orange")
                    .encode(y="y:Q", text="text:N")
                )

                st.altair_chart(chart + threshold_line + label, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load Google Sheet / plot data: {e}")


elif selected == "⚙️ Device":
    st.title("⚙️ Device Management")
    st.write("Monitor and manage connected smart waste bins within TRX District in real-time.")

    # --- Custom CSS for search bar & device cards ---
    st.markdown("""
        <style>
        .search-bar {
            background-color: rgba(240, 240, 240, 0.6);
            border-radius: 12px;
            padding: 10px 18px;
            width: 60%;
            display: flex;
            align-items: center;
        }
        .search-input {
            background: transparent;
            border: none;
            outline: none;
            width: 100%;
            font-size: 16px;
        }
        /* --- Device Card Styling --- */
        .device-card {
            background-color: #E0E5E5;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            text-align: left;
            margin-bottom: 25px;
        }
        .device-header {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .device-sub {
            color: #333;
            font-size: 18px;
        }
        .status {
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 14px;
        }
        .online { background-color: #ccf5cc; color: #228B22; }
        .offline { background-color: #ffcccc; color: #a80000; }
        .maintenance { background-color: #fff3cd; color: #8a6d3b; }
        </style>
    """, unsafe_allow_html=True)

    try:
        # --- Load real-time Google Sheet data ---
        url_realtime = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQAiujqFGFtpOsWWhbfZ5mKoY2EpbNTTfjYIDOZaHA8SIGxBecHXmC6FXvQ-swgz3iG9FXNSBdC-WOY/pub?output=csv"
        df = pd.read_csv(url_realtime)

        # --- Data Cleaning & Preparation ---
        # df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        # --- Auto-detect timestamp column ---
        time_col = next((c for c in df.columns if "time" in c.lower() or "stamp" in c.lower()), None)

        if not time_col:
            st.error(f"❌ No timestamp-like column found. Detected columns: {df.columns.tolist()}")
            st.stop()

        df["Timestamp"] = pd.to_datetime(df[time_col], errors="coerce")

        df = df.dropna(subset=["Timestamp", "Bin_ID"])  # remove empty rows

        # Keep latest record for each bin
        latest_df = df.sort_values("Timestamp").groupby("Bin_ID").tail(1)

        # --- Location Mapping (Set manually here) ---
        location_map = {
            "Bin_A": "Barat Walk",
            "Bin_B": "TRX DM",
        }

        latest_df["Location"] = latest_df["Bin_ID"].map(location_map).fillna("Unknown Location")

        # --- Determine Device Status based on Battery Level ---
        def get_status(battery):
            try:
                battery = float(battery)
                if battery >= 50:
                    return "Online"
                elif 20 <= battery < 50:
                    return "Maintenance"
                else:
                    return "Offline"
            except:
                return "Unknown"

        if "Battery_Level(%)" in latest_df.columns:
            latest_df["Device_Status"] = latest_df["Battery_Level(%)"].apply(get_status)
        else:
            st.warning("⚠️ 'Battery_Level(%)' column not found in Google Sheet.")
            st.stop()

        # --- Search Bar ---
        search_term = st.text_input("🔍 Search by Bin ID or Location", "").lower()

        filtered_df = latest_df[
            latest_df["Bin_ID"].str.lower().str.contains(search_term)
            | latest_df["Location"].str.lower().str.contains(search_term)
        ]

        # --- Display Device Cards in Grid Layout ---
        cols = st.columns(3, gap="large")

        for i, (idx, row) in enumerate(filtered_df.iterrows()):
            bin_id = row["Bin_ID"]
            battery = row.get("Battery_Level(%)", "N/A")
            location = row.get("Location", "Unknown Location")
            status = row.get("Device_Status", "Unknown")
            last_updated = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")

            # Status color class
            if status == "Online":
                status_class = "online"
            elif status == "Maintenance":
                status_class = "maintenance"
            else:
                status_class = "offline"

            # Display card
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="device-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="device-header">{bin_id}</div>
                            <span class="status {status_class}">{status}</span>
                        </div>
                        <div class="device-sub">📍 {location}</div>
                        <div style="margin-top:8px; color:black; font-size:18px;">
                            🔋 Battery: <b>{battery}%</b>
                        </div>
                        <div style="margin-top:4px; color:black; font-size:14px;">
                            🕒 Last Updated: {last_updated}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Failed to load Google Sheet: {e}")


elif selected == "👤 Account":
    st.title("👤 Account Settings")

    # --- Custom CSS for modern clean dark UI ---
    st.markdown("""
        <style>
        .settings-container {
            background-color: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            margin-top: 10px;
        }
        .section {
            padding: 15px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .divider {
            border-bottom: 1px solid rgba(255,255,255,0.15);
            margin: 10px 0;
        }
        .label {
            font-weight: 800;
            color: #ffffff;
            font-size: 20px;
            letter-spacing: 0.5px;
        }
        .value {
            color: #f0f0f0;
            font-size: 15px;
            margin-top: 4px;
        }
        .edit-button {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #666;
            border-radius: 8px;
            padding: 6px 14px;
            cursor: pointer;
            font-size: 14px;
            transition: 0.2s;
        }
        .edit-button:hover {
            background-color: #444;
        }
        .profile-section {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-top: 15px;
            margin-bottom: 25px;
        }
        .profile-pic {
            border-radius: 12px;
            width: 50%;
        }
                
        .upload-btn {
            background-color: #2b2b2b;
            border: 1px solid #666;
            color: white;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            margin-right: 10px;
            transition: 0.2s;
        }
        .upload-btn:hover {
            background-color: #444;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Profile Picture Section ---
    st.markdown("<div class='profile-section'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])

    # ✅ Default image path (you can change this)
    default_profile = "C:/Users/user/OneDrive/Documents/FYP/profilepic.jpg"

    # Keep the image in session state
    if "profile_pic" not in st.session_state:
        st.session_state.profile_pic = default_profile

    with col1:
        st.image(st.session_state.profile_pic, caption="", use_container_width=False, width=350)

    with col2:
        uploaded_file = st.file_uploader("Upload new profile picture", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

        if uploaded_file:
            import base64
            image_bytes = uploaded_file.getvalue()
            st.session_state.profile_pic = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
            st.image(st.session_state.profile_pic, width=110)
            st.success("Profile picture updated successfully!")

        remove = st.button("Remove Picture")
        if remove:
            st.session_state.profile_pic = default_profile
            st.warning("Profile picture removed and reset to default.")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Account Info Sections ---
    # st.markdown("<div class='settings-container'>", unsafe_allow_html=True)

    st.markdown("""
        <div class='section'>
            <div>
                <div class='label'>Name</div>
                <div class='value'>Ellya Mysara Binti Mohd Subri</div>
            </div>
            <button class='edit-button'>Edit</button>
        </div>
        <div class='divider'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='section'>
            <div>
                <div class='label'>Contacts</div>
                <div class='value'>Tel: +60 10-219 0196<br>Email: ellya_22006990@utp.edu.my</div>
            </div>
            <button class='edit-button'>Edit</button>
        </div>
        <div class='divider'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='section'>
            <div>
                <div class='label'>Social Media</div>
                <div class='value'>
                    www.linkedin.com/in/ellya-mysara<br>
                </div>
            </div>
            <button class='edit-button'>Edit</button>
        </div>
        <div class='divider'></div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='section'>
            <div>
                <div class='label'>Language</div>
                <div class='value'>English</div>
            </div>
            <button class='edit-button'>Edit</button>
        </div>
        <div class='divider'></div>
    """, unsafe_allow_html=True)

   # --- Theme Toggle Section (horizontally aligned with toggle) ---
    # --- Theme Toggle Section (2-line text aligned with toggle) ---
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Dark"

    # Logic toggle (hidden)
    toggle_state = st.toggle("", value=(st.session_state.theme_mode == "Dark"),
                            label_visibility="collapsed", key="theme_toggle")

    mode = "Dark" if toggle_state else "Light"
    st.session_state.theme_mode = mode

    # --- CSS ---
    st.markdown("""
    <style>
    .theme-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: -40px;
        padding: 15px 0;
    }

    /* Left side (Theme + description) */
    .theme-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .theme-text .label {
        font-weight: 800;
        color: #ffffff;
        font-size: 20px;
        margin-bottom: 3px;
    }

    .theme-text .value {
        color: #f0f0f0;
        font-size: 13px;
        margin: 0;
    }

    /* Toggle style */
    .toggle-box {
        position: relative;
        width: 120px;
        height: 40px;
        border-radius: 25px;
        background: #2b2b2b;
        border: 1px solid #666;
        display: flex;
        align-items: center;
        justify-content: flex-start; /* align text to the left */
        padding-left: 12px; /* spacing for text */
        transition: background 0.3s ease;
        cursor: pointer;
    }

    .toggle-box.dark {
        background: #808080;
        border-color: #444;
    }

    .toggle-text {
        z-index: 2;
        color: #000000;
        font-weight: 600;
        font-size: 13px;
    }

    .toggle-slider {
        position: absolute;
        top: 3px;
        left: 4px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #fff;
        transition: left 0.2s ease, background 0.2s ease;
    }

    .toggle-box.dark .toggle-slider {
        left: 74px;
        background: #C0C0C0;
    }

    /* Hide Streamlit default toggle label */
    div[data-testid="stCheckbox"] label {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render HTML layout ---
    st.markdown(f"""
    <div class="theme-section">
        <div class="theme-text">
            <div class="label">Theme</div>
            <div class="value">Switch between Light or Dark Mode</div>
        </div>
        <div class="toggle-box {'dark' if mode == 'Dark' else ''}">
            <div class="toggle-text">{mode}</div>
            <div class="toggle-slider"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

