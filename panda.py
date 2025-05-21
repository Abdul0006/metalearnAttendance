import pandas as pd

# Create a simple DataFrame
data = {
    "Name": ["Ali", "Sami", "Kamal"],
    "Age": [25, 30, 35],
    "Salary": [50000, 60000, 70000]
}
print("Dictionary Data:", data)


df = pd.DataFrame(data)
print("Data Frame Data:", df)

# Display data
# print(df.head(1))

# Analyze data
# print("Average Salary:", df["Salary"].mean())
# print("Maximum Salary:", df["Salary"].max())
# print("Minimum Salary:", df["Salary"].min())
# print("Total Salaries:", df["Salary"].sum())
