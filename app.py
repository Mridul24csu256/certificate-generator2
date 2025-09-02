import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import numpy as np
import io

st.title("📜 Certificate Generator")

# Upload certificate template
template_file = st.file_uploader("Upload Certificate Template (PNG/JPG)", type=["png", "jpg", "jpeg"])

# Upload Excel/CSV data
data_file = st.file_uploader("Upload Data File (CSV/XLSX)", type=["csv", "xlsx"])

# ✅ Built-in fonts (place .ttf files in a `fonts` folder inside repo)
FONT_LIBRARY = {
    "Arial": "fonts/arial.ttf",
    "Times New Roman": "fonts/times.ttf",
    "Courier New": "fonts/cour.ttf"
}

if template_file and data_file:
    # Load template
    template = Image.open(template_file).convert("RGB")
    template_np = np.array(template)  # ✅ Convert to numpy for st_canvas

    # Load data
    if data_file.name.endswith(".csv"):
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file)

    st.write("Preview of Uploaded Data:")
    st.dataframe(df.head())

    # Select columns to use
    selected_columns = st.multiselect("Select columns to use in certificate", df.columns.tolist())

    text_settings = {}
    for col in selected_columns:
        st.subheader(f"⚙️ Settings for {col}")

        # Canvas for positioning
        st.write("Drag to position:")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=0,
            stroke_color="",
            background_image=template_np,
            update_streamlit=True,
            height=template.height,
            width=template.width,
            drawing_mode="transform",
            key=f"canvas_{col}"
        )

        # Save position
        x, y = 100, 100
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
            obj = canvas_result.json_data["objects"][-1]
            x, y = int(obj["left"]), int(obj["top"])

        # Font selection
        font_choice = st.selectbox(f"Font for {col}", list(FONT_LIBRARY.keys()), key=f"font_{col}")
        font_size = st.slider(f"Font Size for {col}", 10, 100, 30, key=f"size_{col}")
        font_color = st.color_picker(f"Font Color for {col}", "#000000", key=f"color_{col}")

        text_settings[col] = {
            "x": x,
            "y": y,
            "font": FONT_LIBRARY[font_choice],
            "size": font_size,
            "color": font_color
        }

    if st.button("🎉 Generate Certificates"):
        output_zip = io.BytesIO()
        import zipfile
        with zipfile.ZipFile(output_zip, "w") as zipf:
            for idx, row in df.iterrows():
                cert = template.copy()
                draw = ImageDraw.Draw(cert)
                for col, settings in text_settings.items():
                    font = ImageFont.truetype(settings["font"], settings["size"])
                    draw.text((settings["x"], settings["y"]), str(row[col]), font=font, fill=settings["color"])
                cert_bytes = io.BytesIO()
                cert.save(cert_bytes, format="PNG")
                zipf.writestr(f"certificate_{idx+1}.png", cert_bytes.getvalue())

        st.success("✅ Certificates generated successfully!")
        st.download_button(
            "⬇️ Download All Certificates as ZIP",
            data=output_zip.getvalue(),
            file_name="certificates.zip",
            mime="application/zip"
        )
