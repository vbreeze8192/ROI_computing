import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import math
import streamlit as st
import io

from utilities import licence, ams, setup, backoffice, occurency_maintenance, maint_savings, energy_savings, opt_savings, mipu_colors, download_excel, ROIcompute, check_password

##TODO: integra pwd https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

import streamlit as st


if check_password():

	st.title('ROI of an AI project')
	st.write('''
	AI trained on process and maintenance data can be a game changer for both the production and the O&M.
	According to Deloitte, AI can :green[decrease production cost by 20%] and :green[increase process efficiency by up to 15%] , \
		thanks to optimization, process automation and a better quality control.
	McKinsey states that AI driven predictive maintenance can :green[decrease machine downtimes by 50%] and :green[maintenance costs by up to 40%.]\
	The World Economic Forum says that AI applied to energy management can :green[decrease energy consumption by 10 to 20%] \
		an contribute to :green[lowering CO2 emissions.]''')
	st.write('''In MIPU experience, those savings must be leveraged on :orange[data availability, AS-IS situation and AI solution design].
		This app collects those informations and provides a :green[preliminary assessment of costs and savings.]
		All results represent orders of magnitude for investment and savings, and need to be confirmed by an expert in industrial AI.''')
	st.markdown('''To start with the evaluation, :orange[upload your file] or :orange[download the template] clicking on the button below.''') 
	st.write('''Scenario sheets must be named accordingly to the index in the general sheet. Add as many scenario as you need. 
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
	if st.checkbox(':paperclip: :red[Show template structure and descriptions:]'):
		for item in template_structure:
			st.write('Sheet: :orange[{}]'.format(item))
			st.write(template_structure[item])
	st.write(""" If you have the template ready, upload it here. """)
	uploaded_file = st.file_uploader("Upload excel", type=".xlsx")

	if st.button(':moneybag: Ready, compute ROI! :moneybag:',disabled=not uploaded_file, type='primary'):
		st.subheader('Results for each scenario')
		[scenarios,CF,synth,minn,tots]=ROIcompute(uploaded_file) 
		cii=0
		#st.line_chart(CF)

		
		fig,ax=plt.subplots()
		for scenario in scenarios:
			txt='{} | PBT: {}, ROI: {}'.format(scenario,\
								round(synth['PBT'].loc[scenario],1),\
								round(synth['ROI'].loc[scenario],1))
			ax.plot(CF[scenario], 'o-', linewidth=2,color=mipu_colors(cii),label=txt)
			ax.plot(synth['PBT'].loc[scenario],0, marker='*', markersize=20,color='gold')
			cii=cii+1
			#customization
			#plt.xticks([2017, 2018, 2019, 2020, 2021])
			#plt.text(int(PBT),cash_flow[int(round(PBT,1))+1], 'Payback time: {} years\nROI: {}'.format(round(PBT,1),round(ROI,1)))#, fontdict=None)

		ax.text(tots/2-0.5, minn,'Copyright MIPU', fontsize=10,color='gray',style='italic')

		ax.hlines(0, 0, tots)
		plt.xlabel('Years')
		plt.ylabel('Cash flow [k€]')
		plt.title('Scenarios of investment for AI projects')

		ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),
			fancybox=True, shadow=True, ncol=1)
		plt.xlim([0, tots])
		st.pyplot(fig)
		
		

		fn = 'ROI_results.png'
		plt.savefig(fn, bbox_inches='tight')
		with open(fn, "rb") as img:
			btn = st.download_button(
				label="Download image",
				data=img,
				file_name=fn,
				mime="image/png"
			)
		
    ##TODO: capire come / dove salva e perche i risultati vengono diversi

