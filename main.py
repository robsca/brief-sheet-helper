import streamlit as st
st.set_page_config(page_title='Time sheet', page_icon=':clock1:', layout='wide', initial_sidebar_state='expanded')

# add image from the assets folder
st.image('assets/logo.png', width=200)

import pandas as pd
import datetime

def transform(df):
   features = ['Division', 'Employee', 'Start1', 'Stop1', 'Start2', 'Stop2']
   df = df[features]
   #with st.expander('Show dataframe'):
   #   st.write(df)
   features_time = ['Start1', 'Stop1', 'Start2', 'Stop2']
   # drop columns if start1, stop1, start2, stop2 are all 0
   df = df.drop(df[(df[features_time] == 0).all(axis=1)].index)

   # create a new column for name and surname
   df['Name'] = df['Employee'].str.split(' ', expand=True)[0]
   df['Surname'] = df['Employee'].str.split(' ', expand=True)[1]   
   # drop the old column
   df.drop('Employee', axis=1, inplace=True)
   # move the new columns to the front
   df = df[['Division', 'Name', 'Surname','Start1', 'Stop1', 'Start2', 'Stop2']]
   # add a empty column between stop1 and start2
   df.insert(5, ' ', ' ')

   for feature in features_time:
      # ad string to the column
      df[feature] = df[feature].astype(str)
      # add. : before the last 2 digits
      df[feature] = df[feature].str[:-2] + ':' + df[feature].str[-2:]
      # if ':0' the nan
      df[feature] = df[feature].replace(':0', None)
      # when not 0 transform to datetime
      df[feature] = pd.to_datetime(df[feature], format='%H:%M', errors='coerce')
      # keep only the time
      df[feature] = df[feature].dt.time


   # iterate over the rows
   for index, row in df.iterrows():
      # if start1 is >= to 15:00 then takes use the value for start2 and use the stop1 as stop2
      hour_start1 = int(row['Start1'].hour)
      if hour_start1 >= 14:
         df.at[index, 'Start2'] = row['Start1']
         df.at[index, 'Stop2']  = row['Stop1']
         df.at[index, 'Start1'] = None
         df.at[index, 'Stop1'] = None

   # None instead of Nat
   df = df.fillna(0)
   # instead of 0 is None
   df = df.replace(0, None)

   for index, row in df.iterrows():
      row_to_examine = row[features_time]
      row_to_examine = row_to_examine.tolist()
      # check the types
      is_start1_None_type = isinstance(row_to_examine[0], type(None))
      is_stop1_None_type = isinstance(row_to_examine[1], type(None))
      is_start2_None_type = isinstance(row_to_examine[2], type(None))
      is_stop2_None_type = isinstance(row_to_examine[3], type(None))

      if not is_start1_None_type and is_stop1_None_type:
         df.at[index, 'Stop1'] = datetime.time(00, 00)

      if not is_start2_None_type and is_stop2_None_type:
         df.at[index, 'Stop2'] = datetime.time(00, 00)

   # SHOW RESULTS
   divisions = df['Division'].unique()
   
   for d in divisions:
      with st.expander(f'{d}'):
         # create a new dataframe for each division
         df_div = df[df['Division'] == d]
         # sort the dataframe by start1
         df_div = df_div.sort_values(by=['Start1'])
         # drop the index
         df_div = df_div.reset_index(drop=True)
         st.write(df_div)

uploaded_file = st.sidebar.file_uploader("Import the Fourth Data")
if uploaded_file is not None:
   df = pd.read_csv(uploaded_file)
   transform(df)

else:
   st.info('Please upload the file containing the data.')