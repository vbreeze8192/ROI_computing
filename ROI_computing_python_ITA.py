import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import warnings
#warnings.filterwarnings("ignore")
import math
import streamlit as st
import io

def licence (en_mod, main_mod,tot_opt, sw):
    if sw==1:
        if tot_opt>0:
            fixed_optima=20000 #Prezzo fisso optima ipotetico
        else: fixed_optima=0
        lic_cost=18700 + 11134*math.log(en_mod+main_mod+tot_opt)-20167+fixed_optima #calcolato sulle licenze 2023 per Rebecca.

    else: lic_cost=0
    lic_cost = np.ceil(lic_cost)
    return(lic_cost)


def ams (en_mod, main_mod,tot_opt, sw):
    if sw == 0:
        retem = 800 #circa un giorno per retraining
        retmm = 1600 # circa 2 giorni per retraing
        retopt=8000 # circa 15 giorni per reimpostare tutto l'ottimizzatore
        fixed_cost=7000 #costo gestione: circa 10 giornate all'anno + hosting per il cloud cca 2000 €/anno
    else:
        retem = 200 #retraining in 2 ore
        retmm = 400 #retraining in 4 ore
        retopt=1600 #impostazione scenario in 2 giorni
        fixed_cost=1600 #costo di gestione: circa 2 giorni l'anno

    ams = fixed_cost + retem * en_mod + retmm * main_mod + \
        retopt*(tot_opt +2)
    ams = np.ceil(ams)
    return(ams)

def setup (en_mod, main_mod,tot_opt, sw):
    if sw == 0:
        cem = 7000 #circa 15 giornate
        cmm = 10000 #circa 20 giornate
        if tot_opt>0:
            copt_fix=50000 #circa 30 giornate per definizione vincoli, scenari, funzione di costo etc
        else: copt_fix=0
        copt=7000 #circa 15 giornate per i modelli di forecast
        ind = 25000 
        alarms = 4500
        valid = 5000
    else:
        cem = 2000 #circa 4 giornate
        cmm = 6000 #circa 12 giornate
        
        copt=3000 #circa 6 giornate per i modelli di forecast
        ind = 10000
        alarms = 2500
        valid = 2000
        if tot_opt>0:
            copt_fix=20000 #circa 40 giornate per definizione vincoli, scenari, funzione di costo etc
        else: copt_fix=0

    SETUP_COST = en_mod * cem + main_mod * cmm + copt*(tot_opt+2)+ ind + alarms + valid
    return(SETUP_COST)

def backoffice(max_save, models, n_asset):
    
    SAVINGS_BACKOFFICE = max_save * models / n_asset
    return(SAVINGS_BACKOFFICE)



def occurency_maintenance(what, av_failures, perc_data, mm, em):
    #computes perc savings on occurrency
    if mm == 1:
        if what == "Plan":
            max_save = 0.1
        elif what == 1:
            max_save = 0.1
        elif what == 2:
            max_save = 0.6
        elif what == 3:
            max_save = 0.9
        elif what == "Pred":
            max_save = 1
        else:
            max_save = -1
    elif mm == 0:
        if em == 1:
            if what == "Plan":
                max_save = 0
            elif what == 1:
                max_save = 0
            elif what == 2:
                max_save = 0.2
            elif what == 3:
                max_save = 0.3
            elif what == "Pred":
                max_save = 1
            else:
                max_save = -1

    else:
        max_save = 0


    if max_save > -1:
        OCC_MAN = max_save / 2 * perc_data + max_save / 2 * av_failures * perc_data
    else:
        raise Exception("First voice must be Plan for planned maintenance, 0, 1 and 2 for low, medium and high level of failure, Pred for predictive maintenance.")
    return(OCC_MAN)

def maint_savings(what, av_failures, perc_data, mm):
    #computes cost savings for maintenance
    if mm == 1:
        if what == "Plan":
            max_save = 0
        elif what == 1:
            max_save = 0
        elif what == 2:
            max_save = 0.2
        elif what == 3:
            max_save = 0.4
        elif what == "Pred":
            max_save = 0
        else:
            max_save = -1

    else:
        max_save = 0

    SAVINGS_MAN = max_save * av_failures * perc_data
    return(SAVINGS_MAN)


def energy_savings(perc_data, mm, en):
    #computes energy savings, up to 7 perc 
    if en == 1 and mm == 1:
        SAVINGS_EN = 0.07 * perc_data
    elif en == 1 and mm == 0:
            SAVINGS_EN = 0.035 * perc_data
    elif mm == 1 and en == 0:
        SAVINGS_EN = 0.01 * perc_data
    else:
        SAVINGS_EN = 0
    return(np.abs(SAVINGS_EN))

def opt_savings(perc_data, opt):
    #computes ptimization savings, up to 15perc
    if opt == 1:
        SAVINGS_OPT = 0.15 * perc_data
    else:
        SAVINGS_OPT = 0
    return(np.abs(SAVINGS_OPT))

def mipu_colors(N):
    all_colors=['#16679C','#00B398','#C9609F','#FF7F50','#219AE9','#BDD48D','#EE6F90','#FFBD69']
    color=all_colors[N]
    return(color)

def download_excel(dftoexc,name_exc='Download_Excel'):
    # buffer to use for excel writer
    buffer = io.BytesIO()
    st.write(dftoexc)
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        dftoexc.to_excel(writer, sheet_name='Sheet1', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()
    st.download_button(
    label="Download data as Excel",
    data=buffer,
    file_name='{}.xlsx'.format(name_exc),
    mime='application/vnd.ms-excel')


def ROIcompute(name_file):

    minn=0
    tots=0 

    gen=df=pd.read_excel(name_file,sheet_name='GENERICO', index_col='INDEX')
    scenarios=gen.index
    #scenario=scenarios[0]
    synth=pd.DataFrame(data=np.nan,index=scenarios, columns=['Setup_cost','Licence','ams','Yearly_savings','PBT','ROI'])
    CF=pd.DataFrame(columns=scenarios)

    for scenario in scenarios:
        models=0
        en_mod=0
        main_mod=0
        tot_opt=0
        descr=gen['scenario_description'].loc[scenario]
        st.write('Computing scenario :orange[{}]'.format(scenario))
        st.write('Scenario features:')
        st.write(gen.loc[scenario])
        
        ce=gen['ce'].loc[scenario]
        cg=gen['cg'].loc[scenario]
        cve=gen['cve'].loc[scenario]
        bck_ee=gen['bck_ee'].loc[scenario]
        bck_man=gen['bck_man'].loc[scenario]
        bck_opt=gen['bck_opt'].loc[scenario]
        cost_bck=gen['cost_FTE'].loc[scenario]
        tot_yr=gen['tot_yr'].loc[scenario]
        sw=gen['sw'].loc[scenario]


        df=pd.read_excel(name_file,sheet_name=scenario, index_col='asset_name')

        assets=df.index    
        #for each row:
        for asset in assets:
            #each asset can have at most 1 energy model, 1 maint model and be optimized. 
            temp=df.loc[asset]
            em=int(temp['enmod']) #must be int
            mm=int(temp['maintmod']) #must be int
            opt=int(temp['optmod']) #must be int
            
            #compute number of models for licence,setup costs and bckf saving
            models=models+em+mm+opt
            en_mod=en_mod+em
            main_mod=main_mod+mm
            tot_opt=tot_opt+opt


        df['CYR_EE']=df['E']*ce 
        #df['Eprod'] #per ora autoprod elettrica non si conta...
        #df['Thprod'] #autoprod termica non utilizzata...
        df['CYR_G']=df['G']*cg
        df['CYR_VE']=df['VE']*cve 

        for what in ['Plan',1,2,3,'Pred']:
            df['CYR_{}'.format(what)]=df['C_{}'.format(what)].copy()*0
            df['Sperc_OCC_MAN_{}'.format(what)]=df['C_{}'.format(what)].copy()*0
            df['Sperc_MAN_{}'.format(what)]=df['C_{}'.format(what)].copy()*0
        df['Sperc_EN']=df['perc_data'].copy()*0
        df['Sperc_OPT']=df['perc_data'].copy()*0


        for asset in assets:
            for what in ['Plan',1,2,3,'Pred']:
                df['CYR_{}'.format(what)].loc[asset]=df['C_{}'.format(what)].loc[asset]*df['O_{}'.format(what)].loc[asset]
                df['Sperc_OCC_MAN_{}'.format(what)].loc[asset]=\
                    occurency_maintenance(what, df['av_failure'].loc[asset], df['perc_data'].loc[asset], df['maintmod'].loc[asset], df['enmod'].loc[asset])
                df['Sperc_MAN_{}'.format(what)].loc[asset]=\
                    maint_savings(what, df['av_failure'].loc[asset], df['perc_data'].loc[asset], df['maintmod'].loc[asset])
            df['Sperc_EN'].loc[asset]=\
                energy_savings(df['perc_data'].loc[asset],df['maintmod'].loc[asset], df['enmod'].loc[asset])
            df['Sperc_OPT'].loc[asset]=\
                opt_savings(df['perc_data'].loc[asset], df['optmod'].loc[asset])

         
        back_save=bck_ee* backoffice(0.6, en_mod, len(df.index))+\
                bck_man* backoffice(0.3, main_mod, len(df.index))+\
                bck_opt* backoffice(0.4, tot_opt, len(df.index))

    


        TOTYR_savings=0
        #compute savings after models
        #energy savings: how many euros imma save for optimization and monitoring
        for item in ['CYR_EE','CYR_G','CYR_VE']:
            df['{}_YRsave'.format(item)]=df['{}'.format(item)]*(df['Sperc_EN']+df['Sperc_OPT'])
            TOTYR_savings=TOTYR_savings+df['{}_YRsave'.format(item)].sum()

        #maint savings: how many euros imma save 
        for what in ['Plan',1,2,3,'Pred']:
            df['{}_YRsave'.format(what)]=df['CYR_{}'.format(what)]-(df['C_{}'.format(what)]*(1-df['Sperc_MAN_{}'.format(what)])*\
                df['O_{}'.format(what)]*(1-df['Sperc_OCC_MAN_{}'.format(what)]))
            TOTYR_savings=TOTYR_savings+df['{}_YRsave'.format(what)].sum()
        TOTYR_savings=TOTYR_savings+back_save

        #df.to_excel('{}.xlsx'.format(scenario)) ##capire come fare questo
        st.write('Main results for each asset:')
        download_excel(df,scenario)

        lic=licence (en_mod, main_mod,tot_opt, sw) + ams (en_mod, main_mod,tot_opt, sw) #licence and maintenance
        stp=setup (en_mod, main_mod,tot_opt, sw)/1000
        cf_t=(TOTYR_savings-lic)/1000 #saving per year without scaling

        st.write('Total saving expected per year is :green[{} k€/yr]'.format(round(TOTYR_savings/1000,1)))


        cash_flow=[-stp]
        if cash_flow[0]<minn:
            minn=cash_flow[0]
        if tot_yr>tots:
            tots=tot_yr
        tact=0.05
        ratio=stp/cf_t

        for ii in range(1,11): #standard valutato su 11 anni per non incasinare il dataframe sotto
            cash_flow=cash_flow+[cash_flow[ii-1] + cf_t/((1+tact)**ii)]
        ROI=tot_yr*(1/ratio)*(1+tact)**tot_yr
        PBT=ratio*(1+tact)**(ratio-1)
 
        txt='{} | PBT: {}, ROI: {}'.format(descr,round(PBT,1),round(ROI,1))

        st.write('Setup cost  is :orange[{} k€]'.format(round(stp,1)))
        st.write('Licence cost is :orange[{} k€/yr]'.format(round(licence (en_mod, main_mod,tot_opt, sw)/1000,1)))
        st.write('Maintenance cost is :orange[{} k€/yr]'.format(round(ams(en_mod, main_mod,tot_opt, sw)/1000,1)))
        st.write('Net cashflow for each year is :green[{} k€/yr]'.format(round(cf_t,1)))
        st.write('Main economics for scenario :green[{}, {}]'.format(scenario,txt) )
        st.write('Finished scenario {} - {}\n_____\n\n'.format(scenario,descr))

        synth.loc[scenario]=[round(stp,1),round(licence (en_mod, main_mod,tot_opt, sw)/1000,1),\
            round(ams(en_mod, main_mod,tot_opt, sw)/1000,1),round(cf_t,1),\
                round(PBT,1),round(ROI,1)]
        CF[scenario]=cash_flow
    
    st.subheader('Global results')
    st.write('Cash flow')
    download_excel(CF,'Cash_flow')

    st.write('Main economics')
    download_excel(synth,'Main_economics')
    return(scenarios,CF,synth,minn,tots)

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
                    'cost_FTE':'Average hourly cost for backoffice activities'\
                        }
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

    from bokeh.plotting import figure
    p = figure(title='Scenarios of investment for AI projects', x_axis_label='Years', y_axis_label='Cash flow [k€]')
    for scenario in scenarios:
        txt='{} | PBT: {}, ROI: {}'.format(scenario,\
                                           round(synth['PBT'].loc[scenario],1),\
                                            round(synth['ROI'].loc[scenario],1))
        p.line(CF[scenario], legend_label=txt, line_width=2,color=mipu_colors(cii))
        p.circle(synth['PBT'].loc[scenario],color='gold')
        cii=cii+1
        #customization
        #plt.xticks([2017, 2018, 2019, 2020, 2021])
        #plt.text(int(PBT),cash_flow[int(round(PBT,1))+1], 'Payback time: {} years\nROI: {}'.format(round(PBT,1),round(ROI,1)))#, fontdict=None)

    st.bokeh_chart(p)
    '''
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
    '''
    ##TODO: capire come / dove salva e perche i risultati vengono diversi

