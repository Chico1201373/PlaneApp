import toga
from toga.style import Pack
from toga import ImageView, Table, Button
import http.client
import json


class MapboxApp(toga.App):

    def on_table_select(self, widget):
        self.selected_icao24 = self.table.selection
        print(self.selected_icao24.icao24)

    def on_button_press(self, widget):
        # Este método será chamado quando o botão for pressionado
        if self.selected_icao24.icao24 is not None:
            print(f"Button pressed! Selected ICAO24: {self.selected_icao24.icao24}")
        else:
            print("Button pressed, but no ICAO24 selected.")



    def startup(self):
        # Initialize the main box
        main_box = toga.Box()

        # Mapbox Access Token (replace with your own token)
        mapbox_access_token = 'pk.eyJ1IjoiY2hpY28wNzA2IiwiYSI6ImNscWlsNnkwajFvNGEyaW82MHBrbDRqaWIifQ.cUGoXE2vwPG-0qp34xhlyw'

        # Mapbox Static Image API URL for a world map
        mapbox_path = f'/styles/v1/mapbox/streets-v11/static/0,0,1,0,0/1000x1000?access_token={mapbox_access_token}'

        # Make request to Mapbox API for the map image
        conn = http.client.HTTPSConnection("api.mapbox.com")
        conn.request("GET", mapbox_path)
        response = conn.getresponse()
        data = response.read()
        image_view = ImageView(image=data, style=Pack(flex=1, width=1000, height=1000))
        conn.close()

        # Create a table for the list of icao24 values
        self.table = Table(
            headings=["Icao24"],
            data=[],
            on_select=self.on_table_select
        )

        # Get icao24 values from the OpenSky API
        url_icao = "https://opensky-network.org/api/flights/all?begin=1671904563&end=1671908163"
        conn = http.client.HTTPSConnection("opensky-network.org")
        conn.request("GET", url_icao)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        flight_data = json.loads(data)
        icao24_values = list(set(flight["icao24"] for flight in flight_data))

        # Add icao24 values to the table
        for icao24 in icao24_values:
            self.table.data.append((icao24,))

        # Create a button to perform some Python code
        button = Button('Click me!', on_press=self.on_button_press)

        # Adicione uma nova variável de instância para armazenar o ICAO24 selecionado
        self.selected_icao24 = None

        # Add widgets to the main box
        main_box.add(image_view)
        main_box.add(self.table)
        main_box.add(button)

        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(800, 600))
        self.main_window.content = main_box
        self.main_window.show()
def main():
    return MapboxApp('MapboxApp', 'org.example.mapboxapp')
