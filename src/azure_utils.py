import os, requests, json
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
#from keras.preprocessing import image

# retrieve environment variables
keyVaultName = os.environ["KEY_VAULT_NAME"]
KVUri = f"https://{keyVaultName}.vault.azure.net"
prediction_key = os.environ["VISION_PREDICTION_KEY"]
prediction_endpoint = os.environ["VISION_PREDICTION_ENDPOINT"]
prediction_endpoint_url = os.environ["VISION_PREDICTION_ENDPOINT_URL"]
identity_client_id = os.environ["IDENTITY_CLIENT_ID"]

def get_kv_secret(secret_name):
    #With managed identity (=> we don't have the permission to assign roles)
    #credential = DefaultAzureCredential(managed_identity_client_id=identity_client_id)
    #With default Azure account (logged with az login)
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KVUri, credential=credential)
    return client.get_secret(secret_name)

def work_on_predictions(predictions):
    for pred in predictions:
        pred["probability"] = round(pred["probability"]*100, 2)
        if pred["probability"] > 51:
            pred["selected"] = "checked"

def work_on_predictions_with_sdk(predictions):
    result = []
    for pred in predictions:
        if pred.probability > 0.51:
            result.append({"probability": round(pred.probability*100, 2), "tagName": pred.tag_name, "selected": "chacked"})
        else:
            result.append({"probability": round(pred.probability*100, 2), "tagName": pred.tag_name})
    return result

def make_a_prediction(image_file):
    url = prediction_endpoint
    #secret_key = get_kv_secret("cv-ludo-key")
    headers = {
        'Content-Type': 'application/octet-stream',
        'Prediction-Key': prediction_key
    }
    with open(image_file, "rb") as file:
        img_data = file.read()

    result = requests.request("POST", url, headers=headers, data=img_data)
    predictions = result.json()["predictions"]
    work_on_predictions(predictions)
    return predictions

def make_a_prediction_url(image_url):
    url = prediction_endpoint_url
    #secret_key = get_kv_secret("cv-ludo-key")
    headers = {
        'Content-Type': 'application/json',
        'Prediction-Key': prediction_key
    }
    body = json.dumps({"url": image_url})
    result = requests.request("POST", url, headers=headers, data=body)
    predictions = result.json()["predictions"]
    return predictions

def make_a_prediction_with_sdk(image_file):
    ENDPOINT = os.environ["VISION_ENDPOINT"]
    project_id = os.environ["VISION_PROJECT_ID"]
    #secret_key = get_kv_secret("cv-ludo-key")

    credentials = ApiKeyCredentials(in_headers={"Training-key": prediction_key})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

    project = trainer.get_project(project_id)

    with open(image_file, "rb") as image_contents:
        results = predictor.classify_image(
            project.id, "Iteration1", image_contents.read())
    predictions = work_on_predictions_with_sdk(results.predictions)
    return predictions

# def dirty_or_clean(model, image_file):
#     img_load = image.load_img(image_file, target_size=(256, 256))
#     img_array = image.img_to_array(img_load)
#     img_array /= 255. # remettre les valeurs de pixel entre 0 et 1
#     img_array = img_array.reshape((1, 256, 256, 3)) # reshape correctement pour que le modèle accepte
#     prediction = model.predict(img_array)
#     final_pred = False #False <=> clean
#     try:
#         final_pred = False if prediction[0][0] < 0.5 else True
#         print(prediction[0][0])
#     except IndexError:
#         print("clean/dirty model prediction didn't work")
#     return final_pred
