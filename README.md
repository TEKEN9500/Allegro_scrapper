# Allegro_scrapper

The objective of the project is to advise the real price of given GPU on current market and scrapp information about GPUs from online shop Allegro (biggest online shop in Poland)

It downloads data(price, memory, condition and other parameters) about all GPUs from first 100 pages on Allegro.pl and first 160 pages of allegro.archiwum - archive.
It involves simple GUI to input what GPU I want information about designed in QT Designer. Information about used and new models are separeted. 
Weighted mean takes popularity of certain price into consideration (and ignores the offers which no-one bought).


Allegro.py - downloads the GPU data from allegro.pl

Archiwum_scarp.py - downloads the GPU data from archive of allegro's offers

GUI.py - it runs the application with GUI, takes in model and puts out statistics

archiwum_1.csv, global_df_2.csv - saved to csv dataframes that were engineered in allegro.py and archiwum_scarp.py

Terminal_noGui.py    - version of app to run in terminal with no GUI (basically the function display_stats in GUI)
