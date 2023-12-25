from flask import Flask,request,jsonify
import threading
import json
import time
import requests

app=Flask(__name__)
lock=threading.Lock()
request_queue=[]
path = "/home/ubuntu/flaskapp/"
results_ml=[]

def send_request_to_container(container_id,container_info,incoming_request_data):
    print(f"\n\nSending request to {container_id} with data : {incoming_request_data}...")
    container_ip=container_info["ip"]
    container_port=container_info["port"]

    try:
        #creation of the url
        url="http://{}:{}/{}".format(container_ip, container_port,'run_model')
        #post to send the request to the container 
        response=requests.post(url,data=incoming_request_data)
    except Exception as e:
        print('Exception returned is',e)
    
    if response.status_code == 200:
        data = response.json()
        input_text = data['input_text']
        probabilities = data['probabilities']
        # add the result of the request in the list of results
        results_ml.append(data)
    else:
        print("La requête a échoué. Code d'état du serveur :", response.status_code)

    print(f"Received response from {container_id}\n\n") 
    return data


def update_container_status(container_id,status):
    with lock:
        with open(path+"test.json","r") as f:
            data=json.load(f)
        data[container_id]["status"]=status
        with open (path+"test.json","w") as f:
            json.dump(data,f)

def process_request(incoming_request_data, list_of_return):
    with lock:
        with open(path+"test.json","r") as f:
            data=json.load(f)
    free_container=None
    for container_id, container_info in data.items():
        if container_info["status"]=="free":
            free_container=container_id
            break
    if free_container:
        update_container_status(free_container,"busy")
        sd = send_request_to_container(
            free_container,data[free_container],incoming_request_data
        )
        list_of_return.append(sd)
        # time.sleep(2)
        update_container_status(free_container,"free")
    else:
        #### Les requetes sont dans la queue QUE FAIRE POUR LES TRAITER
        request_queue.append(incoming_request_data)    
    return list_of_return

def process_request_queue(waiting_request, list_of_return):
    while waiting_request:
        incoming_request_queue = waiting_request.pop(0)  # Get the oldest request (FIFO)
        process_request(incoming_request_queue, list_of_return) 

@app.route("/new_request",methods=["POST"])
def new_request():
    list_of_return = []
    incoming_request_data=""
    # Si les requetes sont dans la queue, mettre une gestion FIFO des ancieenes & nouvelles requetes
    th = threading.Thread(target=process_request,args=(incoming_request_data, list_of_return))
    th.start()
    # In order to wait the completion of the thread
    th.join()

    if request_queue:
        # threading.Thread(target=process_request,args=(request_queue,)).start()
        process_request_queue(request_queue, list_of_return)
    
    return list_of_return


    return jsonify({"message":"Request received and processing started."})

# add a new route to get the results of the requests 
@app.route("/get_results",methods=["GET"])
def get_results():
    return(results_ml)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
   