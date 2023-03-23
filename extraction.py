# Importing the required libraries
import easyocr
import cv2
import pandas as pd
import re
import sqlite3
import base64
import streamlit as st
from streamlit_option_menu import option_menu

# -------------------------------------------------------------------> CREATING A FILE TO STORE AN IMAGE
file_name = 'KIRUTHIGA SURESH'
# ------------------------------------------------------------------->ESTABLISHING CONNECTION WITH SQL DATABASE WITH SQLITE 3
conn = sqlite3.connect('mydatabase.db', check_same_thread=False)
cursor = conn.cursor()
my_table = 'CREATE TABLE IF NOT EXISTS Business_cards_data(ID INTEGER PRIMARY KEY AUTOINCREMENT,COMAPANY_NAME TEXT,EMPLOYEE_NAME TEXT,DISIGNATION Text,EMAIL_ID TEXT,CONTACT TEXT,ALTERNATE_CONTACT TEXT,WEBSITE TEXT,ADDRESS TEXT,IMAGE BLOB)'
cursor.execute(my_table)
# ---------------------------------------------------------------------> WRITING FUN TO GETDATA FROM THE CARD
def upload_database(image):
    img = cv2.imread(image)
    # ---------------------------------------------------------------->PROCESSING IMAGE
    # converting colour image to gray-color image
    original_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Arguments of function cv2.threshold
    # cv2.threshold(grayscale image, threshold value, maximum value of pixel, type of threshold)
    # Output is a tuple contain the threshold value and threshold image
    # Threshold to zero
    rect, thresh_image = cv2.threshold(original_img, 70, 255, cv2.THRESH_TOZERO)
    # ----------------------------------------------------------------> UPLOADED DATA FROM IMAGE USING OCR
    reader = easyocr.Reader(['en'], gpu=False)
    res = reader.readtext(thresh_image, detail=0, paragraph=True)
    result = reader.readtext(thresh_image, detail=0, paragraph=False)
    # ----------------------------------------------------------------> CONVERTING UPLOADED DATA INTO SINGLE STRING
    text = ''
    for i in result:
        text = text + ' ' + i

    # ----------------------------------------------------------------> EXTRACTING NAME
    name = result[0]
    text = text.replace(name, '')

    # ----------------------------------------------------------------> EXTRACTING DESIGNATION
    designation = result[1]
    text = text.replace(designation, '')

    # ----------------------------------------------------------------> EXTRACTING MAIL ID
    mail_id = re.findall(r'[A-Za-z0-9\.\-+_]+@[A-Za-z0-9\.\-+_]+\.[a-z]+', text)
    email = []
    for i in mail_id:
        email.append(i)
    email_id = email[0]
    text = text.replace(email_id, '')
    # ---------------------------------------------------------------->EXTRACTING CONTACT NUMBERS
    phone_Num = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    # print(number)
    arr = []
    for i in phone_Num:
        if len(i) >= 10:
            arr.append(i)
    contact = ''
    alter_contact = ''
    if len(arr) > 1:
        contact = arr[0]
        alter_contact = arr[1]
        text = text.replace(contact, '')
        text = text.replace(alter_contact, '')
    else:
        contact = arr[0]
        alter_contact = ' '
        text = text.replace(contact, '')
    # -----------------------------------------------------------------> EXTRACTING ADDRESS
    add_regex = re.compile(r'\d{2,4}.+\d{6}')
    address = ''
    for addr in add_regex.findall(text):
        address += addr
        text = text.replace(addr, '')
    # -----------------------------------------------------------------> EXTRACTING SITE LINK
    website_link_regex = re.compile(r'www.?[\w.]+', re.IGNORECASE)
    link = ''
    for lin in website_link_regex.findall(text):
        link += lin
        text = text.replace(link, '')
    # -----------------------------------------------------------------> EXTRACTING COMPANY DATA
    a = name + ' ' + designation
    b = designation + ' ' + name
    c = link + ' ' + email_id
    d = email_id + ' ' + link
    e = link
    f = email_id
    g = contact + ' ' + alter_contact
    h = alter_contact + ' ' + contact
    i = contact
    j = alter_contact
    arr = [a, b, c, d, e, f, g, h, i, j]
    for i in arr:
        if i in res:
            res.remove(i)
        else:
            continue
    company_name = res[-1]
    # -------------------------------------------------------------------> TO READ IMAGE
    with open(image, 'rb') as f:
        img = f.read()
    image = base64.b64encode(img)
    # --------------------------------------------------APPENDING RETRIEVED DATA INTO TABLE
    my_data = 'INSERT INTO Business_cards_data(COMAPANY_NAME,EMPLOYEE_NAME,DISIGNATION,EMAIL_ID,CONTACT,ALTERNATE_CONTACT,WEBSITE,ADDRESS,IMAGE)values(?,?,?,?,?,?,?,?,?)'
    cursor.execute(my_data, (company_name, name, designation, email_id, contact, alter_contact, link, address, image))
    conn.commit()


# -----------------------------------------------------------------------> CREATING FUN FOR EXTRACTING DATA
def extracted_data(image):
    img = cv2.imread(image)
    # -------------------------------------------------------------------> PROCESSING THE IMAGE
    # converting colour image to gray-color image
    original_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Arguments of function cv2.threshold
    # cv2.threshold(grayscale image, threshold value, maximum value of pixel, type of threshold)
    # Output is a tuple contain the threshold value and threshold image
    # Threshold to zero
    rect, thresh_image = cv2.threshold(original_img, 70, 255, cv2.THRESH_TOZERO)
    # ----------------------------------------------------------------> EXTRACTED DATA FROM IMAGE USING OCR
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(thresh_image, paragraph=False, decoder='wordbeamsearch')
    img = cv2.imread(image)

    for detection in result:
        top_left = tuple([int(val) for val in detection[0][0]])
        bottom_right = tuple([int(val) for val in detection[0][2]])
        text = detection[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.rectangle(img, top_left, bottom_right, (204, 0, 34), 5)
        img = cv2.putText(img, text, top_left, font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        # plt.figure(figsize=(10, 10))
        # plt.imshow(img)
        # plt.show()

    return img


# -------------------------------------------------------> SETTING PAGE CONFIGURATION WITH TITLE & ICON USING STREAMLIT
st.set_page_config(page_title='TEXT_EXTRACTION_USING_OCR', page_icon="chart_with_upwards_trend", layout='wide')

# -------------------------------------------------------> ADD TITLE TO THE CREATING APP
st.title(':black[TEXT_EXTRACTION_FROM_BUSINESS_CARDS_USING_OCR ]')

# -------------------------------------------------------> DEFINING THE MENU BAR
SELECT = option_menu(
    menu_title=None,
    options=['Home', 'Process', 'Search', 'Contact'],
    icons=['house', 'bar-chart', 'search', 'at'],
    default_index=2,
    orientation='horizontal',
    styles={
        'container': {'padding': '0!important', 'background-color': 'white', 'size': 'cover'},
        'icon': {'color': 'white', 'font-size': '20px'},
        'nav-link': {'font-size': '20px', 'text-align': 'center', 'margin': '-2px', '--hover-color': '#0b0214'},
        'nav-link-selected': {'background-color': '#0b0214'}
    }
)

# ---------------------------------------------------------> CREATING HOME SECTION
if SELECT == 'Home':
    st.subheader(
        'Getting started with EasyOCR for Optical Character Recognition---> EasyOCR is an open-source optical character recognition (OCR) engine that can be used to recognize text from images.OCR is the process of converting images of text into editable and searchable text.It supports more than 70 languages.One of the main advantages of EasyOCR is its ease of use. It requires minimal setup and can be run with just a few lines of code. It also supports multiple output formats.')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('![Alt Text](https://cdn.dribbble.com/users/2037413/screenshots/4144417/ar_businesscard.gif)')
# --------------------------------------------------------> CREATING PROCESS SECTION
if SELECT == "Process":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(':black[Choose image file to extract data]')
        # ------------------------------------------------> UPLOADING IMG TO THE APP
        uploaded = st.file_uploader('Choose a image file')
        # ------------------------------------------------> CONVERT BINARY VALUES OF THE image TO IMAGE
        if uploaded is not None:
            with open(f'{file_name}.png', 'wb') as f:
                f.write(uploaded.getvalue())
        # ------------------------------------------------> UPLOADING THE DATA TO DB
        st.subheader(':black[Upload extracted to Database]')
        if st.button('Upload data'):
            upload_database(f'{file_name}.png')
            st.success('Data uploaded to Database successfully!', icon="✅")
    # ----------------------------------------------------> EXTRACTING DATA FROM IMAGE
    with col2:
        st.subheader(':black[Image view of Data]')
        if st.button('Extract Data from Image'):
            extracted = extracted_data(f'{file_name}.png')
            st.image(extracted)

# --------------------------------------------------------> CHECKING THE DATABASE FOR CONFIRMATION
cursor.execute('select*from Business_cards_data')
df = pd.DataFrame(cursor.fetchall(),
                  columns=['ID', 'COMAPANY_NAME', 'EMPLOYEE_NAME', 'DISIGNATION', 'EMAIL_ID', 'CONTACT',
                           'ALTERNATE_CONTACT', 'WEBSITE', 'ADDRESS', 'IMAGE'])

if SELECT == 'Search':
    # ----------------------------------------------------> TO SEE ALL IN DB
    st.title(':black[To SEE All The Data in Database]')
    if st.button('Show All'):
        st.write(df)

    # ----------------------------------------------------> SEE THE RECORD WITH PARTICULAR VALUE
    st.header(':black[Search Data by Column]')
    column = str(st.radio('Select column to search', (
        'COMAPANY_NAME', 'EMPLOYEE_NAME', 'DISIGNATION', 'EMAIL_ID', 'CONTACT', 'ALTERNATE_CONTACT', 'WEBSITE','ADDRESS'),horizontal=True))
    value = str(st.selectbox('Please select value to search', df[column]))
    if st.button('Search Data'):
        st.dataframe(df[df[column] == value])

#CONTACT
if SELECT == 'Contact':
    name = " KIRUTHIGA SURESH"
    mail = (f'{"Mail :"}  {"deepasuresh7078@gmail.com"}')
    social_media = {"GITHUB": "https://github.com/keerthy-analyst ",
                    "LINKEDIN": "https://www.linkedin.com/in/kiruthiga-suresh-5a2a49249/"
                    }
    st.title(name)
    st.subheader("An Aspiring DATA-ANALYST..!")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(mail)
    # st.write("#")
    with col2:
        cols = st.columns(len(social_media))
        for index, (platform, link) in enumerate(social_media.items()):
            cols[index].write(f"[{platform}]({link})")
