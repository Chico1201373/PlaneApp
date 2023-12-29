import toga
from toga import ImageView, Table, Box, TextInput, Button,Label
import http.client
import json
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, Pack



class MapboxApp(toga.App):

    def place_marker(self, x, y, text):
        # Adicione um marcador (Label) na posição desejada na imagem do mapa
        marker_label = Label(
            text=text,
            style=Pack(
                color='red',  # Cor do marcador
                font_size=16  # Tamanho da fonte do marcador
            )
        )
        self.main_box.add(marker_label)

    def on_search(self, widget):
        icao24_search = self.search_input.value.strip()
        self.filter_table(icao24_search)

    def on_table_select(self, widget):
        selected_row = self.table.selection
        if selected_row:
            icao24 = selected_row  # Assuming the first column contains the Icao24 value
            self.make_aircraft_request(icao24)

    def filter_table(self, search_term):
        # Clear existing data in the table
        self.table.data.clear()
        print(search_term)

        # Use the original list of icao24 values obtained during startup
        for icao24 in self.icao24_values:
            if search_term in icao24:
                self.table.data.append((icao24,))

    def make_aircraft_request(self, icao24):
        # Make request to get aircraft details
        url_aircraft = f"https://opensky-network.org/api/flights/aircraft?icao24={icao24.icao24}&begin=1517184000&end=1517270400"

        try:
            conn = http.client.HTTPSConnection("opensky-network.org")
            conn.request("GET", url_aircraft)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            aircraft_data = json.loads(data)
            print(response)
            print(data)
            print(aircraft_data)

            # Clear existing data in the details table
            self.details_table.data.clear()

            for aircraft_info in aircraft_data:
                self.details_table.data.append((
                    aircraft_info.get("estDepartureAirport", ""),
                    aircraft_info.get("estArrivalAirport", "")
                ))

            # Trigger a refresh of the details table
            self.details_table.refresh()

        except Exception as e:
            print(f"Error making HTTP request: {e}")

    def getMapBox(self):
        # Mapbox Access Token (replace with your own token)
        mapbox_access_token = 'pk.eyJ1IjoiY2hpY28wNzA2IiwiYSI6ImNscWlsNnkwajFvNGEyaW82MHBrbDRqaWIifQ.cUGoXE2vwPG-0qp34xhlyw'

        # Mapbox Static Image API URL for a world map
        mapbox_path = f'/styles/v1/mapbox/streets-v11/static/0,0,1,0,0/1000x1000?access_token={mapbox_access_token}'

        # Make request to Mapbox API for the map image
        conn = http.client.HTTPSConnection("api.mapbox.com")
        conn.request("GET", mapbox_path)
        response = conn.getresponse()
        data = response.read()
        self.image_view = ImageView(image=data, style=Pack(flex=1, width=800, height=1000,alignment="top"))
        conn.close()
        self.main_box.add(self.image_view)

    def createTable(self):
         # Create a table for the list of icao24 values
        self.table = Table(
            headings=["Icao24"],
            data=[],
            on_select=self.on_table_select,
        )
        self.main_box.add(self.table)

    def getICAO24(self):
        # Get icao24 values from the OpenSky API
        url_icao = "https://opensky-network.org/api/flights/all?begin=1671904563&end=1671908163"
        conn = http.client.HTTPSConnection("opensky-network.org")
        conn.request("GET", url_icao)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        flight_data = json.loads(data)
        return flight_data
    
    def addICAO24Table(self, flight_data):
        self.icao24_values = list(set(flight["icao24"] for flight in flight_data))
        # Add icao24 values to the table
        for icao24 in self.icao24_values:
            self.table.data.append((icao24,))
            
    def addSearch(self):
        # Add a search input and button
        self.search_input = TextInput(style=Pack(width=70))
        search_button = Button('Search', on_press=self.on_search)

        # Create a box for the search bar
        search_box = Box(style=Pack(direction='row'))
        search_box.add(self.search_input)
        search_box.add(search_button)
        self.main_box.add(search_box)
    def createTableAirports(self):
         # Create a table for displaying aircraft details
        self.details_table = Table(
            headings=["Departure Airport", "Arrival Airport"],
            data=[],
            style=Pack(width=300)  # Set the desired width here
        )
        self.main_box.add(self.details_table)


    def startup(self):
        # Initialize the main box
        self.main_box = Box(style=Pack(alignment='center'))
        
        self.getMapBox()


        self.createTable()

    
        flight_data = self.getICAO24()

        self.addICAO24Table(flight_data)


        # Adicione uma nova variável de instância para armazenar o ICAO24 selecionado
        self.selected_icao24 = None

        self.addSearch()

        self.createTableAirports()

        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(1000, 1000))
        self.main_window.content = self.main_box
        self.main_window.show()


def main():
    return MapboxApp('MapboxApp', 'org.example.mapboxapp')

