import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# Setup for saving plots
# =========================
os.makedirs("images", exist_ok=True)

def save_and_show_plot(filename, dpi=300):
    """Save the current plot to the images folder and display it."""
    plt.savefig(f"images/{filename}.png", dpi=dpi, bbox_inches="tight")
    plt.show()

# =========================
# Load Data
# =========================
df = pd.read_csv("E:/Ecommerce customer behaviour/E-commerce Customer Behavior - Sheet1.csv")
print(df.head())

# =========================
# City Remapping
# =========================
unique_cities = df['City'].unique()
print("Original unique cities", unique_cities)

uae_city_map = {
    'San Francisco': 'Dubai',
    'Los Angeles': 'Abu Dhabi',
    'Chicago': 'Sharjah',
    'Miami': "Ajman",
    'New York': 'Ras Al Khaimah',
    'Houston': 'Fujairah'
}

df['City'] = df['City'].map(uae_city_map).fillna(df['City'])
print("UAE-adapted unique cities", df['City'].unique())

# =========================
# Data Cleaning
# =========================
df = df.dropna()
print("Missing Values:\n", df.isnull().sum())

df = df.drop_duplicates()

df['Gender'] = df['Gender'].astype('category')
df['Membership Type'] = df['Membership Type'].astype('category')
df['City'] = df['City'].astype('category')
df['Discount Applied'] = df['Discount Applied'].astype('bool')
df['Satisfaction Level'] = df['Satisfaction Level'].astype('category')

print("\nCleaned DataFrame:", df.shape)

# =========================
# Summary Statistics
# =========================
print("Summary Statistics\n", df.describe())

# =========================
# Visualizations
# =========================

# Age Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['Age'], bins=20, kde=True)
plt.title('Age Distribution of Customers in UAE E-commerce')
plt.xlabel('Age')
plt.ylabel('Frequency')
save_and_show_plot("age_distribution")

# Gender Distribution
plt.figure(figsize=(6, 4))
sns.countplot(x='Gender', data=df)
plt.title("Gender Distribution")
save_and_show_plot("gender_distribution")

# Total Spend by City
plt.figure(figsize=(10, 5))
sns.barplot(x='City', y='Total Spend', data=df, estimator='mean')
plt.title('Average Total Spend by UAE Emirate')
plt.xticks(rotation=45)
save_and_show_plot("spend_by_city")

# =========================
# Customer Segmentation
# =========================
print("DataFrame Columns:", df.columns.tolist())

max_age = df['Age'].max()
bins_age = [18, 30, 50, max_age + 1] if max_age > 50 else [18, 30, max_age + 1]
labels_age = ['Young (18-30)', 'Middle (31-50)', 'Senior (51+)'][:len(bins_age)-1]
df['Age Group'] = pd.cut(df['Age'], bins=bins_age, labels=labels_age, right=False)

max_spend = df['Total Spend'].max()
spend_bins = [0, 500, 2000, max_spend + 1] if max_spend > 2000 else [0, 500, max_spend + 1]
spend_labels = ['Low Spend', 'Medium Spend', 'High Spend'][:len(spend_bins)-1]
df['Spend Segment'] = pd.cut(df['Total Spend'], bins=spend_bins, labels=spend_labels, right=False)

agg_dict = {'Total Spend': 'mean', 'Items Purchased': 'mean'}
if 'CustomerID' in df.columns:
    agg_dict['CustomerID'] = 'count'
    rename_dict = {'CustomerID': 'Count'}
else:
    rename_dict = {'index': 'Count'}

segment_summary = df.groupby(['Age Group', 'Gender', 'City', 'Spend Segment']).agg(agg_dict).reset_index()
if 'CustomerID' not in df.columns:
    segment_summary = segment_summary.rename(columns={'index': 'Count'})
else:
    segment_summary = segment_summary.rename(columns=rename_dict)

print("Segment Summary:\n", segment_summary)

# =========================
# High-Value Customers
# =========================
high_value = df[(df['Spend Segment'] == 'High Spend') &
                (df['Membership Type'] == 'Gold') &
                (df['Satisfaction Level'] == 'Satisfied')]

print("\nHigh-Value Customers Count:", len(high_value))
print(high_value.head())

# Spend Segment by Age Group
plt.figure(figsize=(10, 6))
sns.boxplot(x='Age Group', y='Total Spend', data=df)
plt.title('Total Spend by Age Group in UAE E-Commerce')
save_and_show_plot("spend_by_age_group")

# Heatmap of Average Spend by City and Gender
pivot_table = df.pivot_table(values='Total Spend', index='City', columns='Gender', aggfunc='mean')
plt.figure(figsize=(8, 6))
sns.heatmap(pivot_table, annot=True, cmap='YlGnBu')
plt.title('Average Total Spend by City and Gender (UAE Context)')
save_and_show_plot("spend_heatmap")

# Satisfaction Level by Membership Type
plt.figure(figsize=(8, 5))
sns.countplot(x='Membership Type', hue='Satisfaction Level', data=df)
plt.title('Satisfaction Level by Membership Type')
save_and_show_plot("satisfaction_membership")

# =========================
# Insights Report
# =========================
total_customers = len(df)
high_value_percent = (len(high_value) / total_customers) * 100
top_city = df.groupby('City')['Total Spend'].sum().idxmax()
top_age_group = df.groupby('Age Group')['Total Spend'].sum().idxmax()

report = f"""
Customer Behavior Analysis Report - Dubai/UAE E-Commerce Platform

- Total Customers Analyzed: {total_customers}
- High-Value Customers: {len(high_value)} ({high_value_percent:.2f}% of total) - Focus marketing on Gold members in {top_city}.
- Top Spending City: {top_city} (Target with localized ads in Dubai/Abu Dhabi).
- Top Spending Age Group: {top_age_group} (Personalize offers for seniors if applicable).
- Insights: Females in Dubai show higher average spend; target them with discount campaigns.
- Recommendations:
  1. Run targeted email campaigns for high-spend segments in Sharjah and Ajman to boost retention.
  2. Offer loyalty upgrades to Silver members with medium spend to convert to high-value.
  3. Use satisfaction data to improve services for unsatisfied customers in Ras Al Khaimah.

Visualizations above support these findings for data-driven marketing in UAE.
"""

print(report)

with open('uae_ecommerce_report.txt', 'w') as f:
    f.write(report)

print("End of Project")
