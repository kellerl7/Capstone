# Understanding the Impact of Public Facilities on New York City's Neighborhoods
This is a capstone project for the University of Michigan Masters of Applied Data Science by Lucas Keller, Nicolas Calo, and Tomas Castillo.

## Getting Started
Clone this repo to get started:
```
git clone https://github.com/kellerl7/Capstone.git nyc-public-facilities
cd nyc-public-facilities
```
### Prerequisites
- 🚀 Python 3.10 support
- 👾 Model development through the use of PyCaret
- 📦 Fast dependency management with uv
- 📊 Interactive visualization through Dash and Plotly

> **Project Manager**
> 
> This project utilizes the python library [uv](https://docs.astral.sh/uv/)
> It is not necessary, but is recommended

### Using UV
If you choose to use uv, the project can be run by issuing the following command:

```
uv run app.py
```

# Project Description
#TODO The city of New York City is the largest city in the USA, and has many different resources to service residents, workers, and travelers. As such, there are many facilities to support the life-like nature of the city. This project aims to provide a glimpse into the different facilities around the city, and visualize how other factors impact the value of a given neighborhood.

#TODO Static image of visualization
## App Demo
-- Link to live demo --

## Project Structure
```
nyc-public-facilities/
├── data/
│   ├── model-inputs
│   ├── processed
│   └── raw
├── model
├── notebooks
├── src/
│   ├── process
│   └── viz
├── app.py
├── config.py
├── figure_utils.py
└── pyproject.toml
```

- The file `app.py` at the root directory pulls together the data and files under `src` to run a local server of Dash.
- Data from this project focuses on the following:
    - Public facilities
    - Borough and code geospatial data
    - Market value
    - Crime data
    - Miscellaneous data
- A majority of the data was pulled from [New York City Public Data](https://opendata.cityofnewyork.us/).

#TODO: Diagram of data flow?
