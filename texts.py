"""All the texts YOU write: your analysis under each chart, and your profile in the sidebar.

Edit only this file to change what the app says. Keep the quotation marks.
If a text is empty (""), nothing is shown for that chart.
"""

# --- Profile (shown at the top of the sidebar) -------------------------------
PROFILE = {
    "logo": "assets/efrei_logo.png", 
    "name": "Julie WENG",
    "program": "Engineering cycle, Data Engineering major",
    "year": "ING2",              
    "email": "julie.weng@efrei.net",
    "linkedin": "www.linkedin.com/in/julie-wg",         
    "github": "https://github.com/l1eju",
    "course": "Data Analysis & Visualization",             
    "professor": "Prof. Mano Mathew",
    "professor_contact": "https://www.linkedin.com/in/manomathew/",  
}

# --- Analysis under each chart -----------------------------------------------
ANALYSIS = {
    "sector": (
        "Residential is the biggest sector, ahead of services and industry. "
        "Residential is the only one to show a peak in 2021, the only winter colder than normal, and drops in 2022 when the weather warms up."
    ),
    "weather": (
        "Seven winters out of eight are milder than normal. 2022 is by far the mildest and 2021 the coldest. "
        "Eight years are too few to prove a climate trend."
    ),
    "share": (
        "The temperature-sensitive share follows the weather: lowest in the mild winter of 2022. "
        "But 2018 and 2019 had similar weather and different shares, so something else also changes."
    ),
    "map": (
        "The share goes from about 16 % to 28 %. The Mediterranean coast is low (mild winters), "
        "the mountains are high. A lighter colour means that heating weighs more in winter use."
    ),
    "ranking": (
        "The gaps between EPCI are much bigger than between departments: from about 11 % to 50 %. "
        "The highest ones are small mountain areas."
    ),
    "regions": (
        "All regions have the same shape: high in 2018, a dip in 2022 (when the temperature is milder), then a partial recovery. "
        "The weather is a common factor for the whole country, only the level changes."
    ),
    "scatter": (
        "Electric heating alone does not explain the gaps: the dots form a flat cloud. "
        "The heating rate is only available for 2024."
    ),
    "quality": "",
    "conclusion": "We have seen that temperature has an impact on the energy consumption, but it is not the only factor. The share of temperature-sensitive energy is higher in colder winters, but other factors also play a role.",
}
