import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

model_detect= pickle.load(open('model_detect.pkl','rb'))
model_presence= pickle.load(open('model_presence.pkl','rb'))
#st.title(model_detect.predict(['hi shriyansh']))
#st.title(model_detect.predict(['text']))

st.title('Dark Pattern Identification')

def on_submit(user_input):
    st.write("Fetching details")
    try:
        response = requests.get(user_input)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all a tags and extract href attributes
        a_tags = soup.find_all('a')
        href_attributes = [{'href': a.get('href')} for a in a_tags]

        # Create a DataFrame for href attributes
        href_df = pd.DataFrame(href_attributes)
        href_df['Index'] = range(1, len(href_df) + 1)  # Add an 'Index' column

        # Find all img tags and extract src and alt attributes
        img_tags = soup.find_all('img')
        img_attributes = [{'src': img.get('src'), 'alt': img.get('alt')} for img in img_tags]

        # Create a DataFrame for image attributes
        img_df = pd.DataFrame(img_attributes)
        img_df['Index'] = range(1, len(img_df) + 1)  # Add an 'Index' column

        # Find all text content within the HTML document and split into lines
        text_content = soup.get_text("\n", strip=True)
        text_lines = text_content.split("\n")
        # text_df = pd.DataFrame({'Text Content': text_lines})
        # text_df['Index'] = range(1, len(text_df) + 1)  # Add an 'Index' column
        text_df = pd.DataFrame({'Index': range(1, len(text_lines) + 1), 'Text Content': text_lines})


        presence_predictions = model_presence.predict(text_lines)
        final_predictions = []

        for presence_prediction, text_line in zip(presence_predictions, text_lines):
            if presence_prediction == 'Dark':
                # Run model_detect if 'Dark' is predicted
                detect_prediction = model_detect.predict([text_line])[0]
                final_predictions.append(detect_prediction)
            else:
                # If 'Not Dark' is predicted, append 'Not Dark' to the final predictions
                final_predictions.append('Not Dark')
        text_df['Final Predictions'] = final_predictions


        # Create a DataFrame for text content with each line as a separate row
        # predictions = model_detect.predict(text_lines)
        # text_df['Model Predictions'] = predictions


        # Save the DataFrames to CSV files
        href_df.to_csv('href_attributes.csv', index=False)
        img_df.to_csv('image_attributes.csv', index=False)
        text_df.to_csv('text_content.csv', index=False)

        # Display the extracted data in the Streamlit app
        # st.header("Href Attributes DataFrame:")
        # st.write(href_df,index=False)
        # st.header("Image Attributes DataFrame:")
        # st.write(img_df,index=False)

        st.header("Text Content DataFrame:")
       # st.write(text_df)
        #highlighted_rows = text_df.style.applymap(lambda row: ['background: yellow' if row['Final Predictions'] != 'Not Dark' else '' for _ in row], axis=1)
        # st.dataframe(highlighted_rows) #.style.highlight_max(axis=0, subset='Final Predictions'))
        #highlighted_rows = text_df.style.apply(lambda row: ['border: 2px solid red' if row['Final Predictions'] != 'Not Dark' else '' for _ in row], axis=1).render()
        # st.write(highlighted_rows, unsafe_allow_html=True)
        highlighted_rows = text_df.style.applymap(lambda x: 'background-color: red ; color: white' if x !='Not Dark' else '', subset=['Final Predictions'])

        st.dataframe(highlighted_rows)



        #st.write(text_df)
        #st.pyplot()


        df = pd.read_csv('text_content.csv')

        # Assuming 'Category' is the column with classified categories
        category_counts = df['Final Predictions'].value_counts()
        not_cnt=0
        for prediction in df['Final Predictions']:
            if prediction =='Not Dark':
                not_cnt+=1
        yes_cnt= len(text_df)-not_cnt
        counts=[yes_cnt,not_cnt]
        labels=['Yes',"No"]
        # Create a pie chart using matplotlib

        st.header('Percent of Dark Patterns in the website')
        plt.figure(figsize=(10, 6))
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#70D0C6', '#FEA889'])
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        plt.title('Dark patterns in %')
        st.pyplot(plt.gcf())


        # Streamlit app

        # Display the dataset
       # st.dataframe(df)

        st.header('Distribution of Dark Patterns in Text Content')
        # Create a bar chart using seaborn
        plt.figure(figsize=(10, 6))
        sns.countplot(x='Final Predictions', data=df[df['Final Predictions'] != 'Not Dark'],  palette='viridis')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.title('Dark Pattern Types')
        st.pyplot(plt.gcf())

        # Show the streamlit app
        #st.show()

    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"An error occurred: {err}")

user_input = st.text_input("Enter the URL of the website")
if st.button("Submit"):
    on_submit(user_input)  # Call the function when the button is clicked


