import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import date

# Adjust this if your FastAPI runs on a different host/port
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="IEE 305 National Parks", layout="wide")

st.title("🌲 IEE 305 – National Parks Explorer")
st.write("Frontend built with Streamlit, backend served by FastAPI.")

# -------------------------------------------------------------
# Helper to call the API
# -------------------------------------------------------------
def get_data(endpoint: str, params=None):
    """
    endpoint: string without leading slash, e.g. 'parks', 'events',
              'stats/events-per-park'
    """
    url = f"{API_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error calling `{url}`: {e}")
        return None

# -------------------------------------------------------------
# Sidebar navigation
# -------------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Parks", "Park Detail", "Visitor Centers", "Events Explorer", "Stats Dashboard"]
)

# -------------------------------------------------------------
# HOME
# -------------------------------------------------------------
if page == "Home":
    st.subheader("Welcome")
    st.markdown(
        """
        This app demonstrates the IEE 305 term project:

        - **FastAPI backend** provides data using:
          - `/parks`
          - `/visitor-centers`
          - `/events`
          - `/stats/events-per-park`
          - `/stats/visitor-centers-per-park`
        - **Streamlit frontend** displays and filters that data.

        Use the sidebar to switch between views.
        """
    )

# -------------------------------------------------------------
# PARKS – updated
# -------------------------------------------------------------
elif page == "Parks":
    st.header("🏞 Parks")

    col_filters = st.columns(2)
    with col_filters[0]:
        state_code = st.text_input("Filter by state (2-letter code, e.g. CA)", "")
    with col_filters[1]:
        max_fee = st.number_input(
            "Max entrance fee (example: 35)",
            min_value=0,
            value=0,
            step=1,
        )

    with st.expander("Need help? Tap to see available state codes"):
        st.markdown(
            """
            These are the states currently represented in this project:

            - **AZ** – Arizona  
            - **CA** – California  
            - **UT** – Utah  
            - **ID** – Idaho  
            - **CO** – Colorado  
            """
        )

    if st.button("Load Parks"):
        params = {}
        if state_code.strip():
            params["state_code"] = state_code.strip().upper()
        if max_fee > 0:
            params["max_fee"] = max_fee

        data = get_data("parks", params=params if params else None)

        if data is not None:
            parks = data if isinstance(data, list) else data
            st.write(f"Loaded **{len(parks)}** parks from `/parks`.")
            st.dataframe(parks, use_container_width=True)
        else:
            st.warning("No parks found with the current filters.")

# -------------------------------------------------------------
# PARK DETAIL – updated
# -------------------------------------------------------------
elif page == "Park Detail":
    st.header("🌲🏕 Park Detail")

    with st.expander("Need help? Filter park codes by state"):
        help_state = st.text_input(
            "Enter state code (e.g. CA, UT, AZ, ID, CO)",
            "",
            key="help_state_code",
        )

        if st.button("Show parks in this state", key="show_parks_by_state"):
            params = {}
            if help_state.strip():
                params["state_code"] = help_state.strip()
            parks_in_state = get_data("parks", params=params if params else None)

            if isinstance(parks_in_state, list) and parks_in_state:
                rows = [
                    {"park_code": p.get("park_code", ""), "name": p.get("name", "")}
                    for p in parks_in_state
                ]
                st.table(rows)
            else:
                st.info("No parks found for that state code.")

    park_code = st.text_input(
        "Enter park code (e.g. YOSE, ZION, YELL)",
        "",
        key="park_detail_code",
    )

    if st.button("Load Park Detail", key="load_park_detail") and park_code.strip():
        code = park_code.strip()

        col1, col2 = st.columns([2, 3])

        state_centroids = {
            "CA": {"lat": 36.7783, "lon": -119.4179},
            "UT": {"lat": 39.32098, "lon": -111.0937},
            "AZ": {"lat": 34.0489, "lon": -111.0937},
            "ID": {"lat": 44.0682, "lon": -114.7420},
            "CO": {"lat": 39.5501, "lon": -105.7821},
        }

        with col1:
            st.subheader("Park Info")

            park = get_data(f"parks/{code}")
            if park and isinstance(park, dict):
                state = park.get("state_code", "N/A")
                pcode = park.get("park_code", "N/A")
                name = park.get("name", "N/A")
                total_activities = park.get("total_activities", "N/A")
                entrance_fee = park.get("entrance_fee", "N/A")

                centroid = state_centroids.get(state)
                if centroid is not None:
                    map_df = pd.DataFrame([centroid])
                    st.map(map_df, zoom=5)

                fee_text = (
                    f"{entrance_fee}"
                    if not isinstance(entrance_fee, (int, float))
                    else f"{entrance_fee:.0f}"
                )

                st.markdown(
                    f"""
                    **State code:** {state}  
                    **Park code:** {pcode}  
                    **Name:** {name}  
                    **Total activities:** {total_activities}  
                    **Entrance fee (vehicle):** ${fee_text}
                    """
                )
            else:
                st.info("No park found for that code.")

        with col2:
            st.subheader("📍 Visitor Centers")
            vcs = get_data("visitor-centers", params={"park_code": code})
            if isinstance(vcs, list) and len(vcs) > 0:
                st.table(vcs)
            else:
                st.info("No visitor centers found for this park.")

            st.subheader("🎫 Events")
            events = get_data("events", params={"park_code": code})
            if isinstance(events, list) and len(events) > 0:
                df_events = pd.DataFrame(events)
                preferred_order = [
                    "event_title",
                    "start_date",
                    "end_date",
                    "is_free",
                    "location",
                    "park_code",
                    "event_id",
                ]
                existing = [c for c in preferred_order if c in df_events.columns]
                remaining = [c for c in df_events.columns if c not in existing]
                df_events = df_events[existing + remaining]

                st.dataframe(df_events, use_container_width=True)
            else:
                st.info("No events found for this park.")

    st.markdown(
        "This view demonstrates multiple endpoints in one place:\n"
        "- `GET /parks/{park_code}`\n"
        "- `GET /visitor-centers?park_code=...`\n"
        "- `GET /events?park_code=...`"
    )

# -------------------------------------------------------------
# VISITOR CENTERS – updated
# -------------------------------------------------------------
elif page == "Visitor Centers":
    st.header("📍 Visitor Centers")

    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            state_code = st.text_input(
                "Filter by state code (optional, e.g. CA)",
                "",
                key="vc_state_code",
            )
        with col2:
            park_code = st.text_input(
                "Filter by park code (optional, e.g. YOSE, ZION)",
                "",
                key="vc_park_code",
            )

        st.caption(
            "Enter a park code to see visitor centers for that park, "
            "or a state code to see visitor centers for all parks in that state. "
            "Leave both blank to see centers for all parks."
        )

        load_vc = st.button("Load Visitor Centers", key="vc_load_button")

    if load_vc:
        state = state_code.strip().upper()
        pcode = park_code.strip().upper()

        def show_centers_for_park(park_code_value: str, park_name_value: str | None = None):
            vcs = get_data("visitor-centers", params={"park_code": park_code_value})
            if not (isinstance(vcs, list) and vcs):
                return

            name_val = park_name_value
            if not name_val:
                park_info = get_data(f"parks/{park_code_value}")
                if isinstance(park_info, dict):
                    name_val = park_info.get("name", "")

            header = park_code_value
            if name_val:
                header = f"{park_code_value} – {name_val}"
            st.subheader(header)

            df = pd.DataFrame(vcs)
            if "center_name" in df.columns:
                df = df[["center_name"]].rename(columns={"center_name": "Visitor Center"})
            st.table(df)

        if pcode:
            show_centers_for_park(pcode)
        elif state:
            parks = get_data("parks", params={"state_code": state})
            if isinstance(parks, list) and parks:
                for park in parks:
                    code_val = park.get("park_code", "")
                    name_val = park.get("name", "")
                    if code_val:
                        show_centers_for_park(code_val, name_val)
            else:
                st.info("No parks found for that state code.")
        else:
            all_vcs = get_data("visitor-centers")
            if isinstance(all_vcs, list) and all_vcs:
                df_all = pd.DataFrame(all_vcs)
                if "park_code" in df_all.columns and "center_name" in df_all.columns:
                    for code_val in sorted(df_all["park_code"].unique()):
                        subset = df_all[df_all["park_code"] == code_val]
                        park_info = get_data(f"parks/{code_val}")
                        name_val = park_info.get("name") if isinstance(park_info, dict) else ""
                        st.subheader(f"{code_val} – {name_val}")
                        df = subset[["center_name"]].rename(
                            columns={"center_name": "Visitor Center"}
                        )
                        st.table(df)
                else:
                    st.dataframe(df_all, use_container_width=True)
            else:
                st.info("No visitor centers found in the database.")

# -------------------------------------------------------------
# EVENTS EXPLORER – updated
# -------------------------------------------------------------
elif page == "Events Explorer":
    st.header("🎫 Events Explorer")

    with st.expander("Need help? Show park codes by state"):
        state_choice = st.selectbox(
            "Select a state",
            ["", "AZ", "CA", "UT", "ID", "CO"],
            format_func=lambda x: "Select..." if x == "" else x,
            key="events_state_helper",
        )
        if state_choice:
            parks_in_state = get_data("parks", params={"state_code": state_choice})
            if isinstance(parks_in_state, list) and parks_in_state:
                rows = [
                    {"park_code": p.get("park_code", ""), "name": p.get("name", "")}
                    for p in parks_in_state
                ]
                st.table(rows)
            else:
                st.info("No parks found for that state code.")

    st.write("Filter events by park code and optional criteria.")

    col1, col2, col3 = st.columns(3)
    with col1:
        park_code = st.text_input("Park code (optional, e.g. YOSE, ZION, YELL)", "")
        free_only = st.checkbox("Free events only", value=False)
    with col2:
        start_date = st.date_input("Start date (optional)", value=None)
    with col3:
        end_date = st.date_input("End date (optional)", value=None)

    if st.button("Load Events"):
        params = {}
        if park_code.strip():
            params["park_code"] = park_code.strip().upper()
        if free_only:
            params["free_only"] = "true"
        if isinstance(start_date, date):
            params["start"] = start_date.isoformat()
        if isinstance(end_date, date):
            params["end"] = end_date.isoformat()

        data = get_data("events", params=params if params else None)

        if data is not None:
            events = data if isinstance(data, list) else data
            st.write(f"Loaded **{len(events)}** events from `/events`.")

            df_events = pd.DataFrame(events)
            preferred_order = [
                "event_title",
                "park_code",
                "start_date",
                "end_date",
                "is_free",
                "id",
            ]
            if not df_events.empty:
                existing = [c for c in preferred_order if c in df_events.columns]
                remaining = [c for c in df_events.columns if c not in existing]
                df_events = df_events[existing + remaining]

                if "is_free" in df_events.columns:
                    df_events["is_free"] = df_events["is_free"].map(
                        lambda x: "✅" if bool(x) else ""
                    )
                    styled = df_events.style.applymap(
                        lambda v: "color: red; font-weight: bold;" if v == "✅" else "",
                        subset=["is_free"],
                    )
                    st.dataframe(styled, use_container_width=True)
                else:
                    st.dataframe(df_events, use_container_width=True)
        else:
            st.warning("No events found with the current filters.")

# -------------------------------------------------------------
# STATS DASHBOARD – final layout
# -------------------------------------------------------------
elif page == "Stats Dashboard":
    st.header("📊 Stats Dashboard")

    # ------------- helper for charts ---------------------------
    def render_bar_chart(df: pd.DataFrame, value_col: str, title_suffix: str):
        """Common chart styling: smaller, spaced, names on x-axis, descending."""
        if df.empty or value_col not in df.columns:
            return
        df_plot = df.copy()
        df_plot[value_col] = pd.to_numeric(df_plot[value_col], errors="coerce").fillna(0)
        df_plot = df_plot.sort_values(value_col, ascending=False)

        # space between table and chart
        st.markdown("&nbsp;", unsafe_allow_html=True)

        chart = (
            alt.Chart(df_plot)
            .mark_bar()
            .encode(
                x=alt.X("name:N", sort="-y", title="Park"),
                y=alt.Y(f"{value_col}:Q", title="Number per park"),
                tooltip=["park_code", "name", value_col],
            )
            .properties(width=600, height=250, title=title_suffix)
        )
        st.altair_chart(chart, use_container_width=False)

    # =========================================================
    # 1) EVENTS PER PARK
    # =========================================================
    st.subheader("Events per Park")

    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.number_input(
            "Year",
            min_value=1900,
            max_value=2100,
            value=2025,
            step=1,
        )
    with c2:
        events_ranking = st.selectbox(
            "Rankings",
            ["All parks", "Above average", "Below average", "Zero", "Top 5"],
            key="events_ranking",
        )
    with c3:
        load_events_stats = st.button("Load Event Stats")

    if load_events_stats:
        rows = get_data("stats/events-per-park", params={"year": str(year)})
        if isinstance(rows, list) and rows:
            df_stats = pd.DataFrame(rows)
            if "event_count" in df_stats.columns:
                df_stats["event_count"] = pd.to_numeric(
                    df_stats["event_count"], errors="coerce"
                ).fillna(0)

                mean_val = df_stats["event_count"].mean()

                if events_ranking == "Above average":
                    df_stats = df_stats[df_stats["event_count"] > mean_val]
                elif events_ranking == "Below average":
                    df_stats = df_stats[df_stats["event_count"] < mean_val]
                elif events_ranking == "Zero":
                    df_stats = df_stats[df_stats["event_count"] == 0]
                elif events_ranking == "Top 5":
                    df_stats = df_stats.sort_values("event_count", ascending=False).head(5)

                df_stats = df_stats.sort_values("event_count", ascending=False)
                st.dataframe(df_stats, use_container_width=True)
                render_bar_chart(df_stats, "event_count", "Events per park")
            else:
                st.dataframe(df_stats, use_container_width=True)
        else:
            st.info("No event statistics available for that year.")

    # =========================================================
    # 2) VISITOR CENTERS PER PARK
    # =========================================================
    st.subheader("Visitor Centers per Park")

    c4, c5, c6 = st.columns(3)
    with c4:
        min_centers = st.number_input(
            "Minimum centers",
            min_value=0,
            value=0,
            step=1,
            key="min_centers",
        )
    with c5:
        centers_ranking = st.selectbox(
            "Rankings",
            ["All parks", "Above average", "Below average", "Top 5", "At least one center"],
            key="centers_ranking",
        )
    with c6:
        load_center_stats = st.button("Load Center Stats")

    if load_center_stats:
        params = {}
        if min_centers > 0:
            params["min_centers"] = str(min_centers)

        rows = get_data("stats/visitor-centers-per-park", params=params if params else None)
        if isinstance(rows, list) and rows:
            df_centers = pd.DataFrame(rows)
            if "center_count" in df_centers.columns:
                df_centers["center_count"] = pd.to_numeric(
                    df_centers["center_count"], errors="coerce"
                ).fillna(0)

                mean_val = df_centers["center_count"].mean()

                if centers_ranking == "Above average":
                    df_centers = df_centers[df_centers["center_count"] > mean_val]
                elif centers_ranking == "Below average":
                    df_centers = df_centers[df_centers["center_count"] < mean_val]
                elif centers_ranking == "Top 5":
                    df_centers = df_centers.sort_values(
                        "center_count", ascending=False
                    ).head(5)
                elif centers_ranking == "At least one center":
                    df_centers = df_centers[df_centers["center_count"] >= 1]

                df_centers = df_centers.sort_values("center_count", ascending=False)
                st.dataframe(df_centers, use_container_width=True)
                render_bar_chart(df_centers, "center_count", "Visitor centers per park")
            else:
                st.dataframe(df_centers, use_container_width=True)
        else:
            st.info("No visitor-center statistics available with those filters.")

    # =========================================================
    # 3) ACTIVITIES PER PARK
    # =========================================================
    st.subheader("Activities per Park")

    c7, c8 = st.columns([1, 1])
    with c7:
        activities_ranking = st.selectbox(
            "Rankings",
            ["All parks", "Above average", "Below average", "Top 5"],
            key="activities_ranking",
        )
    with c8:
        load_activities = st.button("Load Activity Stats")

    if load_activities:
        parks = get_data("parks")
        if isinstance(parks, list) and parks:
            df_act = pd.DataFrame(parks)
            if "total_activities" in df_act.columns:
                df_act["total_activities"] = pd.to_numeric(
                    df_act["total_activities"], errors="coerce"
                ).fillna(0)

                mean_val = df_act["total_activities"].mean()

                if activities_ranking == "Above average":
                    df_act = df_act[df_act["total_activities"] > mean_val]
                elif activities_ranking == "Below average":
                    df_act = df_act[df_act["total_activities"] < mean_val]
                elif activities_ranking == "Top 5":
                    df_act = df_act.sort_values(
                        "total_activities", ascending=False
                    ).head(5)

                df_act = df_act.sort_values("total_activities", ascending=False)
                df_display = df_act[["park_code", "name", "total_activities"]]
                st.dataframe(df_display, use_container_width=True)
                render_bar_chart(df_display, "total_activities", "Activities per park")
            else:
                st.dataframe(df_act, use_container_width=True)
        else:
            st.info("No activity statistics available.")
