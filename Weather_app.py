import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit
                             , QPushButton, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather")
        self.setGeometry(100, 100, 600, 600)
        self.setFixedSize(600, 600) 
        self.setWindowIcon(QIcon("Python-Projects\\weather_icon.jpg"))
         
        label = QLabel(self)
        label.setGeometry(0,0,600,600)
        pixmap = QPixmap("Python-Projects\\background_weather.png")
        label.setPixmap(pixmap)
        label.setScaledContents(True)
             
        self.initUI()
    


    def initUI(self):
        main_layout = QVBoxLayout()

        title = QHBoxLayout()
        self.heading = QLabel("<h2 style= 'margin: 6px'>Weather ☀️</h2>")
        title.addWidget(self.heading)

        main_layout.addLayout(title)

        upper_row = QVBoxLayout()

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter City Name")
        self.city_output_button = QPushButton("Get Weather")
        self.city_output_button.setCursor(Qt.PointingHandCursor)
        self.city_output_button.clicked.connect(self.get_weather_data) 
        upper_row.addWidget(self.city_input)
        upper_row.addWidget(self.city_output_button)
        main_layout.addLayout(upper_row)
        

        middle_left = QVBoxLayout()

        self.temperature_label = QLabel("")
        self.feels_like_label = QLabel("")     
        middle_left.addWidget(self.temperature_label)
        middle_left.addWidget(self.feels_like_label)
        main_layout.addLayout(middle_left)


        middle_row = QHBoxLayout()   

        self.emoji_label = QLabel("")
        middle_row.addWidget(self.emoji_label)
        main_layout.addLayout(middle_row)


        bottom_row = QVBoxLayout()
      
        self.main_label = QLabel("")
        self.description_label = QLabel("")     
        bottom_row.addWidget(self.main_label)
        bottom_row.addWidget(self.description_label)
        main_layout.addLayout(bottom_row)



        self.setLayout(main_layout)

        # CSS Editing

        self.heading.setObjectName("heading")
        self.city_input.setObjectName("city_input")
        self.city_output_button.setObjectName("city_output_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.feels_like_label.setObjectName("feels_like")
        self.description_label.setObjectName("description_label")
        self.main_label.setObjectName("main_label")

        self.setStyleSheet("""
            QLabel#heading{
                font-size: 50px;
                font-family: Segoe UI emoji;
            }
            QLineEdit#city_input{
                font-size: 15px;
                font-family: Monocraft Nerd Font;
                background: transparent solid; 
                border: 2px solid #555;         
            }
            QPushButton#city_output_button{
                font-size: 16px;
                font-family: Monocraft Nerd Font; 
                background: transparent;
                border: 2px solid #555;           
            }
            QLabel#temperature_label{
                font-size: 25px;
                font-family: Monocraft Nerd Font;            
            }
            QLabel#emoji_label{
                font-size: 90px;
                font-family: Segoe UI emoji;            
            }
            QLabel#feels_like{
                font-size: 25px;
                font-family: Monocraft Nerd Font;            
            }
            QLabel#description_label{
                font-size: 25px;
                font-family: Monocraft Nerd Font;            
            }
            QLabel#main_label{
                font-size: 25px;
                font-family: Monocraft Nerd Font;            
            }
        """)

    def get_weather_data(self):
        
        api_key = "fd52fb889b7f242042ea2921f9220eb5"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data["cod"] ==  200:
                self.display_weather_data(data)

        except requests.exceptions.HTTPError as http_error:
            self.emoji_label.clear()
            self.description_label.clear()
            match response.status_code:
                case 400:
                    self.display_error("Bad Request:\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized:\nInvalid API Key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not Found:\nCity not Found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease Try again Later")
                case 502:
                    self.display_error("Bad Gateway:\nInvalid responce from the Server")
                case 503:
                    self.display_error("Service Unavailable:\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout:\nNo Responce from the server")
                case _:
                    self.display_error(f"HTTP error occured:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error\nCheck you Internet Conection")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error\nThe requests timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many Redirects\nCheckl the URL")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")

    def display_weather_data(self, data):
        temp_k = data["main"]["temp"]
        temp_c = temp_k - 273.15
        temp_f = (temp_k * 9/5) - 459.67

        feels_like_temp_k = data["main"]["feels_like"]
        feels_like_temp_c = feels_like_temp_k - 273.15

        weather_description = data["weather"][0]["description"]
        weather_id = data["weather"][0]["id"]
        main_weather = data["weather"][0]["main"]

        self.temperature_label.setText(f"{temp_c:.0f}°C")
        self.feels_like_label.setText(f"feels like: {feels_like_temp_c:.0f}°C")
        self.emoji_label.setText(self.get_emoji(weather_id))
        self.main_label.setText(main_weather)
        self.description_label.setText(weather_description.capitalize())

        print(data) 

    def display_error(self, message):
        self.emoji_label.clear()
        self.feels_like_label.clear()
        self.main_label.clear()
        self.description_label.clear()
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)

    @staticmethod
    def get_emoji(weather_id):
        match weather_id:
            case _ if 200 <= weather_id <= 232:
                return "⛈️"
            case _ if 300 <= weather_id <= 321:
                return "🌦️"
            case _ if 500 <= weather_id <= 531:
                return "🌧️"
            case _ if 600 <= weather_id <= 622:
                return "❄️"
            case _ if 701 <= weather_id <= 741:
                return "🌫️"
            case 762:
                return "🌋"    
            case 771:
                return "💨"        
            case 781:
                return "🌀"
            case 800:
                return "☀️"
            case _ if 801 <= weather_id <= 804:
                return "☁️"
            case _:
                return ""

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())