import altair as alt
import pandas as pd
import streamlit as st

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
              'poverty_ratio','umemployment','population','density','confirmed','deaths','recovered','active']
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

# Add correlation coefficient text on top of the chart
correlation_text = alt.Chart(filtered_df).mark_text(
    align='center',
    fontSize=25,
    fontWeight='bold',
    color='black'
).encode(
    text=alt.value(f'Correlation: {correlation_coef:.2f}')
).properties(
    width=700,
    height=50
)

# Create the scatterplot with a regression line
scatter_plot = alt.Chart(filtered_df).mark_circle(size=100).encode(
    x=alt.X(x_axis, title=x_axis.replace('_', ' ').title()),
    y=alt.Y(rate_category, title=rate_category.replace('_', ' ').title()),
    color=alt.Color('country', legend=None),
    tooltip=['country', x_axis, rate_category]
)

# Add the regression line
regression_line = scatter_plot.transform_regression(
    x_axis, rate_category
).mark_line(color='red')

# Combine the scatterplot and the regression line
combined_chart = scatter_plot + regression_line

# Display the combined chart (scatterplot + regression line) and the correlation coefficient
st.altair_chart(combined_chart.properties(
    width=700,
    height=500,
    title=f'Scatterplot: {x_axis.replace("_", " ").title()} vs {rate_category.replace("_", " ").title()}'
), use_container_width=True)

# Display the correlation coefficient text
st.altair_chart(correlation_text, use_container_width=True)

# # Show a slider widget with the years using `st.slider`.
# years = st.slider("Years", 1986, 2006, (2000, 2016))

# # Filter the dataframe based on the widget input and reshape it.
# df_filtered = df[(df["genre"].isin(genres)) & (df["year"].between(years[0], years[1]))]
# df_reshaped = df_filtered.pivot_table(
#     index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
# )
# df_reshaped = df_reshaped.sort_values(by="year", ascending=False)


# # Display the data as a table using `st.dataframe`.
# st.dataframe(
#     df_reshaped,
#     use_container_width=True,
#     column_config={"year": st.column_config.TextColumn("Year")},
# )

# # Display the data as an Altair chart using `st.altair_chart`.
# df_chart = pd.melt(
#     df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
# )
# chart = (
#     alt.Chart(df_chart)
#     .mark_line()
#     .encode(
#         x=alt.X("year:N", title="Year"),
#         y=alt.Y("gross:Q", title="Gross earnings ($)"),
#         color="genre:N",
#     )
#     .properties(height=320)
# )
# st.altair_chart(chart, use_container_width=True)
