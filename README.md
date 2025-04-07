![GRAS_Curve_Editor](https://github.com/user-attachments/assets/2a841253-d3e1-43f3-8c33-b94b994e4af4)

📘 GrasCurveEditor – Luma Correction Curve Editor for Samsung Sensors

What this program does:

GrasCurveEditor is a GUI tool designed for editing luminance correction curves (also known as GRAS or Luma Correction) used in Samsung image sensors. It is primarily intended for developers working with camera tuning, ISP bring-up, or raw sensor analysis.
🧠 What is GRAS / Luma Correction?

GRAS stands for Gain Response Adjustment System (or internally just “luma correction”). It’s a mechanism inside the image sensor or ISP that adjusts the brightness (luminance) across different parts of the image to compensate for:

    🔆 Lens shading (vignetting)

    💡 Brightness fall-off near the corners

    🌗 Uneven exposure across zones

Instead of a simple brightness gain, GRAS applies a zone-based correction using parametric curves. These are defined by:

    tmpr — zone trigger or priority (e.g. light level or temperature index)

    alpha[0–3] — parameters defining brightness amplification in mid/high zones

    beta[0–3] — parameters influencing dark zone correction

Each set of (tmpr, alpha[], beta[]) defines one zone (up to 7 zones total). The correction curve works like this:

Output = Input × (alpha · Input + beta)

✅ What this tool supports:

    📂 Open .txt files with WBlock data from tuning tools or I2C logs

    ✍️ Edit alpha[] and beta[] values interactively by zone

    📊 Visualize correction curves ("before vs after")

    💾 Save files with full formatting and comments preserved

    🧩 Zone detection is automatic based on register addresses (0x3164–0x31F0 range)

The tool is written in pure Python (Tkinter) and does not require any installation beyond standard Python with matplotlib.
