# NITH Result Scraper

A prototype scraper to scrape the results from the NITH website.

![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)
[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)

## Getting started

To get the script running locally:

- Clone the repository.
- Create a `.env` file in the root directory and add the following environment variables:

  ```{.sourceCode .bash}
  export MONGO_URL="mongodb+srv://horizenight:Ramrambro@nithresultdb.jhqelre.mongodb.net/?retryWrites=true&w=majority"


  export MONGO_DB="NithResultdb"
  ```
- `cd scraper` to go to the scraper directory
- `pip install -r requirements.txt` to install all required dependencies
- `python main.py` to start the script
- `python main.py --help` to see the available options
