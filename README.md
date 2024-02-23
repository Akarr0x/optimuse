{\rtf1\ansi\ansicpg1252\cocoartf2757
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red232\green232\blue231;\red105\green167\blue255;
\red251\green0\blue7;\red232\green232\blue231;}
{\*\expandedcolortbl;;\cssrgb\c0\c1\c1;\cssrgb\c92651\c92651\c92535;\cssrgb\c48093\c72057\c100000;
\cssrgb\c100000\c12195\c0;\cssrgb\c92753\c92753\c92521;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Optimuse Energy Demand API\
\
## Introduction\
\
Provides an api GET for retrieving the energy demand for a determined asset.\
 \
The requirements can be found in the \'91requirements.txt\'92\
\
## Installation\
\
Clone the repository to your local machine:\
\
\pard\pardeftab720\sa333\partightenfactor0
\cf2 \expnd0\expndtw0\kerning0
git clone \cf2 https://github.com/Akarr0x/optimuse.git\cf2 \
cd optimuse\
Install the required Python packages:\
pip install -r requirements.txt\
\
## Running the Application\
To run the application, go to the controller directory and execute:\
flask run \
The application will run on `http://127.0.0.1:5000/`\
\
\
## API Usage\
\
### Get Energy Demand\
\
Retrieve the energy demand for a specific asset by name\
\
**URL** : `/energy_demand`\
\
**Method** : `GET`\
\
**Query Parameters** :\
\
\cf5 - \cf2 `name`: The name of the asset.\
\
**Example Request**:\
\pard\pardeftab720\sa333\partightenfactor0

\fs26\fsmilli13333 \cf2 GET /energy_demand?name=High%20Rise\
\pard\pardeftab720\sa333\partightenfactor0

\fs24 \cf2 \
**Success Response**:\
```json\
\{\
    "name": "High Rise",\
    "energy_types": \{\
        "heat": 853452,\
        "water": 724213,\
        "light": 554321,\
        "cool": 652134\
    \},\
    "total_energy_demand": 2784120,\
    "energy_output_reduction": 4.14\
\}\
\
\pard\pardeftab720\sa333\partightenfactor0
\cf2 **Error Response**:\
\pard\pardeftab720\sa333\partightenfactor0
\cf2 \{\
    "error": "Invalid asset name"\
\}\
\
\
\
 }