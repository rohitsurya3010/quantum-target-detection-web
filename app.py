from __future__ import annotations

from pathlib import Path
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.analysis import ExperimentConfig, run_sweep
from src.detection import roc_curve

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

DEFAULT_ETA = (0.1, 0.2, 0.4, 0.6)
DEFAULT_EPSILON = (0.0, 0.05, 0.1, 0.2)
DETECTOR_NAMES = {
    "quantum": "Quantum entangled",
    "classical_correlated": "Classically correlated",
    "classical_matched_filter": "Classical matched filter",
}
DETECTOR_COLORS = {
    "quantum": "#2D5B91",
    "classical_correlated": "#2D7756",
    "classical_matched_filter": "#8A65A5",
}

st.set_page_config(
    page_title="Quantum Correlation Simulation Platform",
    page_icon="⚛️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 2.2rem; max-width: 1500px;}
      .hero {
        padding: 1.45rem 1.7rem;
        border-radius: 16px;
        background: linear-gradient(125deg, #122031 0%, #2D5B91 100%);
        margin-bottom: 1.1rem;
      }
      .hero h1 {color: #ffffff; margin: 0 0 .4rem 0; font-size: 2rem;}
      .hero p {color: #e8eef5; font-size: 1rem; margin: 0;}
      .kicker {color: #d4e2f1; font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .5rem;}
      .small-muted {color: #667085; font-size: .9rem;}
      div[data-testid="stMetric"] {
        border: 1px solid #d9e0e8; padding: .8rem .95rem;
        border-radius: 12px; background: #fbfcfe;
      }
      div[data-testid="stMetricLabel"] {color: #606872;}
      div.stButton > button[kind="primary"] {background: #2D5B91; border-color: #2D5B91;}
      .section-note {padding: .8rem 1rem; background: #f4f7fa; border-left: 4px solid #2D5B91; border-radius: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="kicker">Quantum computing · Research prototype</div>
      <h1>Quantum Correlation Simulation Platform</h1>
      <p>Weak-target detection under noise · Bell-state simulation · Fair comparison with classical detectors</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Explore the saved experiments or run a new simulation using the project's actual Qiskit and classical detector implementations."
)

def locate_file(filename: str) -> Path | None:
    """Support the normal results/ layout and files copied to repository root."""
    candidates = [RESULTS_DIR / filename, BASE_DIR / filename]
    for path in candidates:
        if path.is_file():
            return path
    return None

@st.cache_data
def load_saved_summary() -> tuple[pd.DataFrame | None, str | None]:
    """Load existing per-condition AUC/Pd/Pfa results, or rebuild from a wide AUC table."""
    path = locate_file("summary.csv")
    if path:
        df = pd.read_csv(path)
        needed = {"detector", "eta", "epsilon", "auc"}
        if needed.issubset(df.columns):
            if "pd_at_zero" not in df:
                df["pd_at_zero"] = float("nan")
            if "pfa_at_zero" not in df:
                df["pfa_at_zero"] = float("nan")
            return normalize_summary(df), str(path.relative_to(BASE_DIR))

    wide_path = locate_file("final_results_table.csv")
    if wide_path:
        wide = pd.read_csv(wide_path)
        wide_columns = {
            "eta", "epsilon", "quantum_auc",
            "classical_correlated_auc", "classical_matched_filter_auc",
        }
        if wide_columns.issubset(wide.columns):
            long = wide.melt(
                id_vars=["eta", "epsilon"],
                value_vars=[
                    "quantum_auc",
                    "classical_correlated_auc",
                    "classical_matched_filter_auc",
                ],
                var_name="detector",
                value_name="auc",
            )
            long["detector"] = long["detector"].replace({
                "quantum_auc": "quantum",
                "classical_correlated_auc": "classical_correlated",
                "classical_matched_filter_auc": "classical_matched_filter",
            })
            long["pd_at_zero"] = float("nan")
            long["pfa_at_zero"] = float("nan")
            return normalize_summary(long), str(wide_path.relative_to(BASE_DIR))
    return None, None

def normalize_summary(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["eta"] = pd.to_numeric(result["eta"], errors="coerce")
    result["epsilon"] = pd.to_numeric(result["epsilon"], errors="coerce")
    result["auc"] = pd.to_numeric(result["auc"], errors="coerce")
    result["pd_at_zero"] = pd.to_numeric(result["pd_at_zero"], errors="coerce")
    result["pfa_at_zero"] = pd.to_numeric(result["pfa_at_zero"], errors="coerce")
    return result.dropna(subset=["eta", "epsilon", "auc"])

@st.cache_data
def load_saved_trials() -> tuple[pd.DataFrame | None, str | None]:
    path = locate_file("trial_statistics.csv")
    if not path:
        return None, None
    df = pd.read_csv(path)
    required = {"detector", "eta", "epsilon", "target_present", "statistic"}
    if not required.issubset(df.columns):
        return None, None
    return df, str(path.relative_to(BASE_DIR))

def normalise_trial_bool(values: pd.Series) -> pd.Series:
    if values.dtype == bool:
        return values
    return values.astype(str).str.strip().str.lower().map(
        {"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}
    )

def plot_roc(trials: pd.DataFrame, eta: float, epsilon: float):
    chosen = trials[
        (pd.to_numeric(trials["eta"], errors="coerce").round(6) == round(float(eta), 6))
        & (pd.to_numeric(trials["epsilon"], errors="coerce").round(6) == round(float(epsilon), 6))
    ].copy()
    chosen["target_present"] = normalise_trial_bool(chosen["target_present"])
    if chosen.empty:
        return None
    fig, ax = plt.subplots(figsize=(7.5, 5.0), dpi=130)
    plotted = 0
    for detector, label in DETECTOR_NAMES.items():
        part = chosen[chosen["detector"] == detector]
        present = part.loc[part["target_present"] == True, "statistic"].dropna().tolist()
        absent = part.loc[part["target_present"] == False, "statistic"].dropna().tolist()
        if present and absent:
            pfa, pd_values, _ = roc_curve(present, absent)
            ax.plot(
                pfa, pd_values, linewidth=2.2,
                color=DETECTOR_COLORS[detector], label=label,
            )
            plotted += 1
    if not plotted:
        plt.close(fig)
        return None
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="#9AA4B2", label="Random baseline")
    ax.set_xlabel("Probability of false alarm (Pfa)")
    ax.set_ylabel("Probability of detection (Pd)")
    ax.set_title(f"ROC comparison · η={eta:.2f}, ε={epsilon:.2f}")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=.22)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    return fig

def plot_auc_vs_parameter(summary: pd.DataFrame, fixed_value: float, parameter: str):
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=130)
    other = "epsilon" if parameter == "eta" else "eta"
    part = summary[(summary[other].round(6) == round(float(fixed_value), 6))]
    for detector, label in DETECTOR_NAMES.items():
        line = part[part["detector"] == detector].sort_values(parameter)
        if not line.empty:
            ax.plot(
                line[parameter], line["auc"], marker="o", linewidth=2,
                label=label, color=DETECTOR_COLORS[detector],
            )
    ax.set_xlabel("Target strength (η)" if parameter == "eta" else "Noise probability (ε)")
    ax.set_ylabel("AUC")
    ax.set_ylim(0.45, 1.03)
    ax.grid(True, alpha=.22)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title(
        f"AUC vs target strength at ε={fixed_value:.2f}"
        if parameter == "eta"
        else f"AUC vs noise at η={fixed_value:.2f}"
    )
    fig.tight_layout()
    return fig

if "active_summary" not in st.session_state:
    initial_summary, initial_source = load_saved_summary()
    st.session_state.active_summary = initial_summary
    st.session_state.active_trials = None
    st.session_state.active_source = f"Saved results: {initial_source}" if initial_summary is not None else "No saved summary loaded"
if "active_trials" not in st.session_state:
    st.session_state.active_trials = None

saved_trials, saved_trial_source = load_saved_trials()
if st.session_state.active_trials is None and saved_trials is not None:
    st.session_state.active_trials = saved_trials

saved_summary = st.session_state.active_summary
if saved_summary is None or saved_summary.empty:
    st.warning(
        "No compatible saved results were found. Upload `results/summary.csv` or "
        "`results/final_results_table.csv` to GitHub, then refresh this app."
    )

with st.sidebar:
    st.header("Simulation controls")
    st.caption("Controls below run the real project simulation when you press the button.")
    eta_values = st.multiselect(
        "Target strengths (η)",
        options=list(DEFAULT_ETA),
        default=list(DEFAULT_ETA),
        format_func=lambda x: f"{x:.2f}",
    )
    epsilon_values = st.multiselect(
        "Noise probabilities (ε)",
        options=list(DEFAULT_EPSILON),
        default=list(DEFAULT_EPSILON),
        format_func=lambda x: f"{x:.2f}",
    )
    trials = st.number_input("Trials per hypothesis", min_value=2, max_value=500, value=100, step=10)
    samples = st.number_input("Observations per trial", min_value=32, max_value=2048, value=256, step=32)
    seed = st.number_input("Random seed", min_value=0, max_value=2_147_483_647, value=20260912, step=1)
    run_clicked = st.button("▶ Run Simulation", type="primary", use_container_width=True)
    st.divider()
    st.caption("This research prototype uses a simplified two-qubit target/noise model.")

if run_clicked:
    if not eta_values:
        st.sidebar.error("Choose at least one target strength η.")
    elif not epsilon_values:
        st.sidebar.error("Choose at least one noise probability ε.")
    else:
        try:
            config = ExperimentConfig(
                eta_values=tuple(float(v) for v in eta_values),
                epsilon_values=tuple(float(v) for v in epsilon_values),
                trials=int(trials),
                quantum_shots=int(samples),
                classical_samples=int(samples),
                seed=int(seed),
            )
            with st.spinner(
                f"Running actual Qiskit and classical simulations for "
                f"{len(eta_values) * len(epsilon_values)} condition(s)…"
            ):
                new_summary, new_trials = run_sweep(config)
            st.session_state.active_summary = normalize_summary(new_summary)
            st.session_state.active_trials = new_trials
            st.session_state.active_source = "New simulation run (held in this browser session)"
            st.success(
                f"Simulation complete: {len(new_summary)} detector-condition rows "
                f"and {len(new_trials)} trial-statistic rows generated."
            )
        except Exception as exc:
            st.error(f"Simulation failed: {exc}")
            st.info("Check the dependency installation and review the terminal/log output for details.")

summary = st.session_state.active_summary
trials_df = st.session_state.active_trials
source_label = st.session_state.active_source

if summary is not None and not summary.empty:
    eta_available = sorted(summary["eta"].unique().tolist())
    eps_available = sorted(summary["epsilon"].unique().tolist())

    st.markdown("### Experiment overview")
    st.caption(source_label)
    a, b, c, d = st.columns(4)
    with a:
        st.metric("Detector models", "3")
    with b:
        st.metric("η/ε conditions", f"{summary[['eta','epsilon']].drop_duplicates().shape[0]}")
    with c:
        st.metric("Mean AUC · quantum", f"{summary.loc[summary.detector == 'quantum', 'auc'].mean():.4f}")
    with d:
        st.metric("Best AUC in current results", f"{summary['auc'].max():.5f}")

    st.divider()
    st.markdown("### Compare a condition")
    f1, f2 = st.columns(2)
    with f1:
        selected_eta = st.selectbox(
            "Target strength η to inspect", eta_available,
            index=0, format_func=lambda x: f"{x:.2f}",
        )
    with f2:
        selected_epsilon = st.selectbox(
            "Noise probability ε to inspect", eps_available,
            index=len(eps_available)-1, format_func=lambda x: f"{x:.2f}",
        )

    selected = summary[
        (summary["eta"].round(6) == round(float(selected_eta), 6))
        & (summary["epsilon"].round(6) == round(float(selected_epsilon), 6))
    ].copy()
    selected["detector_label"] = selected["detector"].map(DETECTOR_NAMES).fillna(selected["detector"])
    selected = selected.sort_values("auc", ascending=False)

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("#### Detector AUC comparison")
        if not selected.empty:
            chart_df = selected.set_index("detector_label")[["auc"]].rename(columns={"auc": "AUC"})
            st.bar_chart(chart_df, y="AUC", color="#2D5B91")
            display_df = selected[["detector_label", "auc", "pd_at_zero", "pfa_at_zero"]].rename(
                columns={
                    "detector_label": "Detector",
                    "auc": "AUC",
                    "pd_at_zero": "Pd at threshold 0",
                    "pfa_at_zero": "Pfa at threshold 0",
                }
            )
            st.dataframe(display_df.round(5), hide_index=True, use_container_width=True)
        else:
            st.info("No results are available for this selected condition.")

    with right:
        st.markdown("#### Interpretation")
        if not selected.empty:
            best = selected.iloc[0]
            st.metric("Highest AUC for this condition", f"{best['auc']:.5f}", label_visibility="visible")
        st.markdown(
            "- **AUC** measures separation across thresholds; it is not accuracy.\n"
            "- **Pd** is the probability of detection at threshold 0.\n"
            "- **Pfa** is the probability of false alarm at threshold 0."
        )
        st.info(
            "Scientific conclusion: detector performance depends on target strength and noise. "
            "The quantum detector does not consistently outperform the classical methods."
        )

    st.divider()
    st.markdown("### Parameter analysis")
    plot1, plot2 = st.columns(2)
    with plot1:
        fig_eta = plot_auc_vs_parameter(summary, selected_epsilon, "eta")
        st.pyplot(fig_eta, use_container_width=True)
        plt.close(fig_eta)
    with plot2:
        fig_eps = plot_auc_vs_parameter(summary, selected_eta, "epsilon")
        st.pyplot(fig_eps, use_container_width=True)
        plt.close(fig_eps)

    st.divider()
    st.markdown("### ROC curve")
    roc_fig = None
    if trials_df is not None and not trials_df.empty:
        roc_fig = plot_roc(trials_df, selected_eta, selected_epsilon)
    if roc_fig is not None:
        st.pyplot(roc_fig, use_container_width=True)
        plt.close(roc_fig)
    else:
        saved_roc = locate_file("final_roc_difficult_condition.png")
        if saved_roc and abs(selected_eta - 0.1) < 1e-6 and abs(selected_epsilon - 0.2) < 1e-6:
            st.image(str(saved_roc), caption="Saved ROC for η=0.10, ε=0.20", use_container_width=True)
        else:
            st.caption(
                "A condition-specific ROC requires `results/trial_statistics.csv`. "
                "Run a simulation above or upload the saved trial-statistics file."
            )

    st.divider()
    st.markdown("### All experiment results")
    with st.expander("View complete summary table"):
        all_view = summary.copy()
        all_view["detector"] = all_view["detector"].map(DETECTOR_NAMES).fillna(all_view["detector"])
        all_view = all_view.rename(columns={
            "detector": "Detector", "eta": "η", "epsilon": "ε", "auc": "AUC",
            "pd_at_zero": "Pd at threshold 0", "pfa_at_zero": "Pfa at threshold 0",
        }).sort_values(["η", "ε", "Detector"])
        st.dataframe(all_view.round(5), hide_index=True, use_container_width=True)

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Download summary CSV",
            data=summary.to_csv(index=False).encode("utf-8"),
            file_name="quantum_detector_summary.csv",
            mime="text/csv",
        )
    with dl2:
        if trials_df is not None and not trials_df.empty:
            st.download_button(
                "Download trial statistics CSV",
                data=trials_df.to_csv(index=False).encode("utf-8"),
                file_name="quantum_detector_trial_statistics.csv",
                mime="text/csv",
            )
        else:
            st.button("Trial CSV available after running a simulation", disabled=True)

st.divider()
st.markdown("### How the simulation works")
st.markdown(
    """
    1. A two-qubit circuit starts in `|00⟩`.
    2. Hadamard and CNOT gates prepare the Bell state `( |00⟩ + |11⟩ ) / √2`.
    3. The actual project target/noise model applies target correlation `η` and binary noise `ε` to the probe qubit.
    4. Qiskit Aer simulates the quantum measurements. Classical detectors use their existing NumPy implementations.
    5. All detectors are evaluated with the shared Pd, Pfa, ROC and AUC metrics.
    """
)
st.caption(
    "Scope: simplified two-qubit educational/research simulation, not a complete physical optical quantum-illumination receiver. "
    "New runs stay in the current session and do not overwrite your original saved results."
)
