import requests
import json

from Setup_main import Gatekeeper_IP

# Defining functions to send requests to gatekeeper



# Perform an insertion operation into a database table through the gatekeeper, using the provided SQL INSERT query.
# This is done by utilizing an SQL INSERT query.
# Parameters:
# query: SQL INSERT query for the operation.
# Returns: Insertion status indicating success or failure.
def add_data(query):
    try:
        payload = {"query": query}
        response = requests.post(f"http://{Gatekeeper_IP}:8080/direct", json=payload)
        return response
    except Exception as ex:
        print(f"Failed to insert data into database : {ex}")
        raise SystemExit(ex)



# Retrieve data from a table through the gatekeeper by directly querying the master node using an SQL SELECT statement.
# Parameters:
# query: SQL SELECT query for the operation.
# Returns: Output of the executed query.

def read_direct_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/direct", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select direct data from database : {ex}")
        raise SystemExit(ex)



# Retrieve data from a table through the gatekeeper using a custom call that considers the best ping time between the master and slave nodes. 
# This is done by utilizing an SQL SELECT query.
# Parameters:
# query: SQL SELECT query for the operation.
# Returns: Output of the executed query.

def read_custom_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/custom", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select random data from database : {ex}")
        raise SystemExit(ex)
    


# Retrieve data from a table through the gatekeeper by making a random call to slave nodes using an SQL SELECT statement.
# Parameters:
# query: SQL SELECT query for the operation.
# Returns: Output of the executed query.

def read_random_data(query):
    try:
        response = requests.get(f"http://{Gatekeeper_IP}:8080/random", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to select random data from database : {ex}")
        raise SystemExit(ex)



# Drop a database or table through the gatekeeper by executing the specified SQL query.
# Parameters:
# query: SQL DROP DATABASE or DROP TABLE query.
# Returns:
# Confirmation message indicating the successful dropping of the database or table.

def delete(query):
    try:
        response = requests.delete(f"http://{Gatekeeper_IP}:8080/delete", json={"query": query})
        return response
    except Exception as ex:
        print(f"Failed to delete databse : {ex}")
        raise SystemExit(ex)




if __name__ == '__main__':

# Send requests to firstly to gatekeeper ..
    
    insert_query_1 = ("""INSERT INTO film (title, description) VALUES ('Titanic','Romantic and adventure film');""")
    insert_query_2 = ("""INSERT INTO film (title, description, release_year, language_id, original_language_id, rental_duration, rental_rate, length, replacement_cost, rating) 
                      VALUES ('Titanic','Romantic and adventure film','1997','1','1','48 hours','9','3h 30m','0 USD','PG-13');""")
    select_film_query = ("SELECT * FROM film where title = 'Titanic';")
    select_city_query = "select * from city;"
    delete_query = "DROP TABLE film;"


    print("\nAdd Titanic into film table without specifying all necessary columns")
    print(json.loads(add_data(insert_query_1).content))

    print("\nAdd Titanic into film table by specifying all necessary columns")
    print(json.loads(add_data(insert_query_2).content))

    print("\nSearch for film Titanic using direct read")
    print(json.loads(read_direct_data(select_film_query).content))

    print("\nSearch for film Titanic using custom read")
    print(json.loads(read_custom_data(select_film_query).content))

    print("\nSearch for film Titanic using random read")
    print(json.loads(read_random_data(select_film_query).content))

    print("\nSearch for all cities informations")
    print(json.loads(read_direct_data(select_city_query).content))

    print("\nDelete film table")
    print(json.loads(delete(delete_query).content))
    print("\n")