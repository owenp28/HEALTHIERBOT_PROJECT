from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, Wav2Vec2ForCTC, Wav2Vec2Processor
from torch.utils.data import Dataset
import torch
import librosa
import json
import os

# Load the dataset with error handling (only when training)
def load_dataset():
    try:
        with open('chatbot_medical_dataset.json', 'r') as file:
            dataset = json.load(file)
        # Validate dataset keys
        for entry in dataset:
            if 'prompt' not in entry or 'response' not in entry:
                raise ValueError("Each dataset entry must contain 'prompt' and 'response' keys.")
        return dataset
    except FileNotFoundError:
        raise FileNotFoundError("The dataset file 'chatbot_medical_dataset.json' was not found.")
    except json.JSONDecodeError:
        raise ValueError("The dataset file is not a valid JSON file.")

# Define a custom dataset class
class MedicalDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        prompt = self.data[idx]['prompt']
        response = self.data[idx]['response']
        inputs = self.tokenizer(prompt, return_tensors='pt', max_length=self.max_length, truncation=True, padding='max_length')
        outputs = self.tokenizer(response, return_tensors='pt', max_length=self.max_length, truncation=True, padding='max_length')
        input_ids = inputs['input_ids'][0]
        attention_mask = inputs['attention_mask'][0]
        labels = outputs['input_ids'][0]
        return {'input_ids': input_ids, 'attention_mask': attention_mask, 'labels': labels}

# Initialize the tokenizer and model
MODEL_NAME = "llama4:scout"  # Using the latest Llama 4 Scout model
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # Set padding token to eos_token if not already set
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
except OSError as e:
    print(f"Error loading model {MODEL_NAME}: {e}")
    # Fallback to another available model
    MODEL_NAME = "distilgpt2"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Only create train_dataset when training
def get_train_dataset(tokenizer):
    dataset = load_dataset()
    try:
        train_dataset = MedicalDataset(dataset, tokenizer)
    except KeyError as e:
        raise ValueError(f"Dataset is missing expected keys: {e}")
    return train_dataset

# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=10,
    save_total_limit=2,
    logging_dir='./logs',
    logging_steps=10,
)

# Initialize the Trainer (only when training)
def train_model():
    train_dataset = get_train_dataset(tokenizer)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )
    trainer.train()
    model.save_pretrained('./fine_tuned_model')
    tokenizer.save_pretrained('./fine_tuned_model')

# Train the model only if this file is run directly for training
if __name__ == "__main__" and not os.environ.get("RUN_INFERENCE"):
    train_model()

# Function to load model for inference
def load_model():
    model_path = './fine_tuned_model'
    if os.path.exists(model_path):
        try:
            loaded_model = AutoModelForCausalLM.from_pretrained(model_path)
            loaded_tokenizer = AutoTokenizer.from_pretrained(model_path)
            return loaded_model, loaded_tokenizer
        except Exception as e:
            print(f"Error loading fine-tuned model: {e}")
    
    # Fallback to base model if fine-tuned model doesn't exist or fails to load
    print("Using base model for inference")
    return model, tokenizer

def generate_response(prompt, max_length=100):
    # Load the model only when needed
    inference_model, inference_tokenizer = load_model()
    inputs = inference_tokenizer(prompt, return_tensors='pt')
    outputs = inference_model.generate(
        inputs['input_ids'],
        max_length=max_length,
        num_return_sequences=1,
        pad_token_id=inference_tokenizer.eos_token_id
    )
    response = inference_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Function to transcribe audio using wav2vec2-medical
def transcribe_audio(audio_path):
    # Load the wav2vec2 model and processor
    wav2vec2_model = Wav2Vec2ForCTC.from_pretrained("AndersenC4/wav2vec2-medical")
    wav2vec2_processor = Wav2Vec2Processor.from_pretrained("AndersenC4/wav2vec2-medical")

    # Load audio file
    audio, rate = librosa.load(audio_path, sr=16000)

    # Process audio
    inputs = wav2vec2_processor(audio, sampling_rate=rate, return_tensors="pt", padding=True)

    # Perform inference
    with torch.no_grad():
        logits = wav2vec2_model(inputs.input_values).logits

    # Decode the output
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = wav2vec2_processor.batch_decode(predicted_ids)
    return transcription
# Example usage for inference
if __name__ == "__main__" and os.environ.get("RUN_INFERENCE") == "1":
    prompt = "What are the symptoms of flu?"
    response = generate_response(prompt)
    print(response)

    # Example usage for speech recognition
    audio_path = "path_to_your_audio_file.wav"
    transcription = transcribe_audio(audio_path)
    print(transcription)
