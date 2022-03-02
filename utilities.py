import os
import tweepy as tw
import pandas as pd


def get_tokens(fileName, printTokens=False):
    """
    Get twitter API tokens from a text file.
    """
    with open(fileName, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("[API KEY]"):
                api_key = line.split("=")[1].strip()
            elif line.startswith("[API KEY SECRET]"):
                api_key_secret = line.split("=")[1].strip()
            elif line.startswith("[ACCESS TOKEN]"):
                access_token = line.split("=")[1].strip()
            elif line.startswith("[ACCESS TOKEN SECRET]"):
                access_token_secret = line.split("=")[1].strip()
            elif line.startswith("[BEARER TOKEN]"):
                bearer_token = line.split("=")[1].strip()
    f.close()

    if printTokens:
        print("API Key:", api_key)
        print("API Key Secret:", api_key_secret)
        print("Access Token:", access_token)
        print("Access Token Secret:", access_token_secret)

    return api_key, api_key_secret, access_token, access_token_secret, bearer_token
