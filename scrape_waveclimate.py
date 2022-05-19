from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd
import time
import os
import csv


class ScrapeWaveclimate:
    def __init__(self, climate_dic={}, persistency_dic={}, model_ray_dic={}):
        # Paramètres, valider la correspondance
        self.path_in = 'inputs/'
        self.path_out = 'outputs/'
        self.points_in = 'points.csv'
        self.points_out = 'points_stats.csv'
        self.username = 'demo'
        self.password = ''
        self.wait = 60 # sec, délai max de chargement
        
        # Paramètres défaut
        self.url = 'http://www.waveclimate.com'
        self.path_root = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/'
   
        self.climate_dic = climate_dic
        self.persistency_dic = persistency_dic
        self.model_ray_dic = model_ray_dic

    def initialize_browser(self):
        # Initialiser le navigateur et se connecter
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        try:
            connect_button = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.CLASS_NAME, 'rbutton'))).click()
            time.sleep(1)
            #//TODO handle alert
            accept_button = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'accept'))).click()
            time.sleep(1)
            update_button = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'updatearea')))
        except TimeoutException:
            print("Timed out looking during connection")
            exit()


    def decdeg2dms(self, dd):
        """
        Decimal degrees to min/sec degrees.
        """
        is_positive = dd >= 0
        dd = abs(dd)
        minutes,seconds = divmod(dd*3600,60)
        degrees,minutes = divmod(minutes,60)
        degrees = degrees if is_positive else -degrees
        return (int(degrees), int(minutes), int(seconds))

    def get_location(self):
        try:
            lat_deg, lat_min, _ = self.decdeg2dms(float(self.point_row['lat']))
            lon_deg, lon_min, _ = self.decdeg2dms(float(self.point_row['lon']))
            
            # On zoom au max
            select_zoom = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'dataareasize')))
            Select(select_zoom).select_by_visible_text('50 km')


            # Il faut changer North/South et East/West selon la direction (+/-) de la coordonnée
            if lat_deg < 0:
                lat_deg *= -1
                select_lat = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlatnorthorsouth')))
                Select(select_lat).select_by_visible_text('South')
            else:
                select_lat = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlatnorthorsouth')))
                Select(select_lat).select_by_visible_text('North')
            
            if lon_deg < 0:
                lon_deg *= -1
                select_lon = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactloneastorwest')))
                Select(select_lon).select_by_visible_text('West')
            else:
                select_lon = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactloneastorwest')))
                Select(select_lon).select_by_visible_text('East')
            
            # On insère les données et execute leur formulaire
            form_lat_deg = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlatdeg')))
            form_lat_deg.clear()
            form_lat_deg.send_keys(str(lat_deg))
            form_lat_min = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlatmin')))
            form_lat_min.clear()
            form_lat_min.send_keys(str(lat_min))
            form_lon_deg = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlondeg')))
            form_lon_deg.clear()
            form_lon_deg.send_keys(str(lon_deg))
            form_lon_min = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'exactlonmin')))
            form_lon_min.clear()
            form_lon_min.send_keys(str(lon_min))
            get_data = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, 'getdata')))
            get_data.click()

        except TimeoutException:
            print('Timed out while uploading location form')
            exit()

    def get_all(self):

        # Recuperer les degrés/minutes du point et envoyer le formulaire
        df_points = pd.read_csv(self.path_in + self.points_in, index_col=['id'])
        for id_row, row in df_points.iterrows():

            # On enregistera les infos sur les points extraits ici, créer le fichier si inexistant
            if not os.path.exists(self.path_out + self.points_out):
                if not os.path.exists(self.path_out):
                    os.mkdir(self.path_out)
                with open(self.path_out + self.points_out, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['file', 'id', 'lat', 'lon', 'model', 'records'])

            # On attribue les infos du point pour les appeler des autres fc
            self.point_row = row
            self.point_id = id_row

            self.get_location()
            self.get_climate()
            self.get_persistency()
            self.get_model_ray


    def get_climate(self):
        for suffix, dic in self.climate_dic.items():
            try: 
                link_climate = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'menutooffshorenormals'))).click()
        
                # On choisit les données à récupérer
                sel_months = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'scatter_13x'))).click()
                sel_output = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['output_id']))).click()
                sel_variable = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['variable_id']))).click()
                sel_spectrum = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['spectrum_id']))).click()
                if dic['source_id']:
                    sel_source = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['source_id']))).click()


                # On envoie le formulaire
                content = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'offshorenormalsform')))
                table = content.find_elements_by_tag_name('tbody')[-1]
                table.find_element_by_xpath("//input[@type='button']").click()


                # On recueille les tableaux
                results = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'scatter')))  #//TODO valider id pour non-scatters
                tables = results.find_elements_by_class_name('inner')
                
                descriptions = [desc for desc in results.find_elements_by_tag_name('p') if desc.text]

                if dic['output_id'] == 'outputtype_scatter':
                    assert len(tables) == 13, 'Weird, not 13 tables (' + str(len(tables)) + ')' #//TODO valider pertinence/interoperabilité
                    assert len(descriptions) == 13, 'Weird, not 13 descriptions (' + str(len(descriptions)) + ')'

                # On les enregistre
                for i in range(len(tables)):

                    table = tables[i].find_element_by_tag_name('tbody')

                    # On cré le dossier du point(au besoin) et le nom de fichier
                    if not os.path.exists((self.path_out + str(self.point_id))):
                        os.mkdir(self.path_out + str(self.point_id))
                    month = table.find_element_by_tag_name('tr').find_element_by_tag_name('th').text
                    if month == ' ' and dic['output_id'] == 'outputtype_scatter':
                        month = 'ALL'
                    elif month == ' ' and dic['output_id'] == 'outputtype_scat3d':
                        month = descriptions[i].text.split('\n')[0].split(' is ')[1].replace(' ', '-')
                    elif month == ' ':
                        print('wtf')
                        exit()    
                    name_out = str(self.point_id) + '_' + month + '_' + suffix + '.csv'

                    # On mets les infos dans un CSV de référence
                    with open(self.path_out + '/' + self.points_out, 'a', newline='') as f:
                        writer = csv.writer(f)
                        model_recs = descriptions[i].text.split(' model records')[0].split(' ')[-1]
                        data_source = descriptions[i].text.split('Data source is ')[1].split('\n')[0]
                        stats = [name_out, self.point_id, self.point_row['lat'], self.point_row['lon'], data_source, model_recs]
                        writer.writerow(stats)

                    # On mets le tableau dans un CSV
                    with open(self.path_out + '/' + str(self.point_id) + '/' + name_out, 'w', newline='') as f:
                        writer = csv.writer(f)
                        rows_src = table.find_elements_by_tag_name('tr')
                        for row_src in rows_src:
                            headers = row_src.find_elements_by_tag_name('th')
                            cells = row_src.find_elements_by_tag_name('td')
                            cols_ele = headers + cells
                            vals = [val.text for val in cols_ele]

                            # Exception pour ligne "Total" avec les headers fusionnés
                            if len(headers) == 1:
                                vals = [''] + vals
                                
                            writer.writerow(vals)

            except TimeoutException:
                print('Timed out while getting climate results')
                exit()


    def get_persistency(self):
        for suffix, dic in self.persistency_dic.items():
            try:
                link_climate = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'menutooffshorenormals'))).click()
                link_persisteny = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'menutooffshorepersist'))).click()
        
                # On choisit les données à récuperer
                sel_output = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['output_id']))).click()
                sel_wave = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, dic['wave_id']))).click()
                for condition_dic in dic['conditions']:
                    sel_parameter = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, condition_dic['parameter_id']))).click()
                    sel_type = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, condition_dic['type_id']))).click()
                    send_condition = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, condition_dic['condition_id'])))
                    send_condition.clear()
                    send_condition.send_keys(str(condition_dic['condition_value']))

                # On envoie le formulaire
                content = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'offshorepersistform')))
                table = content.find_elements_by_tag_name('tbody')[-1]
                table.find_element_by_xpath("//input[@type='button']").click()

                results = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'output'))) 
                table = results.find_element_by_class_name('inner').find_element_by_tag_name('tbody')
                description = [desc for desc in results.find_elements_by_tag_name('p') if desc.text]
                
                # On cré le dossier du point(au besoin) et le nom de fichier
                if not os.path.exists((self.path_out + str(self.point_id))):
                    os.mkdir(self.path_out + str(self.point_id))
                name_out = str(self.point_id) + '_' + suffix + '.csv'

                # On mets les infos dans un CSV de référence
                with open(self.path_out + '/' + self.points_out, 'a', newline='') as f:
                    writer = csv.writer(f)
                    model_recs = description[0].text.split(' model records')[0].split(' ')[-1]
                    data_source = description[0].text.split('Data source is ')[1].split('\n')[0]
                    stats = [name_out, self.point_id, self.point_row['lat'], self.point_row['lon'], data_source, model_recs]
                    writer.writerow(stats)

                # On mets le tableau dans un CSV
                with open(self.path_out + '/' + str(self.point_id) + '/' + name_out, 'w', newline='') as f:
                    writer = csv.writer(f)
                    rows_src = table.find_elements_by_tag_name('tr')
                    for row_src in rows_src:
                        headers = row_src.find_elements_by_tag_name('th')
                        cells = row_src.find_elements_by_tag_name('td')
                        cols_ele = headers + cells
                        vals = [val.text for val in cols_ele]

                        writer.writerow(vals)

                image = results.find_element_by_tag_name('center').find_element_by_tag_name('img')
                image.save_screenshot(name_out.split('.')[0] + '.png')

            except TimeoutException:
                print('Timed out while getting persistency results')
                exit()


    def get_model_ray(self):
        for suffix, dic in self.model_ray_dic.items():
            link_model_ray = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.ID, 'menutoswrtlocation'))).click()
        
            send_water = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, dic['water_dic']['water_name'])))
            send_water.clear()
            send_water.send_keys(str(dic['water_dic']['water_value']))

            send_bed = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, dic['bed_dic']['bed_name'])))
            send_bed.clear()
            send_bed.send_keys(str(dic['bed_dic']['bed_value']))

            for condition_uncheck in dic['uncheck_conditions_names']:
                sel_condition = WebDriverWait(self.driver, self.wait).until(EC.presence_of_element_located((By.NAME, condition_uncheck))).click()

            #//TODO make logic for wait