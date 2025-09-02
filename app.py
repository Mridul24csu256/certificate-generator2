import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import numpy as np
import os

st.title("🖼 Certificate Generator")

# Upload template
template_file = st.file_uploader("Upload Certificate Template (PNG/JPG)", type=["png", "jpg", "jpeg"])
if template_file:
    template = Image.open(template_file).convert("RGB")

    # Upload Excel/CSV with names & details
    data_file = st.file_uploader("Upload Data File (CSV/Excel)", type=["csv", "xlsx"])
    if data_file:
        if data_file.name.endswith(".csv"):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)

        st.write("### Preview Data")
        st.dataframe(df.head())

        # Select columns you want to use
        selected_columns = st.multiselect("Select Columns to Use in Certificate", df.columns)

        # Font library (local or Google fonts if you add them)
        fonts = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Courier": "cour.ttf",
        }

        # Settings for each column
        column_settings = {}
        for col in selected_columns:
            st.subheader(f"⚙️ Settings for {col}")

            # Font selection
            font_choice = st.selectbox(f"Choose font for {col}", list(fonts.keys()), key=f"font_{col}")
            font_size = st.slider(f"Font size for {col}", 10, 100, 40, key=f"size_{col}")
            font_color = st.color_picker(f"Font color for {col}", "#000000", key=f"color_{col}")

            # Canvas for placement
            st.write(f"📍 Place {col} on certificate")
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=0,
                stroke_color="",
                background_image=np.array(template).astype("uint8"),  # ✅ fresh copy for each column
                update_streamlit=True,
                height=template.height,
                width=template.width,
                drawing_mode="transform",
                key=f"canvas_{col}"
            )

            if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
                obj = canvas_result.json_data["objects"][-1]  # last placed
                x, y = obj["left"], obj["top"]
                column_settings[col] = {"font": font_choice, "size": font_size, "color": font_color, "pos": (x, y)}

        # Generate certificates
        if st.button("🎉 Generate Certificates"):
            os.makedirs("certificates", exist_ok=True)
            for idx, row in df.iterrows():
                cert = template.copy()
                draw = ImageDraw.Draw(cert)

                for col in selected_columns:
                    if col in column_settings:
                        settings = column_settings[col]
                        try:
                            font = ImageFont.truetype(fonts[settings["font"]], settings["size"])
                        except:
                            font = ImageFont.load_default()

                        text = str(row[col])
                        x, y = settings["pos"]
                        draw.text((x, y), text, font=font, fill=settings["color"])

                cert_path = f"certificates/{row[selected_columns[0]]}_certificate.png"
                cert.save(cert_path)

            st.success("✅ Certificates generated successfully!")
            st.write("Certificates saved in `certificates/` folder.")
