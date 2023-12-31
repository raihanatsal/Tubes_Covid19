import pandas as pd
import streamlit as st
from bokeh.models import ColumnDataSource, Select, DateRangeSlider, HoverTool, CustomJS, TapTool
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.resources import CDN

st.set_page_config(page_title='Final Project')
st.markdown("<h1 style='text-align: left; font-size: 36px;'>Tugas Besar Visualisasi Data</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left; font-size: 24px;'>Raihan Atsal Hafizh - 1301204485</h2>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left; font-size: 24px;'>Satria Aji Permana S. - 1301204209</h2>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left; font-size: 24px;'>IF-43-PIL-DS02</h2>", unsafe_allow_html=True)

# Membaca dataset CSV
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
# Line Plot
menu = Select(options=Location_list, value='Jawa Barat', title='Location')  
bokehline = figure(x_axis_label='Date', y_axis_label='Total Active Cases', y_axis_type="linear",
                 x_axis_type="datetime")  
bokehline.line(x='Date', y='Total Cases', color='yellow', legend_label="Case", source=Curr)
bokehline.line(x='Date', y='Total Deaths', color='red', legend_label="Death", source=Curr)
bokehline.line(x='Date', y='Total Recovered', color='purple', legend_label="Recover", source=Curr)
bokehline.line(x='Date', y='Total Active Cases', color='green', legend_label="Active Case", source=Curr)
bokehline.legend.location = "top_left"

bokehline.add_tools(HoverTool(
    tooltips=[
        ('Total Kasus', '@{Total Cases}'),
        ('Total Kematian', '@{Total Deaths}'),
        ('Total Sembuh', '@{Total Recovered}'),
        ('Total Kasus Aktif', '@{Total Active Cases}'),
    ],
    mode='mouse'
))
# Scatter Plot
scatter_p = figure(x_axis_label='Total Cases', y_axis_label='Total Deaths', y_axis_type="linear",
                   x_axis_type="linear", title='Hubungan Total Kasus dan Total Kematian',
                   width=600, height=400)
scatter_p.circle(x='Total Cases', y='Total Deaths', source=Curr, color='black')
scatter_p.add_tools(HoverTool(
    tooltips=[
        ('Total Kasus', '@{Total Cases}'),
        ('Total Kematian', '@{Total Deaths}'),
    ],
    mode='mouse'
))

# Menambahkan interaksi pada Scatter Plot
scatter_p.add_tools(TapTool(callback=CustomJS(code="""
    const selected_index = cb_data.source.selected.indices[0];
    if (selected_index !== undefined) {
        const selected_location = source.data['Location'][selected_index];
        menu.value = selected_location;
        menu.dispatchEvent(new Event('change'));
    }
""")))
# Range Slider
menu.js_on_change('value', callback)
range_slider = DateRangeSlider(value=(min(df['Date']), max(df['Date'])), start=min(df['Date']),
                                   end=max(df['Date']))
range_slider.js_link("value", bokehline.x_range, "start", attr_selector=0)
range_slider.js_link("value", bokehline.x_range, "end", attr_selector=1)

# Bar Plot
bar_data = df.groupby('Location').sum().reset_index()
bar_plot = figure(x_range=bar_data['Location'], y_axis_label='Total Cases',
                  title='Total Case COVID 19 Berdasarkan Lokasi', toolbar_location=None, width=600, height=400)
bar_plot.vbar(x='Location', top='Total Cases', source=ColumnDataSource(bar_data),
              width=0.9, color='purple')
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

# Deploy menggunakan Streamlit
st.bokeh_chart(column(menu, range_slider, bokehline, scatter_p, bar_plot))
