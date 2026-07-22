from pathlib import Path
import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
CURRENT_SWEEP_FILE = DATA_DIR / "awe_current_temperature_1bar.csv"
PRESSURE_SWEEP_FILE = DATA_DIR / "awe_pressure_temperature_90a.csv"

st.set_page_config(
    page_title="AWE Digital Twin Explorer",
    layout="wide",
    page_icon="⚡",
)


def validate_columns(df: pd.DataFrame, required: set[str], dataset_name: str) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {', '.join(sorted(missing))}"
        )


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not CURRENT_SWEEP_FILE.exists():
        raise FileNotFoundError(f"Missing dataset: {CURRENT_SWEEP_FILE}")
    if not PRESSURE_SWEEP_FILE.exists():
        raise FileNotFoundError(f"Missing dataset: {PRESSURE_SWEEP_FILE}")

    current_df = pd.read_csv(CURRENT_SWEEP_FILE)
    pressure_df = pd.read_csv(PRESSURE_SWEEP_FILE)

    validate_columns(
        current_df,
        {"Temperature", "Current", "Voltage", "Theta"},
        "Current-temperature sweep",
    )
    validate_columns(
        pressure_df,
        {"Temperature", "Pressure", "Voltage", "Theta"},
        "Pressure-temperature sweep",
    )

    # Condition 3 is explicitly synthetic and is retained only as a UI demonstration.
    temperatures = np.array([273, 298, 323, 353, 373], dtype=float)
    pressures = np.array([1, 5, 10, 20, 30], dtype=float)
    currents = np.linspace(0, 100, 21)

    synthetic_rows = []
    for temperature in temperatures:
        for pressure in pressures:
            for current in currents:
                voltage = (
                    1.23
                    + 0.005 * current
                    + 0.02 * np.log(pressure)
                    - 0.001 * (temperature - 273)
                )
                synthetic_rows.append(
                    {
                        "Temperature": temperature,
                        "Pressure": pressure,
                        "Current": round(float(current), 1),
                        "Voltage": float(voltage),
                    }
                )

    synthetic_df = pd.DataFrame(synthetic_rows)
    return current_df, pressure_df, synthetic_df


def find_row(
    df: pd.DataFrame,
    filters: dict[str, float],
) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, value in filters.items():
        mask &= np.isclose(df[column].astype(float), float(value))

    matches = df.loc[mask]
    if matches.empty:
        raise LookupError(f"No model result was found for: {filters}")
    return matches.iloc[0]


def clear_history(key: str) -> None:
    st.session_state.history[key] = []


def draw_plot(
    placeholder,
    history: list[dict],
    animation_data: tuple[float, float, float, float] | None = None,
) -> None:
    figure = go.Figure()
    voltages = [float(item["V"]) for item in history]

    if not history and animation_data is None:
        figure.update_layout(
            title="Waiting for an operating point",
            xaxis={"title": "Time Step", "range": [-0.5, 1], "dtick": 1},
            yaxis={"title": "Cell Voltage (V)", "range": [1.1, 2.2]},
            template="plotly_white",
            height=500,
        )
        placeholder.plotly_chart(figure, use_container_width=True)
        return

    if history:
        figure.add_trace(
            go.Scatter(
                x=list(range(len(history))),
                y=voltages,
                mode="lines+markers",
                line={"width": 2},
                marker={"size": 11, "line": {"width": 1}},
                name="Recorded operating points",
                customdata=[
                    "<br>".join(
                        f"{name}: {value:.4f}" if isinstance(value, float)
                        else f"{name}: {value}"
                        for name, value in item.items()
                        if name != "V"
                    )
                    for item in history
                ],
                hovertemplate=(
                    "Step %{x}<br>Voltage: %{y:.4f} V"
                    "<br>%{customdata}<extra></extra>"
                ),
            )
        )

    if animation_data is not None:
        current_x, current_y, start_x, start_y = animation_data
        figure.add_trace(
            go.Scatter(
                x=[start_x, current_x],
                y=[start_y, current_y],
                mode="lines",
                line={"width": 3, "dash": "dot"},
                name="Transition",
                hoverinfo="skip",
            )
        )
        figure.add_trace(
            go.Scatter(
                x=[current_x],
                y=[current_y],
                mode="markers",
                marker={"size": 17, "symbol": "star"},
                name="Moving point",
                hovertemplate="Voltage: %{y:.4f} V<extra></extra>",
            )
        )
        voltages.append(float(current_y))

    minimum = min(voltages) if voltages else 1.0
    maximum = max(voltages) if voltages else 2.0
    span = maximum - minimum
    padding = 0.05 if span < 0.05 else span * 0.20

    figure.update_layout(
        title="Cell-Voltage Timeline",
        xaxis={
            "range": [-0.5, max(len(history) + 1, 1)],
            "dtick": 1,
            "title": "Time Step",
        },
        yaxis={
            "range": [minimum - padding, maximum + padding],
            "tickformat": ".4f",
            "title": "Cell Voltage (V)",
        },
        template="plotly_white",
        height=500,
        showlegend=False,
        hovermode="closest",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
    )
    placeholder.plotly_chart(figure, use_container_width=True)


def animate_transition(placeholder, key: str, new_entry: dict) -> None:
    history = st.session_state.history[key]

    if not history:
        history.append(new_entry)
        draw_plot(placeholder, history)
        return

    start_x = len(history) - 1
    start_voltage = float(history[-1]["V"])
    target_voltage = float(new_entry["V"])
    frames = 15

    for frame in range(1, frames + 1):
        fraction = frame / frames
        current_x = start_x + fraction
        current_voltage = start_voltage + (target_voltage - start_voltage) * fraction
        draw_plot(
            placeholder,
            history,
            animation_data=(current_x, current_voltage, start_x, start_voltage),
        )
        time.sleep(0.04)

    history.append(new_entry)
    draw_plot(placeholder, history)


try:
    current_df, pressure_df, synthetic_df = load_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Data-loading error: {exc}")
    st.stop()


if "history" not in st.session_state:
    st.session_state.history = {"cond1": [], "cond2": [], "cond3": []}


st.sidebar.title("Operating Mode")
mode = st.sidebar.radio(
    "Select a dataset:",
    (
        "1. Current and temperature sweep at ≈1 bar",
        "2. Pressure and temperature sweep at 90 A",
        "3. Synthetic T, P, and I demonstration",
    ),
)

condition_key = f"cond{mode[0]}"

st.sidebar.markdown("---")
if st.sidebar.button("Clear current timeline", use_container_width=True):
    clear_history(condition_key)
    st.rerun()

st.title("⚡ Alkaline Water Electrolyzer Digital Twin Explorer")
st.caption(
    "Select an operating point and add it to the timeline to inspect the "
    "predicted cell-voltage response."
)

new_entry: dict[str, float] = {}

if condition_key == "cond1":
    left, right = st.columns(2)

    temperatures = sorted(current_df["Temperature"].unique())
    with left:
        temperature = st.select_slider("Temperature (K)", options=temperatures)

    currents = sorted(
        current_df.loc[
            np.isclose(current_df["Temperature"], temperature), "Current"
        ].unique()
    )
    with right:
        current = st.select_slider("Current (A)", options=currents)

    row = find_row(
        current_df,
        {"Temperature": temperature, "Current": current},
    )
    new_entry = {
        "T (K)": float(temperature),
        "I (A)": float(current),
        "V": float(row["Voltage"]),
        "Bubble coverage": float(row["Theta"]),
    }
    if "Hflux" in row.index:
        new_entry["H₂ flux"] = float(row["Hflux"])

elif condition_key == "cond2":
    left, right = st.columns(2)

    temperatures = sorted(pressure_df["Temperature"].unique())
    with left:
        temperature = st.select_slider("Temperature (K)", options=temperatures)

    pressures = sorted(
        pressure_df.loc[
            np.isclose(pressure_df["Temperature"], temperature), "Pressure"
        ].unique()
    )
    with right:
        pressure = st.select_slider("Pressure (bar)", options=pressures)

    row = find_row(
        pressure_df,
        {"Temperature": temperature, "Pressure": pressure},
    )
    new_entry = {
        "T (K)": float(temperature),
        "P (bar)": float(pressure),
        "V": float(row["Voltage"]),
        "Bubble coverage": float(row["Theta"]),
    }

else:
    st.warning(
        "This mode uses a synthetic demonstration equation. It is not a result "
        "from the validated Simulink datasets."
    )
    first, second, third = st.columns(3)

    temperatures = sorted(synthetic_df["Temperature"].unique())
    with first:
        temperature = st.select_slider("Temperature (K)", options=temperatures)

    pressures = sorted(
        synthetic_df.loc[
            np.isclose(synthetic_df["Temperature"], temperature), "Pressure"
        ].unique()
    )
    with second:
        pressure = st.select_slider("Pressure (bar)", options=pressures)

    currents = sorted(
        synthetic_df.loc[
            np.isclose(synthetic_df["Temperature"], temperature)
            & np.isclose(synthetic_df["Pressure"], pressure),
            "Current",
        ].unique()
    )
    with third:
        current = st.select_slider("Current (A)", options=currents)

    row = find_row(
        synthetic_df,
        {
            "Temperature": temperature,
            "Pressure": pressure,
            "Current": current,
        },
    )
    new_entry = {
        "T (K)": float(temperature),
        "P (bar)": float(pressure),
        "I (A)": float(current),
        "V": float(row["Voltage"]),
    }


metric_columns = st.columns(4)
metric_columns[0].metric("Predicted voltage", f"{new_entry['V']:.4f} V")

if "Bubble coverage" in new_entry:
    metric_columns[1].metric(
        "Bubble coverage",
        f"{new_entry['Bubble coverage']:.4f}",
    )

if "H₂ flux" in new_entry:
    metric_columns[2].metric("Hydrogen flux", f"{new_entry['H₂ flux']:.6f}")

with metric_columns[3]:
    add_point = st.button(
        "Add operating point",
        type="primary",
        use_container_width=True,
    )

plot_placeholder = st.empty()

if add_point:
    animate_transition(plot_placeholder, condition_key, new_entry)
else:
    draw_plot(plot_placeholder, st.session_state.history[condition_key])

history = st.session_state.history[condition_key]
if history:
    with st.expander("View logged operating points"):
        history_df = pd.DataFrame(history)
        history_df.index.name = "Step"
        numeric_formats = {
            column: "{:.4f}"
            for column in history_df.select_dtypes(include="number").columns
        }
        st.dataframe(
            history_df.style.format(numeric_formats),
            use_container_width=True,
        )

with st.expander("Dataset information"):
    if condition_key == "cond1":
        st.write(
            f"Rows: **{len(current_df):,}** | "
            f"Temperatures: **{current_df['Temperature'].nunique()}** | "
            f"Current values: **{current_df['Current'].nunique()}**"
        )
    elif condition_key == "cond2":
        st.write(
            f"Rows: **{len(pressure_df):,}** | "
            f"Temperatures: **{pressure_df['Temperature'].nunique()}** | "
            f"Pressure values: **{pressure_df['Pressure'].nunique()}**"
        )
    else:
        st.write("Synthetic demonstration dataset generated inside the app.")
