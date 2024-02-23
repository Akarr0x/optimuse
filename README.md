# Optimuse Energy Demand API

## Introduction

Provides an api GET for retrieving the energy demand for a determined asset.
 
The requirements can be found in the requirements.txt

## Installation

Clone the repository to your local machine:
```
git clone https://github.com/Akarr0x/optimuse.git

cd optimuse
```
Install the required Python packages:
```
pip install -r requirements.txt
```
## Running the Application
To run the application, go to the controller directory and execute:
```
flask run 
```
The application will run on `http://127.0.0.1:5000/`


## API Usage

### Get Energy Demand

Retrieve the energy demand for a specific asset by name

**URL** : `/energy_demand`

**Method** : `GET`

**Query Parameters** :

`name`: The name of the asset

**Example Request**:
```
http://127.0.0.1:5000/energy_demand?name=High%20Rise
```
**Success Response**:
```json
{
    "name": "High Rise",
    "energy_types": {
        "heat": 853452,
        "water": 724213,
        "light": 554321,
        "cool": 652134
    },
    "total_energy_demand": 2784120,
    "energy_output_reduction": 4.14
}
```
**Error Response**:
```json
{
    "error": "Invalid asset name"
}
