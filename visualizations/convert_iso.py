import numpy as np
import pandas as pd
import pycountry

def get_country_iso3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None
    