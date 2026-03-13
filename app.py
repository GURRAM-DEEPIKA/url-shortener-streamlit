import streamlit as st
import sqlite3
import shortuuid
import validators
import qrcode
import os
import pandas as pd

BASE_URL = "https://url-shortener-app-jakqtyechmkpvv6wgyx5gz.streamlit.app/"

if not os.path.exists("qrcodes"):
    os.makedirs("qrcodes")


conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS urls(
id INTEGER PRIMARY KEY AUTOINCREMENT,
original_url TEXT,
short_code TEXT UNIQUE,
clicks INTEGER DEFAULT 0
)
""")

conn.commit()


st.set_page_config(page_title="Smart URL Shortener", page_icon="🔗")


st.title("🚀 Smart URL Shortener")


menu = st.sidebar.selectbox(
"Navigation",
["Create Short URL", "Analytics Dashboard"]
)


if menu == "Create Short URL":

    st.subheader("Enter Long URL")

    long_url = st.text_input("Paste your URL")

    if st.button("Generate Short URL"):

        if validators.url(long_url):

            short_code = shortuuid.ShortUUID().random(length=6)

            cursor.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?,?)",
            (long_url, short_code)
            )

            conn.commit()

            short_url = BASE_URL + short_code

            st.success("Short URL Generated")

            st.write(short_url)

            qr = qrcode.make(short_url)

            qr_path = f"qrcodes/{short_code}.png"

            qr.save(qr_path)

            st.image(qr_path, caption="QR Code")

        else:
            st.error("Invalid URL")


elif menu == "Analytics Dashboard":

    st.subheader("📊 URL Analytics")

    cursor.execute("SELECT original_url, short_code, clicks FROM urls")

    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=["Original URL","Short Code","Clicks"])

    st.dataframe(df)

    st.bar_chart(df["Clicks"])



query_params = st.query_params

if "code" in query_params:

    code = query_params["code"]

    cursor.execute(
    "SELECT original_url, clicks FROM urls WHERE short_code=?",
    (code,)
    )

    data = cursor.fetchone()

    if data:

        long_url, clicks = data

        cursor.execute(
        "UPDATE urls SET clicks=? WHERE short_code=?",
        (clicks+1, code)
        )

        conn.commit()

        st.markdown(f'<meta http-equiv="refresh" content="0; url={long_url}">',
        unsafe_allow_html=True)
