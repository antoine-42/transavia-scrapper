from datetime import date, datetime
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Travel:
    def __init__(self, origin: str, destination: str, departure_date: date, return_date: date):
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.return_date = return_date


class Flight:
    def __init__(self, origin: str, destination: str, departure_time: datetime, arrival_time: datetime):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class TransaviaConnector:
    """Handles contact with the Transavia website through Selenium"""
    URL_SEARCH = "https://www.transavia.com/fr-FR/reservez-un-vol/vols/rechercher/"

    def __init__(self, headless: bool = True):
        self.headless = headless

        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def search_travel(self, travel: Travel) -> List[Flight]:
        """Find travels matching the provided travel. Ignores time, only the date is used.

        :param travel: Travel object.
        :return: List of matching travels.
        """
        self.driver.get(TransaviaConnector.URL_SEARCH)

        origin_input = self.driver.find_element_by_css_selector("input#routeSelection_DepartureStation-input")
        destination_input = self.driver.find_element_by_css_selector("input#routeSelection_ArrivalStation-input")
        departure_input = self.driver.find_element_by_css_selector("input#dateSelection_OutboundDate-datepicker")
        return_input = self.driver.find_element_by_css_selector("input#dateSelection_IsReturnFlight-datepicker")

        origin_input.send_keys(travel.origin)
        destination_input.send_keys(travel.destination)
        departure_input.send_keys(travel.departure_date.strftime("%d-%m-%Y"))
        return_input.send_keys(travel.return_date.strftime("%d-%m-%Y"))
        destination_input.send_keys(Keys.RETURN)

        outbound_box = self.driver.find_element_by_css_selector("section.flight.outbound")
        outbound_flights_selectors = outbound_box.find_element_by_css_selector(".nav-days .animation-container form")
        for flight_date_selector in outbound_flights_selectors.find_elements_by_css_selector(".day-with-availability"):
            flight_date_selector.find_element_by_css_selector(".button").click()
            for flight_button in outbound_box.find_elements_by_css_selector("button.flight-result-button"):
                flight_data = flight_button.get_attribute("value")
                print(flight_data)


if __name__ == "__main__":
    t = Travel("Paris (Orly 3), France", "Amsterdam (Schiphol), Pays-Bas", date(2021, 10, 22), date(2021, 10, 22))
    connector = TransaviaConnector(False)
    connector.search_travel(t)
