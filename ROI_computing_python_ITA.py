import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.express as px
import datetime
import math
import streamlit as st
import io

from utilities import licence, ams, setup, backoffice, occurency_maintenance, maint_savings, energy_savings, opt_savings, mipu_colors, download_excel, ROIcompute, check_password



		


st.set_page_config(page_title="AI project ROI", page_icon="🤖")
if check_password():
	
	st.title('AI, ne vale la pena?')
	st.subheader('Calcolo del ritorno di investimento di un progetto di AI industriale.')
	st.write('''
	L'intelligenza artificiale addestrata sui dati di processo e manutenzione può essere un punto di svolta sia per la produzione che per l'O&M.
Secondo Deloitte, l'intelligenza artificiale può :green[ridurre i costi di produzione del 20%] e :green[aumentare l'efficienza del processo fino al 15%] , \
grazie all'ottimizzazione, all'automazione dei processi e ad un migliore controllo della qualità.
McKinsey afferma che la manutenzione predittiva guidata dall'intelligenza artificiale può :green[ridurre i tempi di fermo macchina del 50%] e :green[costi di manutenzione fino al 40%.]\
Il World Economic Forum afferma che l'IA applicata alla gestione dell'energia può :verde[ridurre il consumo di energia dal 10 al 20%] \
e contribuire alla :green[riduzione delle emissioni di CO2.]''')
	st.write('''Nell'esperienza MIPU, questi risparmi devono essere valutati in base a :orange[disponibilità dei dati, situazione AS-IS e progettazione della soluzione AI].
Questa app raccoglie queste informazioni e fornisce una :verde[valutazione preliminare di costi e risparmi.]
Tutti i risultati rappresentano ordini di grandezza per investimenti e risparmi e devono essere confermati da un esperto di intelligenza artificiale industriale.''')
	st.markdown('''Per iniziare con la valutazione, :orange[carica il tuo file] o :orange[scarica il modello] cliccando sul pulsante sottostante.''') 
	st.write('''Le schede degli scenari devono essere denominate in base all'indice della scheda generale. Aggiungi tutti gli scenari di cui hai bisogno.
	''')

	sc_col=['asset_name','C_Plan','O_Plan','C_1','O_1','C_2','O_2','C_3','O_3',\
		'C_Pred','O_Pred','E','G','VE','Eprod','Thprod','enmod','maintmod'\
		,'optmod','perc_data','av_failure']
	gen_col=['INDEX','scenario_description','ce','cg','cve','bck_ee','bck_man','bck_opt','tot_yr','sw','cost_FTE']
	general=pd.DataFrame(columns=gen_col)
	scenario=pd.DataFrame(columns=sc_col)
	buffer = io.BytesIO()
	with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
		# Write each dataframe to a different worksheet.
		general.to_excel(writer, sheet_name='GENERICO', index=False)
		scenario.to_excel(writer, sheet_name='scenario_name', index=False)
		# Close the Pandas Excel writer and output the Excel file to the buffer
		writer.save()
	st.download_button(
	label="Download Template",
	data=buffer,
	file_name='{}.xlsx'.format('Template'),
	mime='application/vnd.ms-excel')

	template_structure={}
	#template_structure={}
	template_structure['GENERICO']={'INDEX':'List of scenarios to be explored. Those names need to be equal to the Sheets names',\
				'scenario_description':'Description for each scenario',\
				'ce':'Electricity cost, must be aligned with energy consumption measurement unit (€/kWh, €/MWh...)',\
				'cg':'Gas cost, must be aligned with gas consumption measurement unit',\
				'cve':'Cost for other energy vectors consumed',\
				'bck_ee':'Backoffice hours related to energy management',\
				'bck_man':'Backoffice hours related to maintenance management',\
				'bck_opt':'Backoffice hours related to process analysis and optimization',\
				'tot_yr':'Years of the economic analysis, useful for ROI evaluation',\
				'sw':'Provision of proprietary software for AI creation and modelops',\
				'cost_FTE':'Average hourly cost for backoffice activities'}
	template_structure['scenario_name_from_INDEX']={'asset_name':'Name of the asset analysed',\
				'C_Plan':'Cost for each planned maintenance activity on the asset - average',\
				'O_Plan':'Planned maintenance occurrency in one year(1=once a year; 0.1= once every 10 years)',\
				'C_1':'Average cost for minor faults',\
				'O_1':'Yearly occurrency of minor faults',\
				'C_2':'Cost for main faults',\
				'O_2':'Yearly occurrency of main faults',\
				'C_3':'Cost for major faults',\
				'O_3':'Yearly occurrency of major faults',\
				'C_Pred':'Cost for predictive maintenance activity (vibration analysis, others)',\
				'O_Pred':'Predictive maintenance occurrency in one year',\
				'E':'Yearly electricity consumption of the asset',\
				'G':'Yearly gas consumption of the asset',\
				'VE':'Yearly consumption of other energy vectors',\
				'Eprod':'Electricity autoproduction',\
				'Thprod':'Other energy vector autoproduction',\
				'enmod':'Energy and efficiency model to be implemented (1=Yes, 0=No)',\
				'maintmod':'Predictive maintenance model to be implemented (1=Yes, 0=No)',\
				'optmod':'Process optimization (1=Yes,0=No)',\
				'perc_data':'Percentage of available data from the process (1=the process is fully represented, 0=all data are missing)',\
				'av_failure':'Enough fault data or machine log are avilable (1=Yes, 0=No)'}
	if st.checkbox(':paperclip: :red[Mostra le descrizioni per i campi del template:]'):
		for item in template_structure:
			st.write('Foglio: :orange[{}]'.format(item))
			st.write(template_structure[item])
	st.write(""" Se hai tutti gli scnari pronti, carica il template compilato qui. """)
	uploaded_file = st.file_uploader("Carica excel", type=".xlsx")

	if st.button(':moneybag: Ready, compute ROI! :moneybag:',disabled=not uploaded_file, type='primary'):
		st.subheader('Risultati per ogni scenario')
		[scenarios,CF,synth,minn,tots]=ROIcompute(uploaded_file) 
		cii=0
		fig=px.line(CF, x=CF.index, y=CF.columns, title='Cash Flow annuo [€]')
		st.plotly_chart(fig)


