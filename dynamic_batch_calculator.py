import streamlit as st
import pandas as pd

st.set_page_config(page_title="Batch Calculator", layout="wide")
st.title("Dynamic Batch Ingredient Calculator")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")

    unit = st.selectbox("Unit", ["g", "lb", "pcs"], index=0)

    n = st.number_input("Number of ingredients", min_value=1, max_value=50, value=4, step=1)

    # Rounding options depend on unit
    if unit == "g":
        rounding = st.selectbox("Rounding", ["No rounding", "1 g", "0.1 g", "0.01 g"], index=1)
        round_step = 0.0 if rounding == "No rounding" else float(rounding.split()[0])
    elif unit == "lb":
        rounding = st.selectbox("Rounding", ["No rounding", "0.01 lb", "0.001 lb"], index=0)
        round_step = 0.0 if rounding == "No rounding" else float(rounding.split()[0])
    else:  # pcs
        rounding = st.selectbox("Rounding", ["No rounding", "1 pcs"], index=0)
        round_step = 0.0 if rounding == "No rounding" else 1.0

# ---------- Inputs ----------
st.subheader("Batch Formula (RFT)")

ingredients = []
old_qty = []

for i in range(int(n)):
    col_name, col_qty = st.columns([1.4, 1.0])

    with col_name:
        ing = st.text_input(
            f"Ingredient {i+1}",
            placeholder="Type anything (e.g., OG2001, Flour, Screws...)",
            key=f"ing_{i}"
        ).strip()

    with col_qty:
        label = f"{ing} ({unit})" if ing else f"Ingredient {i+1} ({unit})"
        qty = st.number_input(
            label,
            min_value=0.0,
            step=1.0 if unit in ("g", "pcs") else 0.01,
            format="%.4f" if unit in ("g", "lb") else "%.0f",
            key=f"qty_{i}"
        )

    ingredients.append(ing if ing else f"Ingredient {i+1}")
    old_qty.append(float(qty))

total_qty = sum(old_qty)
st.write(f"**RFT total:** {total_qty:,.4f} {unit}" if unit != "pcs" else f"**RFT total:** {total_qty:,.0f} pcs")

new_total = st.number_input(
    f"New batch total ({unit})",
    min_value=0.0,
    value=total_qty if total_qty > 0 else 0.0,
    step=1.0 if unit in ("g", "pcs") else 0.01,
    format="%.4f" if unit in ("g", "lb") else "%.0f",
    key="new_total"
)

# ---------- Calculate ----------
if st.button("Calculate batch"):
    if total_qty <= 0:
        st.error("RFT total must be greater than zero.")
    else:
        ratios = [x / total_qty for x in old_qty]
        raw = [r * new_total for r in ratios]

        # Rounding + drift correction
        if round_step == 0.0:
            final = raw
        else:
            final = [round(x / round_step) * round_step for x in raw]
            drift = new_total - sum(final)
            biggest_idx = max(range(len(final)), key=lambda i: final[i])
            final[biggest_idx] += drift

        st.subheader("New batch results")

        df = pd.DataFrame({
            "Ingredient": ingredients,
            "Ratio": [round(r, 10) for r in ratios],
            f"Old ({unit})": [round(x, 4) if unit != "pcs" else int(round(x, 0)) for x in old_qty],
            f"New ({unit})": [round(x, 4) if unit != "pcs" else int(round(x, 0)) for x in final],
        })

        st.dataframe(df, hide_index=True, use_container_width=True)
        st.write(
            f"**Check sum:** {sum(final):,.4f} {unit}" if unit != "pcs" else f"**Check sum:** {sum(final):,.0f} pcs"
        )
