import numpy as np
import cv2
import Levenshtein
from medilyzerapp.ocr.normalization import word_normalization
from medilyzerapp.ocr import page, words
from medilyzerapp.ocr.tfhelpers import Model
from medilyzerapp.ocr.datahelpers import idx2char

MODEL_LOC_CHARS = 'medilyzerapp/models/char-clas/en/CharClassifier'
MODEL_LOC_CTC = 'medilyzerapp/models/word-clas/CTC/Classifier1'
CHARACTER_MODEL = Model(MODEL_LOC_CHARS)
CTC_MODEL = Model(MODEL_LOC_CTC, 'word_prediction')

def load_words_list(file_path):
    with open(file_path, 'r') as file:
        words_list = [line.strip() for line in file.readlines()]
    return words_list

words_list_path = 'medilyzerapp/words_list.txt'
words_list = load_words_list(words_list_path)
threshold=0.5


def recognize_and_compare(image_path):
    def recognize(img):
        """Recognising words using CTC Model."""
        img = word_normalization(img, 64, border=False, tilt=False, hyst_norm=False)
        length = img.shape[1]
        # Input has shape [batch_size, height, width, 1]
        input_imgs = np.zeros((1, 64, length, 1), dtype=np.uint8)
        input_imgs[0][:, :length, 0] = img

        pred = CTC_MODEL.eval_feed({
            'inputs:0': input_imgs,
            'inputs_length:0': [length],
            'keep_prob:0': 1})[0]

        word = ''
        for i in pred:
            word += idx2char(i + 1)
        return word

    image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

    crop = page.detection(image)
    boxes = words.detection(crop)
    lines = words.sort_words(boxes)

    recognized_words_list = []  

    for line in lines:
        recognized_words_line = []  
        for (x1, y1, x2, y2) in line:
            recognized_word = recognize(crop[y1:y2, x1:x2])
            recognized_words_line.append(recognized_word)
        recognized_words_list.append(recognized_words_line)

    def find_most_similar_word(word, word_list, threshold):
        most_similar_word = None
        min_distance = float('inf')

        for candidate_word in word_list:
            distance = Levenshtein.distance(word, candidate_word)
            similarity_ratio = 1 - (distance / max(len(word), len(candidate_word)))
            if similarity_ratio >= threshold and distance < min_distance:
                min_distance = distance
                most_similar_word = candidate_word

        return most_similar_word

    most_similar_words_list = []

    for recognized_words_line in recognized_words_list:
        most_similar_words_line = []

        for word in recognized_words_line:
            # Find the most similar word from the word list
            most_similar_word = find_most_similar_word(word, words_list, threshold)
            if most_similar_word:
                most_similar_words_line.append(most_similar_word)
            else:
                most_similar_words_line.append(word)  # Empty string if no similar word found

        # Append the most similar words for the current line to the list
        most_similar_words_list.append(most_similar_words_line)

    for line, most_similar_words_line in zip(lines, most_similar_words_list):
        for (x1, y1, x2, y2), recognized_word in zip(line, most_similar_words_line):
            # Draw bounding box with red color
            cv2.rectangle(crop, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # Write detected word above the bounding box with larger font size
            cv2.putText(crop, recognized_word, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return crop
