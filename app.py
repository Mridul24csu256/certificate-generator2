import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
from io import BytesIO

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

        # --- Font Library + Upload Option ---
        st.subheader("📂 Font Settings")
        uploaded_font = st.file_uploader("Upload Custom Font (.ttf)", type=["ttf"], key="font_upload")
        fonts = {
            "Arial": "arial.ttf",
            "Times New Roman": "times.ttf",
            "Courier": "cour.ttf",
        }
        if uploaded_font:
            font_path = os.path.join("uploaded_fonts", uploaded_font.name)
            os.makedirs("uploaded_fonts", exist_ok=True)
            with open(font_path, "wb") as f:
                f.write(uploaded_font.getbuffer())
            fonts[uploaded_font.name] = font_path

        # Settings for each column
        column_settings = {}
        for col in selected_columns:
            st.subheader(f"⚙️ Settings for {col}")

            font_choice = st.selectbox(f"Choose font for {col}", list(fonts.keys()), key=f"font_{col}")
            font_size = st.slider(f"Font size for {col}", 10, 100, 40, key=f"size_{col}")
            font_color = st.color_picker(f"Font color for {col}", "#000000", key=f"color_{col}")

            x = st.number_input(f"X position (pixels) for {col}", min_value=0, max_value=template.width, value=100, key=f"x_{col}")
            y = st.number_input(f"Y position (pixels) for {col}", min_value=0, max_value=template.height, value=100, key=f"y_{col}")

            alignment = st.selectbox(f"Text alignment for {col}", ["Left", "Center", "Right"], key=f"align_{col}")

            column_settings[col] = {
                "font": font_choice,
                "size": font_size,
                "color": font_color,
                "pos": (x, y),
                "align": alignment,
            }

        # Function to draw text with alignment
        def draw_text(draw, text, font, position, fill, align):
            x, y = position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            if align == "Center":
                x = x - text_width // 2
            elif align == "Right":
                x = x - text_width
            draw.text((x, y), text, font=font, fill=fill)

        # ================= Preview First Certificate =================
        if st.button("👀 Preview First Certificate"):
            sample_row = df.iloc[0]  # pick first row
            cert = template.copy()
            draw = ImageDraw.Draw(cert)

            for col in selected_columns:
                settings = column_settings[col]
                font_path = fonts.get(settings["font"])
                try:
                    font = ImageFont.truetype(font_path, settings["size"])
                except:
                    st.warning(f"⚠️ Font {settings['font']} not found, using default.")
                    font = ImageFont.load_default()

                text = str(sample_row[col])
                draw_text(draw, text, font, settings["pos"], settings["color"], settings["align"])

            st.image(cert, caption="Preview Certificate", use_column_width=True)

        # ================= Generate All Certificates =================
        if st.button("🎉 Generate All Certificates"):
            os.makedirs("certificates", exist_ok=True)

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for idx, row in df.iterrows():
                    cert = template.copy()
                    draw = ImageDraw.Draw(cert)

                    for col in selected_columns:
                        settings = column_settings[col]
                        font_path = fonts.get(settings["font"])
                        try:
                            font = ImageFont.truetype(font_path, settings["size"])
                        except:
                            font = ImageFont.load_default()

                        text = str(row[col])
                        draw_text(draw, text, font, settings["pos"], settings["color"], settings["align"])

                    cert_filename = f"{row[selected_columns[0]]}_certificate.png"
                    cert_path = os.path.join("certificates", cert_filename)
                    cert.save(cert_path)

                    # Add to ZIP
                    zipf.write(cert_path, cert_filename)

            zip_buffer.seek(0)
            st.success("✅ Certificates generated successfully!")
            st.download_button(
                label="⬇️ Download All Certificates (ZIP)",
                data=zip_buffer,
                file_name="certificates.zip",
                mime="application/zip",
            )
