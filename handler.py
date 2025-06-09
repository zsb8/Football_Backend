import logging
from src.step1_getcsv import main as get_csv_main
from src.step2_summarize import main as summarize_main
from src.step3_query_kpi_from_csv import main as query_kpi_from_csv_main
import json

import asyncio

def handler(event, context):
    try:
        # From event object get path
        path = event['requestContext']['http']['path']
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
        
        if path == "/get_csv":
            print("Starting navigation to /get_csv")
            get_csv_main()
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CSV file saved."})
            }
        elif path== "/summarize":
            print("Starting navigation to /summarize")
            summarize_main()
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "Summarized"})
            }
        elif path== "/query_kpi_from_csv":
            print("Starting navigation to /query_kpi_from_csv")
            result = query_kpi_from_csv_main(event)
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(result)
            }
        else:
            print("!!!!======Invalid navigation path")
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"message": "Not Found"})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": "Internal Server Error"})
        }