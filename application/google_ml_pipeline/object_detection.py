import glob

import config
import cv2
from cv2 import rectangle
from google.cloud import automl_v1beta1
from google.protobuf.json_format import MessageToDict


def get_prediction(self, content, project_id, model_id):
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = "projects/{}/locations/us-central1/models/{}".format(project_id, model_id)
    payload = {"image": {"image_bytes": content}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request


def process_image_cloud_ml(self, content, project_id, model_id, image_name):
    print("Calling Google Cloud ML API")
    try:
        predictions = self.get_prediction(content, project_id, model_id)
        response = MessageToDict(predictions, preserving_proto_field_name=True)
    except Exception as e:
        print("There was an issue communicating with Google ML\n{}".format(e))
        return content
    try:
        # Convert RGB to BGR
        content = cv2.UMat(cv2.imread(image_name, cv2.IMREAD_COLOR))
        for x in response["payload"]:
            # Check for type
            if x["display_name"] == "bleached":
                rect_color = (0, 0, 0)
            if x["display_name"] == "healthy":
                rect_color = (255, 255, 255)
            x1, x2, y1, y2 = 0, 0, 0, 0
            for i, coordinates in enumerate(
                x["image_object_detection"]["bounding_box"]["normalized_vertices"]
            ):
                print("Adding prediction coordinates to image with i={}".format(i))
                try:
                    x = coordinates["x"] * 320
                    y = coordinates["y"] * 280
                except Exception as e:
                    x = 0
                    y = 0
                if i == 0:
                    x1 = int(x)
                    y1 = int(y)
                if i == 1:
                    x2 = int(x)
                    y2 = int(y)
            print("Adding rectangle")
            rectangle(
                img=content, pt1=(x1, y1), pt2=(x2, y2), color=rect_color, thickness=3
            )
        return content
    except Exception as e:
        print("Something went wrong while adding bounded boxes!\n{}".format(e))
        return content


def batch_process(self, event):
    print("Starting batch processing. . .")
    for i, image in enumerate(
        f for f in glob.glob(str(self.record_dataset_to_dir) + "/*.jpg")
    ):
        with open(image, "rb") as image_file:
            content = image_file.read()
        # Pass the image data to an encoding function.
        new_img = self.process_image_cloud_ml(
            content, config.google_api_key, config.google_api_secret, image
        )
        cv2.imwrite(
            str(self.record_dataset_to_dir) + "/processed_{}.jpg".format(i), new_img
        )
