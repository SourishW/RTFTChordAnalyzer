import librosa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
import numpy as np

import tensorflow as tf
# from tesn.keras.models import load_model

import caleb_files.data_generators as dg

def audio_to_img(file_name):
    samples, sample_rate = librosa.load(file_name, sr=None)
    sgram = librosa.stft(samples)
        
        
    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True)
    sgram_mag, _ = librosa.magphase(sgram)
    
    mel_scale_sgram = librosa.feature.melspectrogram(S=sgram_mag, sr=sample_rate)
    mel_sgram = librosa.amplitude_to_db(mel_scale_sgram, ref=np.min)
    img = librosa.display.specshow(mel_sgram,y_axis='linear', x_axis='time', ax = ax)
    plt.axis('off')

    canvas = FigureCanvasAgg(plt.gcf())

    # Render the plot as a numpy array
    canvas.draw()
    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(canvas.get_width_height()[::-1] + (3,))  # Reshape to height, width, channels

    non_white_indices = np.where(image != 255)  # Assuming white is represented as 255
    min_x, min_y = np.min(non_white_indices[1]), np.min(non_white_indices[0])
    max_x, max_y = np.max(non_white_indices[1]), np.max(non_white_indices[0])


    # Convert numpy array to PIL Image object
    return Image.fromarray(image[min_y:max_y, min_x:max_x])

def make_prediction(img, model):
    trainable_img = img.resize((dg.targ_height, dg.targ_width))
    trainable_arr = np.array(trainable_img) / 255.0
    # print(trainable_arr)
    prediction = model.predict(np.reshape(trainable_arr, (-1, 256, 256, 3)))
    prediction = np.ravel(prediction)
    sorted_indices = np.argsort(prediction)
    print(prediction)
    print(sorted_indices)

    
    
tf.random.set_seed(42)
np.random.seed(24)

class_indices = dg.get_data().class_indices

# Reverse the dictionary to map indices to class names
class_names = {v: k for k, v in class_indices.items()}

print(class_names)

img = audio_to_img('wav/03a01Fa.wav')
img2 = audio_to_img('wav/03a01Nc.wav')
model = tf.keras.models.load_model("CNN_model.keras")

for layer in model.layers:
    if isinstance(layer, tf.keras.layers.Dropout):
        layer.rate = 0.0  # Set dropout rate to 0 for inference


make_prediction(img, model)
make_prediction(img2, model)


