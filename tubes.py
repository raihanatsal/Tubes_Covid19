import pandas as pd
import streamlit as st
from bokeh.models import ColumnDataSource, Select, DateRangeSlider, HoverTool, CustomJS
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.resources import CDN

st.set_page_config(page_title='Final Project')

st.header('Tugas Besar_Visualisasi Data')

# Baca CSV
df = pd.read_csv("covid_19_indonesia_time_series.csv")

Location_list = list(df['Location'].unique())

df['Date'] = pd.to_datetime(df['Date'])

cols1 = df.loc[:, ['Location', 'Date', 'Total Active Cases', 'Total Deaths', 'Total Recovered', 'Total Cases']]
cols2 = cols1[cols1['Location'] == 'Jawa Barat']

Overall = ColumnDataSource(data=cols1)
Curr = ColumnDataSource(data=cols2)

callback = CustomJS(
    args=dict(source=Overall, sc=Curr),
    code="""
        var f = cb_obj.value
        sc.data['Date']=[]
        sc.data['Total Cases']=[]
        sc.data['Total Deaths']=[]
        sc.data['Total Recovered']=[]
        sc.data['Total Active Cases']=[]
   
        for(var i = 0; i < source.get_length(); i++){
            if (source.data['Location'][i] == f){
                sc.data['Date'].push(source.data['Date'][i])
                sc.data['Total Cases'].push(source.data['Total Cases'][i])
                sc.data['Total Deaths'].push(source.data['Total Deaths'][i])
                sc.data['Total Recovered'].push(source.data['Total Recovered'][i])
                sc.data['Total Active Cases'].push(source.data['Total Active Cases'][i])     
            }
        }

        sc.change.emit();
    """
)
# Pie Chart
pie_data = df.groupby('Location').sum().reset_index()

total_cases = pie_data['Total Cases']
proportions = total_cases / total_cases.sum()
angles = 2 * np.pi * proportions

pie_chart = figure(title='Persentase Total Kasus COVID-19 Berdasarkan Lokasi', toolbar_location=None, width=500, height=400)
pie_chart.wedge(x=0, y=1, radius=0.4, start_angle=np.cumsum([0] + angle[:-1]), end_angle=np.cumsum(angle),
                line_color='white', fill_color='green', legend_field='Location', source=pie_data)

pie_chart.legend.location = "top_right"
pie_chart.axis.axis_label = None
pie_chart.axis.visible = False
pie_chart.grid.grid_line_color = None

# Menambahkan interaksi pada Pie Chart
pie_chart.add_tools(HoverTool(
    tooltips=[
        ('Lokasi', '@Location'),
        ('Total Kasus', '@{Total Cases}'),
    ],
    mode='mouse'
))

menu.js_on_change('value', callback)

date_range_slider = DateRangeSlider(value=(min(df['Date']), max(df['Date'])), start=min(df['Date']),
                                   end=max(df['Date']))

date_range_slider.js_link("value", bokeh_p.x_range, "start", attr_selector=0)
date_range_slider.js_link("value", bokeh_p.x_range, "end", attr_selector=1)

# Bar Plot
bar_data = df.groupby('Location').sum().reset_index()

bar_plot = figure(x_range=bar_data['Location'], y_axis_label='Total Cases',
                  title='Total Kasus COVID-19 Berdasarkan Lokasi', toolbar_location=None, width=600, height=400)
bar_plot.vbar(x='Location', top='Total Cases', source=ColumnDataSource(bar_data),
              width=0.9, color='green')

bar_plot.xaxis.major_label_orientation = 45

# Menambahkan interaksi pada Bar Plot
bar_plot.add_tools(HoverTool(
    tooltips=[
        ('Lokasi', '@Location'),
        ('Total Kasus', '@{Total Cases}'),
    ],
    mode='vline',
    line_policy='nearest',
))

bar_plot.js_on_event('tap', CustomJS(args=dict(source=bar_plot.select(ColumnDataSource)), code="""
    const selected_index = cb_obj.selected['1d'].indices[0];
    if (selected_index !== undefined) {
        const selected_location = source.data['Location'][selected_index];
        menu.value = selected_location;
        menu.dispatchEvent(new Event('change'));
    }
"""))

# Render plot Bokeh menggunakan Streamlit
st.bokeh_chart(column(menu, date_range_slider, bokeh_p, bar_plot, pie_chart))
