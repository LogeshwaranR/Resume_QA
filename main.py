import streamlit as st
import PyPDF2
from openai import OpenAI
import json
import pandas as pd
from pandas import json_normalize
from io import BytesIO
import datetime
import os

def extract_text_from_file(file):
    file_extension = file.name.split(".")[-1]
    text = ""
    if file_extension == "pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
    elif file_extension == "xlsx":
        df = pd.read_excel(file)
        text = df.to_string(index=False)
    elif file_extension == "txt":
        text = file.read().decode("utf-8")
    return text

def dataframe_to_excel(df):
    excel_data = BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_data.seek(0)
    def dataframe_to_excel(df):
        excel_data = BytesIO()
        with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        excel_data.seek(0)
        return excel_data

def main():
    st.title("PDF Q and A")
    st.write("Upload multiple PDF, Excel, and TXT files and ask questions")

    uploaded_files = st.file_uploader(label="", label_visibility="collapsed" ,accept_multiple_files=True)

    check = []
    if uploaded_files:
        text_list = []
        for file in uploaded_files:
            text = extract_text_from_file(file)
            text_list.append(text + "\n" + "***End of File***")
            if len(text) > 0:
                check.append([file.name,True])
            else:
                check.append([file.name,False])
    for i in range(len(check)):
        if check[i][1]:
            st.write(f"<span style='color:green'>{check[i][0]} Extracted Successfully", "\n", unsafe_allow_html=True)
        else:
            st.write(f"<span style='color:red'>{check[i][0]} Failed to Extract</span>", "\n", unsafe_allow_html=True)

    questions = st.text_area("Your Questions")

    but_status = st.button("Process")
    if but_status and uploaded_files:
        API_KEY = os.getenv('API_KEY')
        with st.spinner('Processing...'):
            for text in text_list:
                client = OpenAI(api_key = API_KEY)
                today = datetime.date.today()
                prompt = "".join(text_list) + "I am a HR professional in a multinational company. Answer the following questions based on the above data." + questions
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a ChatGPT model that answers questions."},
                        {"role": "user", "content": prompt}
                    ]
                )
                answer = completion.choices[0].message.content
                st.write(f"Answer: {answer}")

if __name__ == "__main__":
    main()
