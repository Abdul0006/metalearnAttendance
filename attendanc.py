import pandas as pd
import re

# Load the CSV file (make sure 'attendance.csv' is in the same folder)
df = pd.read_csv('attendance.csv')

# Drop unwanted columns if they exist
columns_to_delete_safe = ['Topic', 'Type', 'ID', 'Host name', 'Host email',
                          'Max concurrent views', 'Email', 'Guest', 'Recording disclaimer response',
                          'In waiting room', 'Department', 'Group', 'Source', 'Unique viewers']
df = df.drop(columns=[col for col in columns_to_delete_safe if col in df.columns], errors='ignore')

# Function to clean student names
def clean_student_name(name):
    name = str(name)
    name = re.sub(r'^\d+[-_\s]*', '', name)
    name = re.sub(r'[-_\s]+', ' ', name)
    name = re.sub(r'\d+', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = name.strip()
    name = name.title()
    return name

# Extract Student ID and clean Student Name
df['Student ID'] = df['Name (original name)'].apply(lambda x: re.findall(r'^\d+', str(x))[0] if re.findall(r'^\d+', str(x)) else None)
df['Student ID'] = df['Student ID'].astype(str).str.lstrip('0')
df['Student Name'] = df['Name (original name)'].apply(clean_student_name)

# Convert time columns to datetime
df['Start time'] = pd.to_datetime(df['Start time'])
df['Join Time'] = pd.to_datetime(df['Join time'])

# Extract lecture date
df['Lecture Date'] = df['Start time'].dt.date

# Calculate daily total time and joins
grouped_df_daily = df.groupby(['Student ID', 'Lecture Date']).agg(
    Total_Time=('Duration (minutes).1', 'sum'),
    Daily_Joins=('Student ID', 'size')
).reset_index()

# Rename columns
grouped_df_daily = grouped_df_daily.rename(columns={
    'Total_Time': 'Daily Total Time',
    'Daily_Joins': 'Number of Joins (Daily)'
})

# Merge with student names
student_info = df.drop_duplicates(subset=['Student ID'])[['Student ID', 'Student Name']]
attendance_final_df_daily = pd.merge(grouped_df_daily, student_info, on='Student ID')

# Reorder and clean final daily attendance DataFrame
attendance_final_df_daily = attendance_final_df_daily[['Student ID', 'Student Name', 'Lecture Date', 'Daily Total Time', 'Number of Joins (Daily)']]
df = attendance_final_df_daily

# Summarize data for final report
total_lecture_days = df['Lecture Date'].nunique()

report = df.groupby(['Student ID', 'Student Name']).agg({
    'Daily Total Time': ['sum', 'mean', 'count']
}).reset_index()

report.columns = ['Student ID', 'Student Name', 'Total Time (All Days)', 'Average Daily Time', 'Days Present']

report['Attendance %'] = (report['Days Present'] / total_lecture_days) * 100
report['Attendance %'] = report['Attendance %'].round(2)
report['Total Time (All Days)'] = report['Total Time (All Days)'].round(2)
report['Average Daily Time'] = report['Average Daily Time'].round(2)
report = report.sort_values(by='Total Time (All Days)', ascending=False)

# Print or export final report
print(report.head())

# Optional: Save to CSV
report.to_csv('final_attendance_report.csv', index=False)
