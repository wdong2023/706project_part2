import altair as alt
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Show the page title and description.
st.set_page_config(page_title="Socioeconomic Factors & COVID19")
st.title("Socioeconomic Factors & COVID19")
st.write(
    """
    This app visualizes COVID data from Johns Hopkins University and Socioeconomic data 
    from World Bank Health Nutrition and Population Statistics. 
    It shows how the socioeconomic factors interact with COVID rates for each country. 
    Just click on the widgets below to explore!
    """
)


# Load the data from a CSV
@st.cache_data
def load_data():
    df = pd.read_csv("data/plot2.csv")
    return df


df = load_data()

# rename columns
df.columns = ['country', 'health_expenditure', 'death_rate','GDP','life_expectancy','literacy_rate','net_migration',
              'poverty_ratio','unemployment','population','density','confirmed','deaths','recovered','active']
# calculate rates
df['confirmed_rate'] = df['confirmed'] / df['population']
df['deaths_rate'] = df['deaths'] / df['population']
df['recovered_rate'] = df['recovered'] / df['population']
df['active_rate'] = df['active'] / df['population']

# Dropdown for selecting the X and Y factors
x_axis = st.selectbox('Select X-axis factor (Used for scatterplot)', 
                      options=['health_expenditure', 'death_rate', 'GDP', 'life_expectancy', 'literacy_rate', 'net_migration', 'poverty_ratio', 'unemployment'],
                      index=0) # default heath_expenditure
y_axis = st.selectbox('Select Y-axis factor', 
                      options=['health_expenditure', 'death_rate', 'GDP', 'life_expectancy', 'literacy_rate', 'net_migration', 'poverty_ratio', 'unemployment'],
                      index = 2) # default GDP

# Dropdown for selecting the rate category (confirmed, active, deaths, recovered)
rate_category = st.selectbox(
    'Rate category',
    options=['confirmed_rate', 'active_rate', 'deaths_rate', 'recovered_rate'],
    format_func=lambda x: x.replace('_', ' ').title(),
    index=0  # Set default to 'confirmed_rate'
)

# Dropdown for selecting countries
countries = st.multiselect('Country', 
                           options=df['country'].unique(), 
                           default=df['country'].unique())

# Filter data based on selected countries
filtered_df = df[df['country'].isin(countries)]

# Section 1: Bubble Chart
st.header("Bubble Chart: COVID-19 Rate by Socioeconomic Factors")

# Create the bubble chart
bubble_chart = alt.Chart(filtered_df).mark_circle().encode(
    x=alt.X(x_axis, title=x_axis.replace('_', ' ').title()),
    y=alt.Y(y_axis, title=y_axis.replace('_', ' ').title()),
    size=alt.Size(rate_category, title=rate_category.replace('_', ' ').title(), scale=alt.Scale(range=[100, 1000])),
    color=alt.Color('country', legend=None),
    tooltip=['country', rate_category]
).properties(
    width=700,
    height=500,
    title=f'Bubble Chart: {x_axis.replace("_", " ").title()} vs {y_axis.replace("_", " ").title()} (Size: {rate_category.replace("_", " ").title()})'
)

# Display the bubble chart
st.altair_chart(bubble_chart, use_container_width=True)


# Section 2: Scatterplot + Regression Line
st.header("Scatterplot + Regression Line")

# Calculate the correlation coefficient between the selected socioeconomic factor and the selected COVID rate
correlation_coef = filtered_df[x_axis].corr(filtered_df[rate_category])

# Create the scatterplot with a regression line
scatter_plot = alt.Chart(filtered_df).mark_circle(size=100).encode(
    x=alt.X(x_axis, title=x_axis.replace('_', ' ').title()),
    y=alt.Y(rate_category, title=rate_category.replace('_', ' ').title()),
    color=alt.Color('country', legend=None),
    tooltip=['country', x_axis, rate_category]
)

# Add the regression line with slope and intercept in the tooltip
regression_line = scatter_plot.transform_regression(
    x_axis, rate_category
).mark_line(color='red').encode(
    tooltip=[
        alt.Tooltip('slope:Q', title='Slope'),
        alt.Tooltip('intercept:Q', title='Intercept')
    ]
)

# Layer the scatterplot and regression line, and set the combined title
final_chart = alt.layer(
    scatter_plot + regression_line
).properties(
    width=700,
    height=500,
    title={
        'text': f'Scatterplot: {x_axis.replace("_", " ").title()} vs {rate_category.replace("_", " ").title()}',
        'subtitle': f'Correlation: {correlation_coef:.2f}'
    }
).configure_title(
    anchor='start',
    fontSize=16,
    fontWeight='bold',
    subtitleFontSize=16,  # Subtitle styling
    subtitleFontWeight='normal',
    lineHeight=25  # Adjust title-subtitle spacing
)

# Display the final combined chart (scatterplot + regression line + correlation text as title)
st.altair_chart(final_chart, use_container_width=True)

# Section 3: Heatmap of correlations
# Select columns for the correlation matrix
correlation_columns = ['health_expenditure', 'death_rate', 'GDP', 'life_expectancy', 'literacy_rate', 'net_migration', 
                       'poverty_ratio', 'unemployment', 'population', 'density', 
                       'confirmed_rate', 'deaths_rate', 'recovered_rate', 'active_rate']

# Calculate the correlation matrix
correlation_matrix = df[correlation_columns].corr()

# Plot the heatmap
plt.figure(figsize=(10,8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, linewidths=.5)
plt.title('Correlation Heatmap of Socioeconomic Factors and COVID-19 Rates', fontsize=16)

# Display the heatmap in Streamlit
st.pyplot(plt)

# Section 4: Bar chart

# Dropdown for case type (confirmed, active, deaths, recovered)
case_type = st.selectbox(
    'Case Type',
    options=['confirmed', 'active', 'deaths', 'recovered'],
    format_func=lambda x: x.capitalize()
)

# Slider for filtering countries based on the selected socioeconomic factor
min_value = float(df[x_axis].min())
max_value = float(df[x_axis].max())

factor_range = st.slider(
    f'Select Range for {x_axis.replace("_", " ").title()}',
    min_value=min_value,
    max_value=max_value,
    value=(min_value, max_value)  # Default range is the full range of the data
)

# Filter the dataset based on the selected socioeconomic factor range
filtered_range_df = df[(df[x_axis] >= factor_range[0]) & (df[x_axis] <= factor_range[1])]

# Create a bar chart showing the raw cases for the filtered countries
bar_chart = alt.Chart(filtered_range_df).mark_bar().encode(
    x=alt.X('country:N', title='Country', sort=alt.EncodingSortField(field=case_type, order='descending')),
    y=alt.Y(f'{case_type}:Q', title=f'Total {case_type.capitalize()} Cases'),
    color=alt.Color('country:N', legend=None),
    tooltip=['country', f'{case_type}']
).properties(
    width=700,
    height=500,
    title=f'Total {case_type.capitalize()} Cases by Country (Filtered by {x_axis.replace("_", " ").title()})'
).configure_axisX(
    labelFontSize=10  # Set the font size for the x-axis labels
)

# Display the bar chart
st.altair_chart(bar_chart, use_container_width=True)


