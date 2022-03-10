#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# In[2]:


color_vaccine_map = {'COM':'rgb(255,0,0)', 'UNK':'rgb(0,255,0)', 'JANSS':'rgb(0,0,255)', 'MOD':'rgb(255,140,0)', 'AZ':'rgb(255,20,147)', 'NVXD' : 'rgb(0,0,0)'}


# In[3]:


st.title('Casus 2: Vaccinaties')


# In[4]:


st.caption('Groep 4: Rajiv Chhatta, Noud van de Kreeke, Kevin Luo en Kris de Maat')


# In[5]:


st.write('Deze blog gaat over de voortgang van de vaccinatie graad tegen covid. Hiervoor wordt gebruik gemaakt van data van de European Centre for Disease Prevention and Control. In deze blog zal er specifiek gekeken worden naar Nederland en de buurlanden Duitsland en België.')


# In[6]:


st.header('Data import')


# In[7]:


st.write('De data van European Centre for Disease Prevention and Control wordt als een csv file binnengehaald middels een API. Dit is een open database, waardoor er geen key nodig is. Deze wordt dan gelijk gelezen met de pd.read_csv functie. Er zijn twee datasets binnengehaald. Eén dataset gaat over de vaccinaties in Europa en de andere dataset gaat over aantal besmettingen in Europa.')


# In[8]:


data = pd.read_csv('data.csv')
data2 = pd.read_csv('data_newcases.csv')

# In[55]:


st.code('''data = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/vaccine_tracker/csv/data.csv')
data2 = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/testing/csv/data.csv')''', language = 'python')


# In[9]:


st.header('Data manipulatie')


# In[10]:


st.write('We zijn begonnen met het verkennen van de datasets. De kolommen ‘Region’ en ‘FirstDoseRefused’ zijn verwijderd, omdat deze niet veel informatie toevoegen. ‘FirstDoseRefused’ bevat grotendeels missing values.')


# In[11]:


st.write('Van de rijen waarvan de leeftijdsgroep niet overeenkomen met ‘ALL’ in de kolom ‘TargetGroup’  worden verwijderd. Dit is omdat er alleen naar de leeftijdsgroep ‘ALL’ (18+) is gekeken. ')


# In[12]:


data = data.drop(['Region','FirstDoseRefused'], axis=1)
data['NumberDosesReceived'] = data['NumberDosesReceived'].fillna(0)
data['NumberDosesExported'] = data['NumberDosesExported'].fillna(0)
data.drop(data[data['TargetGroup']!= 'ALL'].index, inplace =True)

data = data.replace(to_replace=17407585,value =17407585-0.2*17407585)
data = data.replace(to_replace=83166711,value =83166711-13750000)
data = data.replace(to_replace=11522440,value =11522440-2312122)


# In[13]:


st.code('''data = data.drop(['Region','FirstDoseRefused'], axis=1)
data['NumberDosesReceived'] = data['NumberDosesReceived'].fillna(0)
data['NumberDosesExported'] = data['NumberDosesExported'].fillna(0)
data.drop(data[data['TargetGroup']!= 'ALL'].index, inplace =True)

data = data.replace(to_replace=17407585,value =17407585-0.2*17407585)
data = data.replace(to_replace=83166711,value =83166711-13750000)
data = data.replace(to_replace=11522440,value =11522440-2312122)''', language = 'python')


# In[14]:


st.write('Vervolgens hebben we nieuwe variabelen aangemaakt. Er is per land en per week gekeken naar het aantal mensen die de eerste dosis, twee dosis en booster prik hebben genomen. Hiervan is de cumulatieve som van genomen.')


# In[51]:


data = data.assign(SumFirstDose = lambda x: x.groupby('ReportingCountry')["FirstDose"].cumsum())
data = data.assign(TotalFirstDoseVaccinated = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumFirstDose"].transform('max'))

data = data.assign(SumSecondDose = lambda x: x.groupby('ReportingCountry')["SecondDose"].cumsum())
data = data.assign(TotalSecondDoseVaccinated = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumSecondDose"].transform('max'))

data = data.assign(SumDoseAdditional1 = lambda x: x.groupby('ReportingCountry')["DoseAdditional1"].cumsum())
data = data.assign(TotalDoseAdditional1 = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumDoseAdditional1"].transform('max'))


# In[52]:


st.code('''data = data.assign(SumFirstDose = lambda x: x.groupby('ReportingCountry')["FirstDose"].cumsum())
data = data.assign(TotalFirstDoseVaccinated = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumFirstDose"].transform('max'))

data = data.assign(SumSecondDose = lambda x: x.groupby('ReportingCountry')["SecondDose"].cumsum())
data = data.assign(TotalSecondDoseVaccinated = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumSecondDose"].transform('max'))

data = data.assign(SumDoseAdditional1 = lambda x: x.groupby('ReportingCountry')["DoseAdditional1"].cumsum())
data = data.assign(TotalDoseAdditional1 = lambda x: x.groupby(['YearWeekISO','ReportingCountry'])["SumDoseAdditional1"].transform('max'))''', language = 'python')


# In[16]:


st.write('Daarnaast is er ook gekeken naar het aantal percentages gevaccineerde van de totale bevolking per land. Deze zijn in de kolommen ‘PercentageFirstDose’, ‘TotalSecondDose’ en ‘PercentageAdditional1’ gezet.')


# In[17]:


data['PercentageFirstDose'] = data['TotalFirstDoseVaccinated'] / data['Population'] * 100 
data['PercentageSecondDose'] = data['TotalSecondDoseVaccinated'] / data['Population'] * 100 
data['PercentageAdditional1'] =  data['TotalDoseAdditional1'] / data['Population'] * 100 


# In[ ]:


st.code('''data['PercentageFirstDose'] = data['TotalFirstDoseVaccinated'] / data['Population'] * 100 
data['PercentageSecondDose'] = data['TotalSecondDoseVaccinated'] / data['Population'] * 100 
data['PercentageAdditional1'] =  data['TotalDoseAdditional1'] / data['Population'] * 100 ''', language = 'python')


# In[18]:


st.write('We willen ook kijken naar aantal besmettingen per week in een land. Hiervoor wordt de data uit de tweede dataset gehaald. Het land en de datum worden gebruikt als keys om de twee datasets samen te voegen. Om de keys te gebruiken, moeten de namen van de kolommen ook hetzelfde zijn.')


# In[19]:


data_newcases = data2[['country_code', 'year_week', 'new_cases']]
data_newcases.rename(columns = {'country_code':'ReportingCountry', 'year_week':'YearWeekISO'}, inplace = True)


# In[53]:


st.code('''data_newcases = data2[['country_code', 'year_week', 'new_cases']]
data_newcases.rename(columns = {'country_code':'ReportingCountry', 'year_week':'YearWeekISO'}, inplace = True)''', language = 'python')


# In[ ]:


st.write("Om de twee datasets samen te voegen is de merge functie gebruikt. De kolom 'new_cases' van de tweede dataset wordt toegevoegd aan de eerste dataset.")


# In[54]:


st.code('''data = pd.merge(data, data_newcases, how = 'left', on = ['ReportingCountry', 'YearWeekISO'])
st.write(data)''', language = 'python')


# In[20]:


st.write('Hieronder is het uiteindelijke dataframe te zien:')


# In[21]:


data = pd.merge(data, data_newcases, how = 'left', on = ['ReportingCountry', 'YearWeekISO'])
st.write(data)


# In[22]:


InputCountry = st.sidebar.selectbox('Select Country', ('NL', 'BE', 'DE',))


# In[23]:


CountrySelect = data[data['ReportingCountry']==InputCountry]


# In[24]:


st.write('Hieronder is de gefilterde dataframe van de geselecteerde land te zien:')


# In[25]:


st.dataframe(CountrySelect)


# In[26]:


start_datum = st.sidebar.selectbox('Start datum', (CountrySelect['YearWeekISO'].drop_duplicates()))
eind_datum = st.sidebar.selectbox('Eind datum', (CountrySelect['YearWeekISO'].drop_duplicates()))


# In[27]:


tijd_select = CountrySelect.set_index('YearWeekISO')

datum= (tijd_select.loc[start_datum:eind_datum])


# In[28]:


datum['week'] = datum.index


# In[29]:


st.subheader('Geïmporteerd en geëxporteerde doses')


# In[30]:


st.write('In de bar plot wordt weergeven welke vaccinatie-soorten en de hoeveelheden hiervan, door het desbetreffende land zijn aangeschaft. ')


# In[31]:


st.write('Voor alle drie landen is Pfizer het meest toegediende vaccinatie soort. Hierna volgen Moderna en Astrazeneca.')


# In[32]:


st.write('In de bar plot wordt ook weergeven welke vaccinatie-soorten en de hoeveelheden hiervan, door het desbetreffende land zijn geëxporteerd. ')


# In[33]:


st.write('Van Nederland is Moderna het meest geëxporteerd. Hierna volgen Astrazeneca en Janssen. Van België en Duitsland wordt Astrazeneca het meest geëxporteerd.')


# In[34]:


NumberDoses = st.selectbox('Geïmporteerd/geëxporteerd', ('NumberDosesReceived','NumberDosesExported' ))


# In[35]:


fig = px.bar(data_frame = datum, 
             x ='Vaccine',
             y= NumberDoses,
             color='Vaccine', color_discrete_map = color_vaccine_map, 
             labels = {'NumberDosesReceived':'Aantal geïmporteerde vaccins', 
                       'NumberDosesExported':'Aantal geëxporteerde vaccins',
                      'Vaccine':'Vaccin soorten'})

fig.update_layout(title = {'text' : 'Aantal doses geïmporteerd/geëxporteerd per soort vaccin', 'x':0.48, 'y':0.95})

#fig.show()
st.write(fig)


# In[36]:


st.subheader('Wekelijks toegediende vaccinatie samenstelling')


# In[37]:


st.write('In deze histogram wordt er gekeken wat de samenstelling van de toegediende vaccinaties zijn verspreid over de afgelopen 2 jaar. In de onderstaande histogram is te zien dat alleen Moderna en Pfizer als boosterprik worden gebruikt, terwijl er bij de eerste en tweede vaccinatierondes gebruik is gemaakt van meer vaccinatie soorten.')


# In[38]:


NumberOfDose = ['FirstDose', 'SecondDose', 'DoseAdditional1']

slider = st.select_slider('Aantal doses', options = NumberOfDose )


# In[39]:


fig = px.bar(data_frame =datum, 
             x ='week',
             y= slider,
            color='Vaccine', color_discrete_map = color_vaccine_map,
            labels = {'week':'Week','FirstDose':'Eerste prik', 'SecondDose': 'Tweede prik', 'DoseAdditional1':'Boosterprik'})
fig.update_layout(title = {'text' : 'Wekelijks toegediende vaccinatie samenstelling', 'x':0.3, 'y':0.95})

#fig.show()
st.write(fig)


# In[40]:


st.header('Vaccinatiegraad')


# In[41]:


st.write('In de line chart is te zien wat de vaccinatie graad is voor de eerste, tweede en booster vaccinatie. Dit is verspreid over de afgelopen twee jaar. (kan worden aangepast met de dropdowns aan de linker zijde). Om de y-as te veranderen in percentages kan er gebruik worden gemaakt van de checkbox.')


# In[42]:


checkbox = st.checkbox('Percentage')

if checkbox:
    checkbox = ['PercentageFirstDose', 'PercentageSecondDose', 'PercentageAdditional1']
    
else:
    checkbox = ['TotalFirstDoseVaccinated', 'TotalSecondDoseVaccinated', 'TotalDoseAdditional1']
    
    


# In[43]:


fig = px.line(data_frame = datum, 
             x ='week',
             y= checkbox,
             labels = {'week':'Week',
                       'value':'Percentage/aantal gevaccineerd'}
            )
fig.update_layout(title = {'text' : 'Vaccinatiegraad per doses', 'x':0.3, 'y':0.95})
#fig.show()
st.write(fig)


# In[44]:


st.header('Aantal besmettingen')


# In[45]:


st.write('Het aantal besmettingen verspreid over de afgelopen twee jaar wordt in de plot weergeven. ')


# In[46]:


fig = px.line(data_frame = datum, 
             x ='week',
             y= 'new_cases',
             labels = {'new_cases': 'Nieuwe besmettingen'}
            )
fig.update_layout(title = {'text' : 'Aantal besmettingen per week', 'x':0.5, 'y':0.95})
#fig.show()
st.write(fig)


# In[47]:


st.header('Vergelijking van de vaccinatiegraad')


# In[48]:


st.write('In de line chart is te zien wat de verschillen zijn in de vaccinatie graad voor de eerste vaccinatie tussen de verschillende landen.')


# In[49]:


Data_NL = data[data['ReportingCountry']=='NL']
Data_BE = data[data['ReportingCountry']=='BE']
Data_DE = data[data['ReportingCountry']=='DE']



data_verg = pd.concat([Data_NL, Data_BE, Data_DE], axis=0)

vergelijking = ['PercentageFirstDose', 'PercentageSecondDose', 'PercentageAdditional1']

slider = st.select_slider('Percentage gevaccineerd', options = vergelijking )


# In[50]:


fig = px.line(data_frame = data_verg,
x ='YearWeekISO',
y= slider , color = 'ReportingCountry', 
labels = {'ReportingCountry':'Land', 
          'PercentageFirstDose':'Percentage eerste prik', 
          'PercentageSecondDose':'Percentage boosterprik'})
fig.update_layout(title = {'text' : 'Vergelijking vaccinatiegraad tussen NL, BE en DE', 'x':0.25, 'y':0.95})
#fig.show()
st.write(fig)


# In[ ]:




