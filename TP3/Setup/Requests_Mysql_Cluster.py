import requests
import json

from Setup_main import Gatekeeper_IP

# Defining functions to send requests to gatekeeper


"""
Insert data into a  database table through the gatekeeper
:param query: SQL INSERT query
:return: insertion status (success or failure)
"""
def insert_data(query):
    try:
        payload = {"query": query}
        response = requests.post(f"http://{Gatekeeper_IP}:8080/direct", json=payload)
        return response
    except Exception as ex:
        print(f"Failed to insert data into database : {ex}")
        raise SystemExit(ex)


"""
Select data from table through the gatekeeper using direct call to master node
:param query: SQL select query
:return: Query output
"""
def select_direct_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/direct", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select direct data from database : {ex}")
        raise SystemExit(ex)


"""
Select data from table through the gatekeeper using random call to silver nodes
:param query: SQL select query
:return: Query output
"""
def select_random_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/random", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select random data from database : {ex}")
        raise SystemExit(ex)


"""
Select data from table through the gatekeeper using custom call with best ping time between master and slaves
:param query: SQL select query
:return: Query output
"""
def select_custom_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/custom", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select random data from database : {ex}")
        raise SystemExit(ex)


"""
Drop databse/table through the gatekeeper
:param query: SQL select query
:return: databse/table dropped
"""
def delete(query):
    try:
        response = requests.delete(f"http://{Gatekeeper_IP}:8080/delete", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to delete databse : {ex}")
        raise SystemExit(ex)




if __name__ == '__main__':

# Send requests to gatekeeper
    
    insert_query_1 = ("""INSERT INTO film (title, description) VALUES ('Titanic','Romantic and adventure film');""")
    insert_query_2 = ("""INSERT INTO film (title, description, release_year, language_id, original_language_id, rental_duration, rental_rate, length, replacement_cost, rating) 
                      VALUES ('Titanic','Romantic and adventure film','1997','1','1','48 hours','9','3h 30m','0 USD','PG-13');""")
    select_film_query = ("SELECT * FROM film where title = 'Titanic';")
    select_city_query = "select * from city;"
    delete_query = "DROP TABLE film;"


    print("\nAdd Titanic into film table without specifying all necessary columns")
    print(json.loads(insert_data(insert_query_1).content))

    print("\nAdd Titanic into film table by specifying all necessary columns")
    print(json.loads(insert_data(insert_query_2).content))

    print("\nSearch for film Titanic using direct read")
    print(json.loads(select_direct_data(select_film_query).content))

    print("\nSearch for film Titanic using custom read")
    print(json.loads(select_custom_data(select_film_query).content))

    print("\nSearch for film Titanic using random read")
    print(json.loads(select_random_data(select_film_query).content))

    print("\nSearch for all cities informations")
    print(json.loads(select_direct_data(select_city_query).content))

    print("\nDelete film table")
    print(json.loads(delete(delete_query).content))
    print("\n")