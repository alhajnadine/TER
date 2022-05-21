# from tkinter import N
# from webbrowser import get
from asyncio import selector_events
from distutils.log import debug
from re import T
from flask import Flask, render_template
import sqlalchemy as db
import pandas as pd
import requests
import copy
import json
from flask import request




app = Flask(__name__)

def get_participant_virtual_ids(url='postgresql://user1:nadine@localhost:5432/ter', table_name='data_processed_record_v2'):
    '''The preprocessed table'''
    engine = db.create_engine(url) 
    connection = engine.connect()
    metadata = db.MetaData()
    data = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
    results = connection.execute(db.select([data.columns.participant_virtual_id.distinct()]))    
    df = pd.DataFrame(results)
    df.columns = ['participant_virtual_id']
    return df.participant_virtual_id.to_list()

def get_canarin(url='postgresql://user1:1234@localhost:5432/ter', table_name='canarin'):
    '''The preprocessed table'''
    engine = db.create_engine(url) 
    connection = engine.connect()
    metadata = db.MetaData()
    data = db.Table(table_name, metadata, autoload=True, autoload_with=engine)
    results = connection.execute(db.select([data.columns.canarin.distinct()]))    
    df = pd.DataFrame(results)
    df.columns = ['canarin']
    return df.canarin.to_list()

def get_dimensions():
    return ['None','Temperature','Humidity','PM','NO2','BC','All']

def get_options():
    return ['Original Data','Preprocessed Data','Original VS Preprocessed']

def get_optionsNo2():
    return ['Original Data','Preprocessed Data','Original VS Preprocessed','Without First 3 Records']

def get_str_of_id(id):
    return "'"+str(id)+"'"

  

@app.route("/",  methods=['GET', 'POST'])
def home():
   
    server = "http://localhost:3000"

    headers = {
        "Authorization":"Bearer eyJrIjoiZ0pDcjhrVVFHcWZSN09MZ1RROFVuMU1wTnpWNXZrdVciLCJuIjoiYWRtaW4iLCJpZCI6MX0=",
        "Content-Type":"application/json",
        "Accept": "application/json"
        }   
    
    if request.method == 'GET': 
        participants = get_participant_virtual_ids()
        dimensions = get_dimensions()
        options = get_options()
        var = participants[-1]
        select2 = dimensions [-1] 
        select3 = options [-2]
        deletePanels(server=server,uid=var,headers=headers)
        return render_template('index.html', participants=participants, dimensions=dimensions, options=options, var=var)
        
    else:
        participants = get_participant_virtual_ids()
        dimensions = get_dimensions()
        options = get_options()
        # var=request.form.get('part_select')
        var = request.form.get('part_select')
        select = request.form.get('part_select')
        select2 = request.form.get('dim_select')
        select3 = request.form.get('opt_select')
        
        query_temperature="select distinct(r.*)\r\nfrom \r\n(\r\nselect  \"data_processed_record_v2\".\"time\" AS \"time\",\r\n  \"data_processed_record_v2\".\"Temperature\" AS \"Température\"\r\nfrom \"canarin\",\"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"data_processed_record_v2\".\"participant_virtual_id\"=\"participant\".\"participant_virtual_id\"\r \nand \"participant\".\"participant_virtual_id\"  = "+get_str_of_id(select) +"\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\r\n) as r\r\norder by 1\r\n"                
        title='Temperature'
        query_humidity="select distinct(r.*)\r\nfrom \r\n(\r\nselect  \"data_processed_record_v2\".\"time\" AS \"time\",\r\n  \"data_processed_record_v2\".\"Humidity\" AS \"Humidité\"\r\nfrom \"canarin\",\"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere  \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"data_processed_record_v2\".\"participant_virtual_id\"=\"participant\".\"participant_virtual_id\"\r\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\r\n) as r\r\norder by 1"             
        title_humidity='Humidity'
        query_PM="select distinct(r.*)\r\nfrom \r\n(\r\nselect  \"data_processed_record_v2\".\"time\" AS \"time\",\r\n  \"data_processed_record_v2\".\"PM1.0\" AS \"PM1.0\"\r\nfrom \"canarin\",\"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"data_processed_record_v2\".\"participant_virtual_id\"=\"participant\".\"participant_virtual_id\"\r\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\r\n) as r\r\norder by 1\r\n\r\n"
        title_PM="PM"
        query_NO2="select distinct(r.*)\r\nfrom \r\n(select  \"data_processed_record_v2\".\"time\" AS \"time\",\r\n  \"data_processed_record_v2\".\"NO2\" AS \"NO2\"\r\nfrom \"cairsens\",\"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"data_processed_record_v2\".\"participant_virtual_id\"=\"participant\".\"participant_virtual_id\"\r\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\r\nand $__timeFilter(\"data_processed_record_v2\".\"time\")\r\n) as r\r\norder by 1"
        title_NO2="NO2"
        query_BC="select distinct(r.*)\r\nfrom \r\n(select \"time\" AS \"time\", \"BC\" AS \"BC\"\r\nfrom \"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere\"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"participant\".\"participant_virtual_id\" = \"data_processed_record_v2\".\"participant_virtual_id\"\r\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\" \r\nand $__timeFilter(\"data_processed_record_v2\".\"time\") and \"data_processed_record_v2\".\"participant_virtual_id\"= \"participant\".\"participant_virtual_id\"\r\n) as r\r\norder by 1\r\n"
        title_BC="BC"
        
        original_temperature="select distinct(r.*)\nfrom \n(\nselect  \"canarinMeasure\".\"timestamp\" AS \"time\",\n  \"canarinMeasure\".\"value_num\" AS \"Température\"\nfrom \"canarin\",\"canarinMeasure\",\"campaignParticipantKit\",\"kit\",\"participant\"\nwhere \"canarinMeasure\".\"canarin_id\"=\"kit\".\"canarin_id\"\nand \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\nand \"canarinMeasure\".\"timestamp\" \nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\nand $__timeFilter(\"canarinMeasure\".\"timestamp\") \nand \"canarinMeasure\".\"canarin_id\"=\"canarin\".\"id\"\nand \"canarinMeasure\".\"type_id\" = 4) as r\norder by 1\n"

        original_humidity="select distinct(r.*)\nfrom \n(\nselect  \"canarinMeasure\".\"timestamp\" AS \"time\",\n  \"canarinMeasure\".\"value_num\" AS \"Humidité\"\nfrom \"canarin\",\"canarinMeasure\",\"campaignParticipantKit\",\"kit\",\"participant\"\nwhere \"canarinMeasure\".\"canarin_id\"=\"kit\".\"canarin_id\"\nand \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\nand \"canarinMeasure\".\"timestamp\" \nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\nand $__timeFilter(\"canarinMeasure\".\"timestamp\") \nand \"canarinMeasure\".\"canarin_id\"=\"canarin\".\"id\"\nand \"canarinMeasure\".\"type_id\" = 5) as r\norder by 1\n"
        original_NO2= "select distinct(r.*)\nfrom \n(select  \"cairsensMeasure\".\"timestamp\" AS \"time\",\n  \"cairsensMeasure\".\"level\" AS \"NO2\"\nfrom \"cairsens\",\"cairsensMeasure\",\"campaignParticipantKit\",\"kit\",\"participant\"\nwhere \"cairsensMeasure\".\"cairsens_id\"=\"kit\".\"cairsens_id\"\nand \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\nand \"participant\".\"participant_virtual_id\" ="+get_str_of_id(select)+"\nand \"cairsensMeasure\".\"timestamp\" \nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\nand $__timeFilter(\"cairsensMeasure\".\"timestamp\") and \"cairsensMeasure\".\"cairsens_id\"=\"cairsens\".\"id\"\n) as r\norder by 1\n"
        original_BC ="select distinct(r.*)\nfrom \n(select  \"ae51Measure\".\"timestamp\" AS \"time\",\n  \"ae51Measure\".\"bc\" AS \"BC\"\nfrom \"ae51\",\"ae51Measure\",\"campaignParticipantKit\",\"kit\",\"participant\"\nwhere\"ae51Measure\".\"ae51_id\"=\"kit\".\"ae51_id\"\nand \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\nand \"participant\".\"participant_virtual_id\"  ="+get_str_of_id(select)+"\nand \"ae51Measure\".\"timestamp\" \nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\nand $__timeFilter(\"ae51Measure\".\"timestamp\") and \"ae51Measure\".\"ae51_id\"=\"ae51\".\"id\"\n) as r\norder by 1\n"
        original_PM = "select distinct(r.*)\nfrom \n(\nselect  \"canarinMeasure\".\"timestamp\" AS \"time\",\n  \"canarinMeasure\".\"value_num\" AS \"PM10\"\nfrom \"canarin\",\"canarinMeasure\",\"campaignParticipantKit\",\"kit\",\"participant\"\nwhere \"canarinMeasure\".\"canarin_id\"=\"kit\".\"canarin_id\"\nand \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\nand \"participant\".\"participant_virtual_id\"="+get_str_of_id(select)+"\nand \"canarinMeasure\".\"timestamp\" \nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\nand $__timeFilter(\"canarinMeasure\".\"timestamp\") \nand \"canarinMeasure\".\"canarin_id\"=\"canarin\".\"id\"\nand \"canarinMeasure\".\"type_id\" = 8) as r\norder by 1\n"
       
        if (select2 == 'Temperature'):
            if(select3=='Preprocessed Data'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1],queries=[query_temperature],titles=[title],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)    
            elif(select3=='Original Data'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1],queries=[original_temperature],titles=[title],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)    
            elif(select3=='Original VS Preprocessed'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1,2],queries=[original_temperature,query_temperature],titles=["Original Temperature", "Preprocessed Temperature"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0}],uid=select,headers=headers,server=server)  
        
        elif(select2 == 'Humidity'):
                if(select3=='Preprocessed Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[query_humidity],titles=[title_humidity],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
                elif(select3=='Original Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[original_humidity],titles=[title_humidity],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
                elif(select3=='Original VS Preprocessed'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1,2],queries=[original_humidity,query_humidity],titles=["Original Humidity", "Preprocessed Humidity"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0}],uid=select,headers=headers,server=server)  
        
        elif(select2 == 'PM'):
            if(select3=='Preprocessed Data'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1],queries=[query_PM],titles=[title_PM],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
            elif(select3=='Original Data'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1],queries=[original_PM],titles=[title_PM],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)    
            elif(select3=='Original VS Preprocessed'):
                deletePanels(server=server,uid=select,headers=headers)
                dash_data=getDash(server=server,uid=select,headers=headers)
                updateDash(dash_data=dash_data,ids=[1,2],queries=[original_PM,query_PM],titles=["Original PM", "Preprocessed PM"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0}],uid=select,headers=headers,server=server)  
            
        
        elif(select2 == 'NO2'):
            if(select3=='Preprocessed Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[query_NO2],titles=[title_NO2],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
            elif(select3=='Original Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[original_NO2],titles=[title_NO2],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
            elif(select3=='Original VS Preprocessed'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1,2],queries=[original_NO2,query_NO2],titles=["Original NO2", "Preprocessed NO2"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0}],uid=select,headers=headers,server=server)  
            
        elif(select2 == 'BC'):
            if(select3=='Preprocessed Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[query_BC],titles=[title_BC],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
            elif(select3=='Original Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1],queries=[original_BC],titles=[title_BC],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0}],uid=select,headers=headers,server=server)
            elif(select3=='Original VS Preprocessed'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1,2],queries=[original_BC,query_BC],titles=["Original BC", "Preprocessed BC"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0}],uid=select,headers=headers,server=server)  
            
        elif (select2 == 'All'):
            if(select3=='Preprocessed Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1,2,3,4,5],queries=[query_temperature,query_humidity,query_PM,query_NO2,query_BC],titles=[title,title_humidity,title_PM,title_NO2,title_BC],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0},{'h': 8, 'w': 12, 'x': 0, 'y': 9},{'h': 8, 'w': 12, 'x': 12, 'y': 9},{'h': 8, 'w': 12, 'x': 0, 'y': 17}],uid=select,headers=headers,server=server)
            elif(select3=='Original Data'):
                    deletePanels(server=server,uid=select,headers=headers)
                    dash_data=getDash(server=server,uid=select,headers=headers)
                    updateDash(dash_data=dash_data,ids=[1,2,3,4,5],queries=[original_temperature,original_humidity,original_PM,original_NO2,original_BC],titles=[title,title_humidity,title_PM,title_NO2,title_BC],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0},{'h': 8, 'w': 12, 'x': 0, 'y': 9},{'h': 8, 'w': 12, 'x': 12, 'y': 9},{'h': 8, 'w': 12, 'x': 0, 'y': 17}],uid=select,headers=headers,server=server)
            elif(select3=='Original VS Preprocessed'):
                   deletePanels(server=server,uid=select,headers=headers)
                   dash_data=getDash(server=server,uid=select,headers=headers)
                   updateDash(dash_data=dash_data,ids=[1,2,3,4,5,6,7,8,9,10],queries=[original_temperature,original_humidity,original_PM,original_NO2,original_BC,query_temperature,query_humidity,query_PM,query_NO2,query_BC],titles=["Original Temperature", "Original Humidity", "Original Pm", "Original NO2", "Original BC","Preprocessed Temperature", "Preprocessed Humidity", "Preprocessed PM", "Preprocessed NO2", "Preprocessed BC"],gridPosions=[{'h': 9, 'w': 12, 'x': 0, 'y': 0},{'h': 9, 'w': 12, 'x': 12, 'y': 0},{'h': 8, 'w': 12, 'x': 0, 'y': 9},{'h': 8, 'w': 12, 'x': 12, 'y': 9},{'h': 8, 'w': 12, 'x': 0, 'y': 17},{'h': 8, 'w': 12, 'x': 12, 'y': 17}],uid=select,headers=headers,server=server)
            
        
        
       
       

        return render_template('index.html',participants=participants,dimensions=dimensions,options=options,var=var,select2=select2,select3=select3)
        
        
       

        
        
        




  
@app.route("/" , methods=['GET', 'POST'])
def test():
    select = request.form.get('part_select')
    select2 = request.form.get('dim_select')
    select3 = request.form.get('opt_select')
    return  '{} {} {}'.format(select, select2, select3)

def deletePanels(server,uid,headers):
    # print(uid)
    url = server + "/api/dashboards/uid/" + uid
    r = requests.get(url=url, headers=headers, verify=False)
    dash_data = r.json()
    dash_data["dashboard"]['panels']=[]
    dash_data["dashboard"]['version'] =dash_data['dashboard']['version'] + 1
    dash_data["overwrite"] = True
    url = server + "/api/dashboards/db"
    r = requests.post(url=url, headers=headers, data=json.dumps(dash_data), verify=False)
    
def getDash(server,uid,headers):
    
    # get the content of dashboard from the example above
    url = server + "/api/dashboards/uid/" + uid
    r = requests.get(url=url, headers=headers, verify=False)
    dash_data = r.json()
    dash_data["dashboard"]['panels']=[]

    return dash_data

def updateDash(dash_data,ids,queries,titles,gridPosions,server,uid,headers):
    new_dashboard_data =dash_data
    dashboard_data = copy.deepcopy(new_dashboard_data)
    
    for id,query,title,gridPos in zip(ids,queries,titles,gridPosions):
        panel=panelBuilder(id,query,title,gridPos)
        dashboard_data['dashboard']['panels'].append(panel)
        
    dashboard_data["dashboard"]['id'] = dash_data['dashboard']['id']
    dashboard_data["dashboard"]['uid'] =uid
    dashboard_data["dashboard"]['version'] =dash_data['dashboard']['version'] + 1
    dashboard_data["overwrite"] = True
    url = server + "/api/dashboards/db"
    r = requests.post(url=url, headers=headers, data=json.dumps(dashboard_data), verify=False)
    

def panelBuilder(id,query,title,gridPos= {'h': 9, 'w': 12, 'x': 0, 'y': 0}):
    panel={'aliasColors': {},
     'bars': False,
     'dashLength': 10,
     'dashes': False,
     'datasource': 'PostgreSQL',
     'fill': 1,
     'id':id,
     'gridPos':gridPos,
     'fillGradient': 0,
     'hiddenSeries': False,
     'legend': {'avg': False,
      'current': False,
      'max': False,
      'min': False,
      'show': True,
      'total': False,
      'values': False},
     'lines': True,
     'linewidth': 1,
     'nullPointMode': 'null',
     'options': {'dataLinks': []},
     'percentage': False,
     'pointradius': 2,
     'points': False,
     'renderer': 'flot',
     'seriesOverrides': [],
     'spaceLength': 10,
     'stack': False,
     'steppedLine': False,
     'thresholds': [],
     'timeFrom': None,
     'timeRegions': [],
     'timeShift': None,
     'targets' :[{'rawSql':query}],                
     'title': title,
     'tooltip': {'shared': True, 'sort': 0, 'value_type': 'individual'},
     'type': 'graph',
     'xaxis': {'buckets': None,
      'mode': 'time',
      'name': None,
      'show': True,
      'values': []},
     'yaxes': [{'format': 'short',
       'label': None,
       'logBase': 1,
       'max': None,
       'min': None,
       'show': True},
      {'format': 'short',
       'label': None,
       'logBase': 1,
       'max': None,
       'min': None,
       'show': True}],
     'yaxis': {'align': False, 'alignLevel': None}}
    
    
    return panel

# def queryBuilder():
#     query_temperature="select distinct(r.*)\r\nfrom \r\n(\r\nselect  \"data_processed_record_v2\".\"time\" AS \"time\",\r\n  \"data_processed_record_v2\".\"Temperature\" AS \"Température\"\r\nfrom \"canarin\",\"data_processed_record_v2\",\"campaignParticipantKit\",\"kit\",\"participant\"\r\nwhere \"kit\".\"id\"=\"campaignParticipantKit\".\"kit_id\"\r\nand \"campaignParticipantKit\".\"participant_id\"=\"participant\".\"id\"\r\nand \"data_processed_record_v2\".\"participant_virtual_id\"=\"participant\".\"participant_virtual_id\"\r\nand \"kit\".\"id\" in ('117')\r\nand \"participant\".\"id\"  in ('98')\r\nand \"data_processed_record_v2\".\"time\" \r\nbetween \"campaignParticipantKit\".\"start_date\" and \"campaignParticipantKit\".\"end_date\"\r\n) as r\r\norder by 1\r\n"

#     panelTemperature=panelBuilder(id=1,title='Temperature',query=query_temperature,gridPos={'h': 9, 'w': 12, 'x': 0, 'y': 0})

#     panelTemperature

#     getDash.dash_data['dashboard']['panels'].append(panelTemperature)
    
#     return panelTemperature

# def updateDash():
#     #Update the dashboard

#     getDash.dashboard_data["dashboard"]['id'] = getDash.dash_data['dashboard']['id']
#     getDash.dashboard_data["dashboard"]['uid'] =getDash.uid
#     getDash.dashboard_data["dashboard"]['version'] = getDash.dash_data['dashboard']['version'] + 1
#     getDash.dashboard_data["overwrite"] = True
#     url = getDash.server + "/api/dashboards/db"
#     r = requests.post(url=url, headers=getDash.headers, data=json.dumps(getDash.dashboard_data), verify=False)
#     return print(r.json())

if __name__=='__main__':
    app.run(debug=True)