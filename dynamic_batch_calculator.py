import streamlit as st
import pandas as pd

st.set_page_config(page_title="Batch Calculator", layout="wide")
st.title("Dynamic Batch Ingredient Calculator (grams)")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    n = st.number_input("Number of ingredients", min_value=1, max_value=50, value=4, step=1)
    rounding = st.selectbox("Rounding", ["No rounding", "1 g", "0.1 g", "0.01 g"], index=1)

round_step = 0.0 if rounding == "No rounding" else float(rounding.split()[0])

# ---------- Inputs ----------
st.subheader("Batch Formula (RFT)")

ingredients = []
old_g = []

for i in range(int(n)):
    col_name, col_weight = st.columns([1.4, 1.0])

    with col_name:
        ing = st.text_input(
            f"Ingredient {i+1}",
            placeholder="Type anything (e.g., Resin A, OG2001, Sugar, Flour...)",
            key=f"ing_{i}"
        ).strip()

    with col_weight:
        label = f"{ing} (g)" if ing else f"Ingredient {i+1} (g)"
        g = st.number_input(
            label,
            min_value=0.0,
            step=1.0,
            format="%.4f",
            key=f"g_{i}"
        )

    ingredients.append(ing if ing else f"Ingredient {i+1}")
    old_g.append(float(g))

total_g = sum(old_g)
st.write(f"**RFT total:** {total_g:,.4f} g")

new_total = st.number_input(
    "New batch total (g)",
    min_value=0.0,
    value=total_g if total_g > 0 else 0.0,
    step=1.0,
    format="%.4f",
    key="new_total_g"
)

# ---------- Calculate ----------
if st.button("Calculate batch"):
    if total_g <= 0:
        st.error("RFT total must be greater than zero.")
    else:
        ratios = [x / total_g for x in old_g]
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
            "Old (g)": [round(x, 4) for x in old_g],
            "New (g)": [round(x, 4) for x in final],
        })

        st.dataframe(df, hide_index=True, use_container_width=True)
        st.write(f"**Check sum:** {sum(final):,.4f} g")
