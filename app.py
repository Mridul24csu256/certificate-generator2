import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

st.title("🖼 Certificate Generator")

# Upload certificate template
template_file = st.file_uploader("Upload Certificate Template (PNG/JPG)", type=["png", "jpg", "jpeg"])
if template_file:
    template = Image.open(template_file).convert("RGB")
    st.image(template, caption="Certificate Template Preview", use_column_width=True)

    # Upload data file
    data_file = st.file_uploader("Upload Data File (CSV/Excel)", type=["csv", "xlsx"])
    if data_file:
        if data_file.name.endswith(".csv"):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)

        st.write("### Preview Data")
        st.dataframe(df.head())

        # Select which columns to use
        selected_columns = st.multiselect("Select Columns to Print", df.columns)

        # Font library (add more .ttf files in repo if you want)
        fonts = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Courier": "cour.ttf",
        }

        # Settings for each column
        column_settings = {}
        for col in selected_columns:
            st.subheader(f"⚙️ Settings for {col}")

            font_choice = st.selectbox(f"Choose font for {col}", list(fonts.keys()), key=f"font_{col}")
            font_size = st.slider(f"Font size for {col}", 10, 100, 40, key=f"size_{col}")
            font_color = st.color_picker(f"Font color for {col}", "#000000", key=f"color_{col}")

            x = st.number_input(f"X position (pixels) for {col}", min_value=0, max_value=template.width, value=100, key=f"x_{col}")
            y = st.number_input(f"Y position (pixels) for {col}", min_value=0, max_value=template.height, value=100, key=f"y_{col}")

            column_settings[col] = {"font": font_choice, "size": font_size, "color": font_color, "pos": (x, y)}

        # Generate certificates
        if st.button("🎉 Generate Certificates"):
            os.makedirs("certificates", exist_ok=True)
            for idx, row in df.iterrows():
                cert = template.copy()
                draw = ImageDraw.Draw(cert)

                for col in selected_columns:
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
