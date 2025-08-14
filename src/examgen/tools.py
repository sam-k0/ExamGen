import dspy
import typing

"""
Loads secrets (base_url, key) from files
"""
def load_secrets()-> typing.Tuple[str,str]:
    with open("key.txt") as f:
        key = f.readline()
        print(f"Using API key {key}")
    
    with open("baseurl.txt") as f:
        url = f.readline()
        print(f"Using Base URL {url}")
    
    return key,url



def search_wikipedia(query: str) -> list[str]:
    results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=3)
    return [x['text'] for x in results] # type: ignore