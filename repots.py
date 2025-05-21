import pandas as pd
import re
import os

# === Step 1: Load the data ===
file_name = 'attendance.csv'
df = pd.read_csv(file_name)

# === Step 2: Drop unnecessary columns (if they exist) ===
columns_to_delete = [
    'Topic', 'Type', 'ID', 'Host name', 'Host email',
    'Max concurrent views', 'Email', 'Guest', 'Recording disclaimer response',
    'In waiting room', 'Department', 'Group', 'Source', 'Unique viewers'
]
df = df.drop(columns=[col for col in columns_to_delete if col in df.columns], errors='ignore')

# === Step 3: Clean student name ===
def clean_student_name(name):
    name = str(name)
    name = re.sub(r'^\d+[-_\s]*', '', name)
    name = re.sub(r'[-_\s]+', ' ', name)
    name = re.sub(r'\d+', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = name.strip()
    name = name.title()
    return name

# Extract Student ID and Clean Name
df['Student ID'] = df['Name (original name)'].apply(lambda x: re.findall(r'^\d+', str(x))[0] if re.findall(r'^\d+', str(x)) else None)
df['Student Name'] = df['Name (original name)'].apply(lambda x: clean_student_name(x))

# === Step 4: Convert time columns to datetime ===
df['Start time'] = pd.to_datetime(df['Start time'])
df['Join Time'] = pd.to_datetime(df['Join time'])

# Extract lecture date
df['Lecture Date'] = df['Start time'].dt.date

# === Step 5: Daily Attendance Report ===
grouped_df_daily = df.groupby(['Student ID', 'Lecture Date']).agg(
    Daily_Total_Time=('Duration (minutes).1', 'sum'),
    Daily_Joins=('Student ID', 'size')
).reset_index()

# Merge with names
student_info = df.drop_duplicates(subset=['Student ID'])[['Student ID', 'Student Name']]
attendance_daily = pd.merge(grouped_df_daily, student_info, on='Student ID')

# Reorder columns
attendance_daily = attendance_daily[['Student ID', 'Student Name', 'Lecture Date', 'Daily_Total_Time', 'Daily_Joins']]

# === Step 6: Full Summary Attendance Report ===
summary_df = attendance_daily.groupby(['Student ID', 'Student Name']).agg(
    Total_Days_Attended=('Lecture Date', 'nunique'),
    Total_Time=('Daily_Total_Time', 'sum'),
    Total_Joins=('Daily_Joins', 'sum')
).reset_index()

# === Step 7: Create output folder ===
output_folder = 'attendance_reports'
os.makedirs(output_folder, exist_ok=True)

# === Step 8: Save reports ===
attendance_daily.to_csv(os.path.join(output_folder, 'daily_attendance_report.csv'), index=False)
summary_df.to_csv(os.path.join(output_folder, 'class_summary_report.csv'), index=False)

# === Step 9: Save individual reports ===
for student_id in summary_df['Student ID']:
    student_name = summary_df.loc[summary_df['Student ID'] == student_id, 'Student Name'].values[0]
    student_report = attendance_daily[attendance_daily['Student ID'] == student_id]
    student_report.to_csv(os.path.join(output_folder, f'{student_name}_{student_id}.csv'), index=False)

print("✅ Reports generated successfully in the 'attendance_reports' folder.")
