import cv2
import os
import numpy as np
from deepface import DeepFace
from PIL import Image
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

# Define the main function
def main():
    # Set up the dictionaries to store the emotion scores
    sums = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    counts = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    dominant_emotions = []

    # Set up the upscale factor
    upscale_factor = int(1)

    # Create the dataset folder if it does not exist
    if not os.path.exists('dataset'):
        os.makedirs('dataset')

    # Set up the OpenCV video capture object to capture frames from the webcam
    cap = cv2.VideoCapture(0)

    # Define the Streamlit app
    st.title('Real-Time Face Expression Recognition using DeepLearning')
    st.write('This app captures images from your webcam and analyzes the emotions in the images using DeepFace.')
    st.write('Click the button below to start the analysis.')

    # Define the 'Start' button
    if st.button('Start'):
        # Capture 50 images from the webcam and save them in the dataset folder
        count = 0
        error_occurred = False

        while count < 10:
            # Capture a frame from the webcam
            ret, frame = cap.read()

            # Convert the frame to a PIL Image object
            img = Image.fromarray(frame)

            # Upscale the image using bicubic interpolation
            upscaled_img = img.resize((img.size[0] * upscale_factor, img.size[1] * upscale_factor), resample=Image.LANCZOS)

            # Upscale the image using nearest-neighbor interpolation
            upscaled_img = img.resize((img.size[0] * upscale_factor, img.size[1] * upscale_factor), resample=Image.NEAREST)

            # Convert the upscaled image back to an OpenCV frame
            frame = np.array(upscaled_img)

            # Save the frame as an image file in the dataset folder
            filename = f'img_{count}.jpg'
            file_path = os.path.join('dataset', filename)
            cv2.imwrite(file_path, frame)

            # Analyze the emotions in the image using DeepFace
            try:
                result = DeepFace.analyze(file_path, actions=['emotion'], enforce_detection=True)
                dominant_emotions.append(result[0]['dominant_emotion'])
            except Exception as e:
                if not error_occurred:
                    #st.warning(f'Error analyzing {file_path}: {str(e)}')
                    st.warning('Face is not detected. Place your face in front of the camera')
                    error_occurred = True
                continue

            # Update the emotion scores
            emotions = result[0]['emotion']
            for emotion, score in emotions.items():
                sums[emotion] += score
                counts[emotion] += 1

            # Increment the counter
            count += 1

            # Reset the error flag
            error_occurred = False

        # Release the OpenCV video capture object and close the window
        cap.release()

        # Calculate the average emotion scores
        averages = {}
        for emotion, score_sum in sums.items():
            if counts[emotion] == 0:
                averages[emotion] = 0
            else:
                averages[emotion] = score_sum / counts[emotion]

        # Sort the average emotion scores in ascending order
        sorted_averages = sorted(averages.items(), key=lambda x: x[1])

        # Print the results
        st.write('Average emotion scores in ascending order:')
        for emotion, score in sorted_averages:
            st.write(f'{emotion.capitalize()}: {score:.2f}')

        # Create a pie chart of the average emotion scores
        labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        sizes = [averages['angry'], averages['disgust'], averages['fear'], averages['happy'], averages['sad'], averages['surprise'], averages['neutral']]
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4', '#9467bd', '#8c564b', '#e377c2']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Average Emotion Scores')

       # Sort the labels and sizes in ascending order
        sorted_labels, sorted_sizes = zip(*sorted(zip(labels, sizes), key=lambda x: x[1]))

        fig = go.Figure(data=[go.Pie(labels=sorted_labels, values=sorted_sizes, textinfo='none')])
        fig.update_traces(marker=dict(colors=colors))
        

        fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, textinfo='none')])
        fig.update_traces(marker=dict(colors=colors))
        fig.update_layout(title_text='Average Emotion Scores', legend=dict(title='Emotions', orientation='h', yanchor='bottom', y=-0.1, xanchor='center', x=0.5))
        st.plotly_chart(fig)

        # Create a list ofthe emotion labels and sizes sorted in ascending order
        labels = [emotion.capitalize() for emotion, score in sorted_averages]
        sizes = [averages[emotion] for emotion, score in sorted_averages]

        # Create the legend labels sorted in ascending order of emotion score
        legend_labels = [f'{label} ({sizes[i]:.1f}%)' for i, label in enumerate(labels)]

        

# Call the main function
if __name__ == '__main__':
    main()
