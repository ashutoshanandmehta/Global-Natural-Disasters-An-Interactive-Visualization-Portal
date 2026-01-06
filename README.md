# Natural-disasters-data-visualization-V2
#This is a temporary edit to this doc, just to describe how the vizualization files will be used

1. tab1_chloropleth.py -> no dropdowns as such as it describes the overall world data, across the overall time frame managed by the slider

2. tab1_treemap.py -> -the user enters country and a specific metric ( so two dropdown menus)
                      -the user can enter "World" that handles the overall data , and the code also handles that. So make sure the country drop down has "World" option.

3. tab5_ rolling_corr.py -> - dropdowns are : country( "World" included as said above),
                                               disaster type ("All" included , and the code handles data accordingly, 
                                               metric x, metric y, window size)

4. tab5_multi_metric.py -> -dropdowns: country(as said above), disaster type(as said above)

5. tab5_correlation_mat.py -> -dropdowns: country(as said above), start year, end year

6. tab5_scatter_mat.py -> -dropdowns: country(as said above), disaster type(as said above), metric x, metric y, start year , end year

7. tab5_correlation_net.py -> dropdowns: country("World" not needed here), start year, end year, correlation threshold, metric

