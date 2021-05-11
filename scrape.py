from sgselenium.sgselenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

option = webdriver.ChromeOptions()
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_argument("window-size=1280,800")
option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
)
option.add_argument("--no-sandbox")
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--headless")

start_url = "https://www.ynhh.org/find-a-location.aspx?page=1&keyword=&sortBy=&distance=0&cz=&locs=0&within=Yale+New+Haven+Hospital&avail=0"

with webdriver.Chrome(options=option) as driver:
    driver.get(start_url)
    html = driver.page_source
    soup = bs(html, "html.parser")

    location_list = (
        html.split("markers = ")[1].split("</script")[0].replace("[", "").split("], ")
    )

    for location in location_list:
        location_deets = location.split(",")
        locator_domain = "https://www.ynhh.org"
        location_name = location_deets[0].replace("'", "")
        page_url = "https://www.ynhh.org" + location_deets[-3].replace("'", "")
        latitude = location_deets[-2]
        longitude = str(location_deets[-1]).replace("]];", "")
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        locator_domains.append(locator_domain)
        location_names.append(location_name)
        page_urls.append(page_url)
        latitudes.append(latitude)
        longitudes.append(longitude)
        country_codes.append(country_code)
        store_numbers.append(store_number)
        location_types.append(location_type)

    total_pages = int(soup.find("span", attrs={"id": "center_0_lblPages"}).text.strip())

    for x in range(total_pages):
        grids = soup.find_all("div", attrs={"class": "module search-details"})
        for grid in grids:
            address_parts = str(grid.find("address")).split("\n")[1].split("<br/>")
            if len(address_parts) == 3:
                address = address_parts[0]
                city = address_parts[1].split(",")[0]
                state = address_parts[-2].split(", ")[1].split(" ")[0]
                try:
                    zipp = address_parts[-2].split(", ")[1].split(" ")[1]
                except Exception:
                    zipp = address_parts[-2].split("CT")[1].strip()

            else:
                address = address_parts[0] + " " + address_parts[1]
                city = address_parts[-2].split(",")[0]
                state = address_parts[-2].split(", ")[1].split(" ")[0]
                zipp = address_parts[-2].split(", ")[1].split(" ")[1]

            phone_section = grid.find_all("div", attrs={"class": "col-sm-4"})[-1]
            phone = "<MISSING>"
            if "Phone" in str(phone_section):
                phone = phone_section.find("a")["href"].replace("tel:", "")
                phone = phone[:10]

            hours_section = grid.find_all("div", attrs={"class": "col-sm-4"})[2]

            if hours_section.text.strip() == "Hours vary.":
                hours = "<MISSING>"

            elif hours_section.text.strip() == "":
                hours = "<MISSING>"

            elif (
                "by appointment"
                == hours_section.text.strip().split(" ")[0].lower()
                + " "
                + hours_section.text.strip().split(" ")[1].lower()
            ):
                hours = "<MISSING>"

            elif 'colspan="2"' not in str(hours_section):
                try:
                    hours_days = grid.find_all("tr")
                    if len(hours_days) > 0:
                        hours = ""
                        for row in hours_days:
                            day = row.find_all("td")[0].text.strip()
                            hours_part = row.find_all("td")[1].text.strip()
                            hours = hours + day + " " + hours_part + ", "
                        hours = hours[:-2]
                    else:
                        if (
                            "always open" in str(hours_section).lower()
                            or "24/7" in str(hours_section).lower()
                            or " anytime" in str(hours_section).lower()
                        ):
                            hours = "24/7"

                        elif (
                            "call for information" in str(hours_section).lower()
                            or "hours vary" in str(hours_section).lower()
                        ):
                            hours = "<MISSING>"

                        elif address == "175 Sherman Avenue Second floor":
                            days = hours_section.text.strip().split("\n")
                            hours = ""
                            for day in days:
                                hours = hours + day + " "

                        elif address == "184 Liberty Street":
                            hours = "Mon-Sun " + hours_section.text.strip()

                        else:
                            hours = (
                                str(hours_section)
                                .replace("\n", "")
                                .split("Hours: ")[1]
                                .split("<")[0]
                                .strip()
                            )
                except Exception:
                    hours = "<MISSING>"

            else:
                last_text = hours_section.find_all("td", attrs={"colspan": "2"})[
                    -1
                ].text.strip()
                last_hours = (
                    hours_section.text.strip().split(last_text)[1].split("X-ray")[0]
                )

                hours = ""
                for line in last_hours.split("\n"):
                    if "schedule" not in line.lower():
                        hours = hours + line + " "
                hours = (
                    hours.strip()
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .split("Note:")[0]
                )
                if "or" in hours:
                    hours = hours.split("pm")[0] + "pm"

            if hours[0] == "M":
                hours = "M " + hours.split("M")[1].strip()

            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            phones.append(phone)
            hours_of_operations.append(hours)
        new_url = (
            "https://www.ynhh.org/find-a-location.aspx?page="
            + str(x + 2)
            + "&keyword=&sortBy=&distance=0&cz=&locs=0&within=Yale+New+Haven+Hospital&avail=0"
        )
        driver.get(new_url)
        soup = bs(driver.page_source, "html.parser")

df = pd.DataFrame(
    {
        "locator_domain": locator_domains[: len(zips)],
        "page_url": page_urls[: len(zips)],
        "location_name": location_names[: len(zips)],
        "street_address": street_addresses[: len(zips)],
        "city": citys[: len(zips)],
        "state": states[: len(zips)],
        "zip": zips[: len(zips)],
        "store_number": store_numbers[: len(zips)],
        "phone": phones[: len(zips)],
        "latitude": latitudes[: len(zips)],
        "longitude": longitudes[: len(zips)],
        "hours_of_operation": hours_of_operations[: len(zips)],
        "country_code": country_codes[: len(zips)],
        "location_type": location_types[: len(zips)],
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
