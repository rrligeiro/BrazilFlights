import requests
import json
import networkx as nx
import matplotlib.pyplot as plt
import geobr
import geopandas as gpd
import datetime as dt
import pandas as pd

MONTHS = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
STATES = {'AC': 'Acre','AL': 'Alagoas','AP': 'Amapá','AM': 'Amazonas','BA': 'Bahia','CE': 'Ceará','DF': 'Distrito Federal','ES': 'Espírito Santo','GO': 'Goiás','MA': 'Maranhão','MT': 'Mato Grosso','MS': 'Mato Grosso do Sul','MG': 'Minas Gerais','PA': 'Pará','PB': 'Paraíba','PR': 'Paraná','PE': 'Pernambuco','PI': 'Piauí','RJ': 'Rio de Janeiro','RN': 'Rio Grande do Norte','RS': 'Rio Grande do Sul','RO': 'Rondônia','RR': 'Roraima','SC': 'Santa Catarina','SP': 'São Paulo','SE': 'Sergipe','TO': 'Tocantins'}

def __main__(date_range='2023-01-01/2023-01-01', departure_hour_range=None, code_state=None, transport_object=None):
    #date_range format: yyyy-mm-dd/yyyy-mm-dd
    #departure_hour_range format: '00:00-23:59'
    #code_state format: ['SP','RJ','MG',...]
    #transport_object format: "PASSAGEIROS" or "CARGA"
    flights = get_flights(date_range, departure_hour_range, transport_object)
    routes = get_routes(flights)
    airports = get_airports_codes()

    if code_state is not None:
        map = gpd.GeoDataFrame()
        states = [STATES[code] for code in code_state]
        routes = [route for route in routes if route[0] in airports and route[1] in airports and airports[route[0]]['UF'] in states and airports[route[1]]['UF'] in states]
        for code_state in code_state:
            map = pd.concat([map, gpd.GeoDataFrame(geobr.read_state(code_state, year=2018))])
        map.plot(color='lightgrey', edgecolor='black', linewidth=0.2)
        G = make_graph(routes, airports)
        draw_graph(G)
        plt.show()
        
    else:
        G = make_graph(routes, airports)
        map = gpd.GeoDataFrame(geobr.read_state(year=2018))
        map.plot(color='lightgrey', edgecolor='black', linewidth=0.2)
        draw_graph(G)
        plt.show()


def format_url(date):
    #date format: yyyy-mm-dd
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]
    #url = 'https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Registro%20de%20servi%C3%A7os%20a%C3%A9reos/2023/01%20-%20Janeiro/registros_2023-01-01.json'
    url = f'https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Registro%20de%20servi%C3%A7os%20a%C3%A9reos/{year}/{month}%20-%20{MONTHS[int(month)]}/registros_{date}.json'
    return url
    
def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8-sig'))
    else:
        print(f'Error HTTP request: {response.status_code} trying to get data from {url}')
        return []
    
def get_flights(date_range, departure_hour_range, transport_object):
    start_date = date_range.split('/')[0]
    end_date = date_range.split('/')[1]
    if departure_hour_range is None:
        if start_date == end_date:
            flights = get_data(format_url(start_date))
            domestic_flights = [flight for flight in flights if flight['Natureza_Operacao'] == 'DOMÉSTICA']
            if transport_object is not None:
                domestic_flights = [flight for flight in domestic_flights if flight['Objeto_Transporte'] == transport_object]
            return domestic_flights
        else:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
            all_flights = []
            while start_date <= end_date:
                flights = get_data(format_url(str(start_date.date())))
                domestic_flights = [flight for flight in flights if flight['Natureza_Operacao'] == 'DOMÉSTICA']
                if transport_object is not None:
                    domestic_flights = [flight for flight in domestic_flights if flight['Objeto_Transporte'] == transport_object]
                all_flights += domestic_flights
                start_date += dt.timedelta(days=1)
            return all_flights
    elif(departure_hour_range is not None and start_date == end_date):
        flights = get_data(format_url(start_date))
        domestic_flights = [flight for flight in flights if flight['Natureza_Operacao'] == 'DOMÉSTICA']
        if transport_object is not None:
            domestic_flights = [flight for flight in domestic_flights if flight['Objeto_Transporte'] == transport_object]
        return [flight for flight in domestic_flights if flight['Horario_Partida'] >= departure_hour_range.split('-')[0] and flight['Horario_Partida'] <= departure_hour_range.split('-')[1]]
    else:
        print('Error: departure_hour_range is not None and start_date != end_date')
        return []        

def get_routes(flights):
    routes = []
    for flight in flights:
        origin_airport = flight['Cod_Origem']
        destination_airport = flight['Cod_Destino']
        if origin_airport is not None and destination_airport is not None:
            routes.append((origin_airport, destination_airport))
    return routes

def get_airports_codes():
    airports_codes = {}
    
    public_airports = get_data('https://sistemas.anac.gov.br/dadosabertos/Aerodromos/Lista%20de%20aer%C3%B3dromos%20p%C3%BAblicos/AerodromosPublicos.json')
    if public_airports is not None:
        for airport in public_airports:
            airport_code = airport['CódigoOACI']
            if airport_code is not None:
                airports_codes[airport_code] = {'latitude': airport['LatGeoPoint'], 'longitude': airport['LonGeoPoint'], 'UF': airport['UF']}

    private_airports = get_data('https://sistemas.anac.gov.br/dadosabertos/Aerodromos/Lista%20de%20aer%C3%B3dromos%20privados/Aerodromos%20Privados/AerodromosPrivados.json')
    if private_airports is not None:
        for airport in private_airports:
            airport_code = airport['CódigoOACI']
            if airport_code is not None:
                airports_codes[airport_code] = {'latitude': airport['LatGeoPoint'], 'longitude': airport['LonGeoPoint'], 'UF': airport['UF']}

    private_helipontos = get_data('https://sistemas.anac.gov.br/dadosabertos/Aerodromos/Lista%20de%20aer%C3%B3dromos%20privados/Heliponto/Helipontos.json')
    if private_helipontos is not None:
        for airport in private_helipontos:
            airport_code = airport['CódigoOACI']
            if airport_code is not None:
                airports_codes[airport_code] = {'latitude': airport['LATGEOPOINT'], 'longitude': airport['LONGEOPOINT'], 'UF': airport['UF']}

    return airports_codes

def make_graph(flight_routes, airports):
    G = nx.MultiDiGraph()
    for flight in flight_routes:
        if flight[0] in airports and flight[1] in airports:
            G.add_node(flight[0], pos=(float(airports[flight[0]]['longitude']), float(airports[flight[0]]['latitude'])))
            G.add_node(flight[1], pos=(float(airports[flight[1]]['longitude']), float(airports[flight[1]]['latitude'])))
            G.add_edge(flight[0], flight[1])
    return G

def draw_graph(G):
    pos = nx.get_node_attributes(G, 'pos')
    node_size = []
    node_color = []
    node_labels = {}
    for node in G.nodes:
        node_degree = G.degree(node)
        if node_degree >= 1000:
            node_size.append(1000)
            node_color.append('red')
            node_labels[node] = f'{node} - {node_degree}'
        elif node_degree >= 500:
            node_size.append(500)
            node_color.append('orange')
            node_labels[node] = f'{node} - {node_degree}'
        elif node_degree >= 100:
            node_size.append(100)
            node_color.append('yellow')
            node_labels[node] = f'{node} - {node_degree}'
        elif node_degree >= 50:
            node_size.append(50)
            node_color.append('green')
            node_labels[node] = f'{node}'
        elif node_degree >= 10:
            node_size.append(10)
            node_color.append('blue')
            node_labels[node] = f'{node}'
        else:
            node_size.append(5)
            node_color.append('black')
            node_labels[node] = f'{node}'
            
    nx.draw(G, 
            pos=pos,
            labels=node_labels,
            node_size=node_size,
            node_color=node_color,
            width=0.2,
            font_size=6,
            arrowsize=1,
            arrowstyle='->',
            arrows=True,
            connectionstyle='arc3,rad=0.1')

if __name__ == '__main__':
    __main__(date_range = '2023-04-01/2023-04-01', transport_object='PASSAGEIROS')