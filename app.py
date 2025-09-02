import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os
from streamlit_drawable_canvas import st_canvas

st.title("🎓 Certificate Generator with Click-to-Place & Font Library")

# 📂 Font library
font_folder = "fonts"
if not os.path.exists(font_folder):
    os.makedirs(font_folder)

available_fonts = [f for f in os.listdir(font_folder) if f.endswith(".ttf")]
if not available_fonts:
    st.error("⚠️ No fonts found in 'fonts/' folder. Please add .ttf files there.")
else:
    # Font options (global for all columns)
    selected_font = st.selectbox("Choose a font", available_fonts)
    font_path = os.path.join(font_folder, selected_font)

    font_size = st.number_input("Font Size", value=40, step=1)
    font_color = st.color_picker("Font Color", "#000000")  # default black

# 📑 Upload Excel and Template
excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
template_file = st.file_uploader("Upload Certificate Template (JPG/PNG)", type=["jpg", "jpeg", "png"])

if excel_file and template_file and available_fonts:
    df = pd.read_excel(excel_file)
    st.write("📑 Columns found in Excel:", list(df.columns))

    # Select columns
    selected_columns = st.multiselect("Select columns to include on certificate", df.columns)

    template = Image.open(template_file).convert("RGB")

    # Dictionary to store positions
    positions = {}

    for col in selected_columns:
        st.subheader(f"Set position for: {col}")
        st.write("👉 Click on the certificate where you want this field to appear:")

        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=0,
            stroke_color="rgba(0,0,0,0)",
            background_image=template,
            update_streamlit=True,
            height=template.height,
            width=template.width,
            drawing_mode="point",
            key=f"canvas_{col}"
        )

        if canvas_result.json_data and len(canvas_result.json_data["objects"]) > 0:
            last_obj = canvas_result.json_data["objects"][-1]
            x, y = last_obj["left"], last_obj["top"]
            positions[col] = (x, y)

    # Preview one certificate
    if st.button("Preview Sample Certificate"):
        if len(positions) < len(selected_columns):
            st.error("⚠️ Please set positions for all selected fields first.")
        else:
            row = df.iloc[0]
            cert = template.copy()
            draw = ImageDraw.Draw(cert)

            for col in selected_columns:
                text = str(row[col])
                x, y = positions[col]
                font = ImageFont.truetype(font_path, font_size)
                draw.text((x, y), text, font=font, fill=font_color)

            st.image(cert, caption="Sample Certificate Preview")

    # Generate all certificates
    if st.button("Generate All Certificates"):
        if len(positions) < len(selected_columns):
            st.error("⚠️ Please set positions for all selected fields first.")
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for _, row in df.iterrows():
                    cert = template.copy()
                    draw = ImageDraw.Draw(cert)

                    for col in selected_columns:
                        text = str(row[col])
                        x, y = positions[col]
                        font = ImageFont.truetype(font_path, font_size)
                        draw.text((x, y), text, font=font, fill=font_color)

                    file_name = f"{row[selected_columns[0]]}.jpg"
                    img_bytes = io.BytesIO()
                    cert.save(img_bytes, format="JPEG")
                    zf.writestr(file_name, img_bytes.getvalue())

            st.success("✅ Certificates generated successfully!")
            st.download_button(
                label="📥 Download All Certificates (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="certificates.zip",
                mime="application/zip"
            )
