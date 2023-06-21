import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.express as px
import os
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
	template_structure['GENERICO']={'INDEX':'Lista degli scenari da esplorare. Questi nomi devono essere uguali ai nomi di Fogli',\
	'scenario_description':'Descrizione per ogni scenario',\
	'ce':"Costo dell'energia elettrica, deve essere allineato con l'unità di misura del consumo energetico (€/kWh, €/MWh...)",\
	'cg':"Costo del gas, deve essere allineato con l'unità di misura del consumo di gas",\
	'cve':"Costo per altri vettori energetici consumati",\
	'bck_ee':"Orari di backoffice relativi alla gestione dell'energia",\
	'bck_man':"Orari di backoffice relativi alla gestione della manutenzione",\
	'bck_opt':"Orari di backoffice relativi all'analisi e all'ottimizzazione dei processi",\
	'tot_yr':"Anni dell'analisi economica, utili per la valutazione del ROI",\
	'sw':"Fornitura di software proprietario per la creazione di AI e modelops",\
	'cost_FTE':"Costo orario medio per attività di backoffice"}
	template_structure['scenario_name_from_INDEX']={'asset_name':"Nome dell'asset analizzato",\
	'C_Plan':"Costo per ogni attività di manutenzione pianificata sull'asset - medio",\
	'O_Plan':"Occorrenza della manutenzione pianificata in un anno(1=una volta all'anno; 0.1= una volta ogni 10 anni)",\
	'C_1':"Costo medio per guasti minori",\
	'O_1':"Presenza annuale di guasti minori",\
	'C_2':"Costo per guasti principali",\
	'O_2':"Presenza annuale dei guasti principali",\
	'C_3':"Costo per guasti gravi'",\
	'O_3':"Presenza annuale di guasti gravi",\
	'C_Pred':"Costo per attività di manutenzione predittiva (analisi delle vibrazioni, altro)",\
	'O_Pred':"Occorrenza della manutenzione predittiva in un anno",\
	'E':"Consumo elettrico annuo dell'asset",\
	'G':"Consumo annuo di gas dell'asset",\
	'VE':"Consumo annuo di altri vettori energetici",\
	'Eprod':"Autoproduzione di energia elettrica",\
	'Thprod':"Altra autoproduzione di vettori energetici",\
	'enmod':"Modello energetico ed efficiente da implementare (1=Sì, 0=No)",\
	'maintmod':"Modello di manutenzione predittiva da implementare (1=Sì, 0=No)",\
	'optmod':"Ottimizzazione del processo (1=Sì,0=No)",\
	'perc_data':"Percentuale di dati disponibili dal processo (1=il processo è completamente rappresentato, 0=mancano tutti i dati)",\
	'av_failure':"Sono disponibili sufficienti dati di errore o registro macchina (1=Sì, 0=No)"}
	if st.checkbox(':paperclip: :red[Mostra le descrizioni per i campi del template e scarica un excel di esempio:]'):
		for item in template_structure:
			st.write('Foglio: :orange[{}]'.format(item))
			st.write(template_structure[item])
		nome_modello= os.path.join(os.getcwd(), os.path.normpath('File_Import_Python.xlsx'))
		xl=pd.ExcelFile('path_to_file.xls')
		buffer = io.BytesIO()
		with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
			for sheet in xl.sheet_names:
				# Write each dataframe to a different worksheet.
				file_example=pd.read_excel(xl,sheet)
				file_example.to_excel(writer, sheet_name=sheet, index=False)
			# Close the Pandas Excel writer and output the Excel file to the buffer
			writer.save()
		st.download_button(
		label="Scarica il file compilato di esempio",
		data=buffer,
		file_name='{}.xlsx'.format('Example_file'),
		mime='application/vnd.ms-excel')

	st.write(""" Se hai tutti gli scenari pronti, carica il template compilato qui. """)
	uploaded_file = st.file_uploader("Carica excel", type=".xlsx")

	if st.button(':moneybag: Ready, compute ROI! :moneybag:',disabled=not uploaded_file, type='primary'):
		st.subheader('Risultati per ogni scenario')
		[scenarios,CF,synth,minn,tots]=ROIcompute(uploaded_file) 
		cii=0
		fig=px.line(CF, x=CF.index, y=CF.columns, title='Cash Flow annuo [€]')
		st.plotly_chart(fig)


