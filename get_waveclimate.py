from scrape_waveclimate import ScrapeWaveclimate

# Données à extraire, i.e. les buttons à cocher (sur lesquels itérer) par ID //TODO ajuster script pour les options hors-scatter
# Sous la forme {[suffix_export] : {[variables...]}}
# Garder 'source_id' vide pour scatter3d
climate_dic = {
    'hstp' : {
        'output_id': 'outputtype_scatter',
        'variable_id': 'scatter_parameters_hs_tp',
        'spectrum_id': 'scatter_tsw_t',
        'source_id': 'scatter_offshoredatasource_ww3'
    }, 
    'hsth': {
        'output_id': 'outputtype_scatter',
        'variable_id': 'scatter_parameters_hs_th',
        'spectrum_id': 'scatter_tsw_t',
        'source_id': 'scatter_offshoredatasource_ww3'
    },
    'hstpth': {
        'output_id': 'outputtype_scat3d',
        'variable_id': 'scat3d_parameters_hs_tp_th',
        'spectrum_id': 'scat3d_tsw_t',
        'source_id': ''
    }
}

persistency_dic = {
    'test_name': {
        'output_id': 'persist_type_cover',
        'wave_id': 'persist_waveperiod_pt',
        'conditions': [{
            'parameter_id': 'persist_parameters_ht',
            'type_id': 'persist_condition_ht_lt',
            'condition_id': 'persist_limit_ht',
            'condition_value': '1'
        }, {
            'parameter_id': 'persist_parameters_hl',
            'type_id': 'persist_condition_hl_gt',
            'condition_id': 'persist_limit_hl',
            'condition_value': '0.5'
        }]
    }
}     


model_ray_dic = {
    'model_ray': {
        'water_dic': {
            'water_name': 'waterlevel',
            'water_value': '0'
        },
        'bed_dic': {
            'bed_name': 'bedlevel',
            'bed_value': '0'
        },
        'uncheck_conditions_names': [
            'wavebreaking',
        ]
    }
}


SWC = ScrapeWaveclimate(
    climate_dic=climate_dic, 
    persistency_dic=persistency_dic,
    model_ray_dic=model_ray_dic,
)
SWC.initialize_browser()
SWC.get_all()