from datetime import date, datetime
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Travel:
    def __init__(
        self, origin: str, destination: str, departure_date: date, return_date: date
    ):
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.return_date = return_date

    def __str__(self) -> str:
        return (
            f"{self.origin} | {self.destination}"
            + f" | {self.departure_date.isoformat()}"
            + f" | {self.return_date.isoformat()}"
        )


class Flight:
    def __init__(
        self,
        number: str,
        origin: str,
        destination: str,
        departure_time: datetime,
        arrival_time: datetime,
        price: int,
    ):
        self.number = number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.price = price

    def __str__(self) -> str:
        return (
            f"{self.number} | {self.origin} | {self.destination}"
            + f" | {self.departure_time.time().isoformat(timespec='minutes')}"
            + f" | {self.departure_time.time().isoformat(timespec='minutes')}"
            + f" | {self.price}€"
        )


class TransaviaConnector:
    """Handles contact with the Transavia website through Selenium"""

    URL_HOME = "https://www.transavia.com/fr-FR/accueil/"
    URL_SEARCH = "https://www.transavia.com/fr-FR/reservez-un-vol/vols/rechercher/"

    def __init__(self, headless: bool = True):
        """TransaviaConnector initializer.

        :param headless: Don't display the browser window.
        """
        self.headless = headless

        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        # self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver = webdriver.Firefox()

    @staticmethod
    def str_to_datetime(value: str) -> datetime:
        """Get a datetime object from the transavia string format.

        :param value: str
        :return: datetime
        """
        return datetime.strptime(value, "%d/%m/%Y %H:%M")

    @staticmethod
    def deserialize_flight_button(button: WebElement) -> Flight:
        """Deserialize a flight button.

        :param button: Selenium WebElement object
        :return: Flight object
        """
        value = button.get_attribute("value")
        parts = [v for v in value.split("|")[1].split("~") if v and v not in [" "]]
        return Flight(
            number="".join(parts[0:2]),
            origin=parts[2],
            destination=parts[4],
            departure_time=TransaviaConnector.str_to_datetime(parts[3]),
            arrival_time=TransaviaConnector.str_to_datetime(parts[5]),
            price=button.find_element_by_css_selector("div.price").text,
        )

    def get_flights(self, base: WebElement) -> List[Flight]:
        """Get the flight list contained in the base web element.

        :param base: Selenium WebElement object
        :return: Flight object list
        """
        flights = []
        outbound_flights_selectors = base.find_element_by_css_selector(
            ".nav-days .animation-container form"
        )
        for (
            flight_date_selector
        ) in outbound_flights_selectors.find_elements_by_css_selector(
            ".day-with-availability"
        ):
            flight_date_selector.find_element_by_css_selector(".button").click()
            for flight_button in base.find_elements_by_css_selector(
                "button.flight-result-button"
            ):
                flights.append(
                    TransaviaConnector.deserialize_flight_button(flight_button)
                )
        return flights

    def accept_cookies(self):
        """Accept cookies to remove the cookie banner"""
        try:
            self.driver.find_element_by_css_selector(
                "button.info-banner-button-all.button-call-to-action"
            ).click()
        except NoSuchElementException:
            pass  # No cookie banner

    def fill_search_form(self, travel: Travel) -> None:
        """Fill the transavia flight search form, and submits it. Works on both URL_HOME and URL_SEARCH.

        :param travel: Travel object
        """
        origin_input = self.driver.find_element_by_css_selector(
            "input#routeSelection_DepartureStation-input"
        )
        destination_input = self.driver.find_element_by_css_selector(
            "input#routeSelection_ArrivalStation-input"
        )
        departure_input = self.driver.find_element_by_css_selector(
            "input#dateSelection_OutboundDate-datepicker"
        )
        return_input = self.driver.find_element_by_css_selector(
            "input#dateSelection_IsReturnFlight-datepicker"
        )

        origin_input.send_keys(travel.origin)
        origin_input.send_keys(Keys.RETURN)
        destination_input.send_keys(travel.destination)
        destination_input.send_keys(Keys.RETURN)
        departure_input.clear()
        departure_input.send_keys(travel.departure_date.strftime("%d-%m-%Y"))
        origin_input.click()
        return_input.clear()
        return_input.send_keys(travel.return_date.strftime("%d-%m-%Y"))
        origin_input.click()
        destination_input.send_keys(Keys.RETURN)

    def search_travel(self, travel: Travel) -> List[Flight]:
        """Find travels matching the provided travel. Ignores time, only the date is used.

        :param travel: Travel object.
        :return: List of matching travels.
        """
        self.driver.get(TransaviaConnector.URL_HOME)

        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(
                (By.ID, "routeSelection_DepartureStation-input")
            )
        )

        self.accept_cookies()
        self.fill_search_form(travel)

        # Solve Captchas

        outbound_box = self.driver.find_element_by_css_selector(
            "section.flight.outbound"
        )
        flights = self.get_flights(outbound_box)

        return_box = self.driver.find_element_by_css_selector("section.flight.inbound")
        flights += self.get_flights(return_box)

        return flights


if __name__ == "__main__":
    t = Travel("Paris", "Amsterdam", date(2021, 10, 21), date(2021, 11, 22))
    connector = TransaviaConnector(False)
    flights = connector.search_travel(t)
    [print(f) for f in flights]
