from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import openai
import streamlit as st
import requests

def generate_synthetic_image(prompt, api_key):
  open.api_key = api_key
  try:
    st.info("Generating synthetic image...")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256"
    )
    image_url = response['data'][0]['url']
    synthetic_image = Image.open(requests.get(image_url, stream=True).raw)
    return synthetic_image
  except Exception as e:
    st.error(f"Error generating synthetic image: {e}")
    return None

## Image rpocessing - yhere is where Opencv comes to functionality and segmentates the image features, and isolates the ones we want to modify.



def segment_asset(image):
  image_array = np.array(image)
  gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray, 100, 200)
  contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  return contours
  mask = np.zeros_like(gray)
  cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)
  masked_image = cv2.bitwise_and(image_array, image_array, mask=mask)
  return masked_image

## We are defining pour second function to have the overlay transformation effect jst for our asset, not for the whole image

def overlay_defects(background_image, synthetic_image, mak, alpha=0.7):

  synthethic_image = synthethic_image.resize(background_image.size, Image.Resampling.LANCZOS)

  background_array = np.array(background_image)
  synthetic_array = np.array(synthetic_image)
  overlay = cv2.addWeighted(background_array, 1 - alpha, synthetic_array, alpha, 0)

  blend_np = background_array.copy()
  blend_np[mask == 255] = synthetic_array[mask == 255]

  return Image.fromarray(blend_np)

## Lets build a cliud-based frontend to make the image  genberation the most interactive as possible and display the results

def main():
  st.title("Synthetic Image Generator")

assets = st.selectbox("Select an asset", ["Pipeline", "Pumps", "Tanks"])
defect = st.selectbox("Select a defect", ["rust", "cracks", "leaks"])

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
  background_image = Image.open(uploaded_file)
  st.image(background_image, caption="Uploaded Image", use_column_width=True)

  prompt = st.text_input("Enter the defect description you want to see on the main asset from your image")
  api_key = st.text_input("Enter your OpenAI API key:")

if st.button("Generate synthetic image..."):
  if openai_api_key and prompt:
    synthetic_image = generate_synthetic_image(prompt, api_key)
    if synthetic_image:
      mask = segment_asset(background_image)
      if mask:
        result_image = overlay_defects(background_image, synthetic_image, mask)
        st.image(result_image, caption="Synthetic Image with Defect Overlay", use_column_width=True)
    else:
      st.error("Please provide a valid prompt and API key.")

if __name__ == "__main__":
  main()
