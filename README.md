# test
football
API:

API initial Url: https://api.football-data.org/

API account name: testing.data999@gmail.com

API token information:

Please modify your client to use a HTTP header named "X-Auth-Token" with the underneath personal token as value. Your token: 12abfbaacdab48bc8948ed6061925e1f

# How to run these programs
## Get data from API then save it as CSV
Run ```python step1_getcsv.py```  
The script retrieves data from football-data.org and saves the raw data as a CSV file named ```premier_league_stats.csv``` in the root directory.
![image](https://github.com/user-attachments/assets/22c3e7bb-c9a5-421b-8ee4-9f1dac175134)

## CSV file
"premier_league_stats.csv", on root folder. 

## Clean the data and save the summaries as graphs
Run ```python step2_summarize.py```  
The script read data from CSV file, validate years, Clean the data by handling missing values using median imputation, then sort dataframe and save data as graphs in the fold ```/premier_league_plots/```.
![image](https://github.com/user-attachments/assets/3f6f1878-ad7c-4b84-be00-c39dec0eeae7)
As a result of the data summary, six graphs have been generated with the following names:
* "premier_league_plots\won_by_team_and_year.png",
* "premier_league_plots\draw_by_team_and_year.png",
* "premier_league_plots\lost_by_team_and_year.png",
* "premier_league_plots\goalsFor_by_team_and_year.png",
* "premier_league_plots\goalsAgainst_by_team_and_year.png".

## Graphs
![won_by_team_and_year](https://github.com/user-attachments/assets/7c9f3475-89d9-43fe-9605-f1f35485b011)
![draw_by_team_and_year](https://github.com/user-attachments/assets/b739f62d-0df2-4d33-b4e8-9135160589bc)
![lost_by_team_and_year](https://github.com/user-attachments/assets/a32576d0-5bea-4f53-8656-101d7cb374df)
![goalsFor_by_team_and_year](https://github.com/user-attachments/assets/e239c49b-493e-483e-827a-d9feeb52d6b8)
![goalsAgainst_by_team_and_year](https://github.com/user-attachments/assets/f29e5c24-c006-47a3-9b0f-5f6fa81949ca)

## Test 
I use pytest.    
There are two test files named ```tests\test_step1_getcsv.py``` and ```tests\test_step2_summarize.py```.    
You can run ``` python -m pytest tests\test_step1_getcsv.py```.     
![image](https://github.com/user-attachments/assets/ea858a4e-2b38-4ebe-aa26-0c02bd3c99f8)    
You can run ```python -m pytest tests\test_step2_summarize.py```.    
![image](https://github.com/user-attachments/assets/e3c71737-69df-4598-af8f-87ed3f92d859)     

## Folder structure:  
![image](https://github.com/user-attachments/assets/41633cfd-0362-4448-8e70-756d6a82d899)

## Auto Deploy as MicroServices on AWS
We can deploy these programs as microservices on AWS. I created 3 APIs on AWS using Lambda and docker ECR.   
* If you want to refresh data from football-data.org, we can call the API namned ```https://y4zeduzvn3.execute-api.us-east-1.amazonaws.com/get_csv``` with Postman. This API can be invoked to retrieve and refresh the incremental data.   
* If you want to query data from the CSV file (stored on AWS S3), you can use the API ```https://y4zeduzvn3.execute-api.us-east-1.amazonaws.com/query_kpi_from_csv```with Postman. This API can be invoked to return JSON data for your custom query.
      
![image](https://github.com/user-attachments/assets/c396de3e-d1a7-4465-a20d-c35434ea788b)   
       
These measures make it easier for BI teams to use this processed data and perform personalized queries.    

## Demo
![image](https://github.com/user-attachments/assets/9b0ad46a-9799-4083-b166-ac72c5f58e75)

## Program limitation
This token may be a token for the free package, so only data for the past two years can be obtained, and the requested data for 2020-2022 cannot be obtained.   
If we have a token of higher-level packagem, we will access to the requested data for 2020 to 2023.
