# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

import boto3
import os
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def log_event(level, message, **kwargs):
    """Log structured JSON events"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    logger.log(getattr(logging, level.upper()), json.dumps(log_entry))


def handler(event, context):
    request_id = context.request_id
    table = os.environ.get("TABLE_NAME")
    
    log_event("info", "Request received", 
              request_id=request_id, 
              table_name=table,
              event_type="api_request")
    
    if event["body"]:
        item = json.loads(event["body"])
        log_event("info", "Processing payload", 
                  request_id=request_id,
                  payload_keys=list(item.keys()))
        
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        
        log_event("info", "Data inserted successfully", 
                  request_id=request_id,
                  item_id=id)
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        log_event("info", "No payload provided, using default data", 
                  request_id=request_id)
        
        default_id = str(uuid.uuid4())
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": default_id},
            },
        )
        
        log_event("info", "Default data inserted successfully", 
                  request_id=request_id,
                  item_id=default_id)
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
