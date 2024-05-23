#!/bin/bash

#SBATCH --account=3214046
#SBATCH --partition=dsba
#SBATCH --gpus=1
#SBATCH --mem=10G
#SBATCH --job-name="RNN"
#SBATCH --time=05:00:00
#SBATCH --output=/home/3214046/my_dir/output/RNN%x_%j.out
#SBATCH --error=/home/3214046/my_dir/error/RNN%x_%j.err

## importing packages
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from pymongo import MongoClient
import logging

# Connect to MongoDB collection
client = MongoClient("mongodb://49.13.173.177:27020/")
collection = client.sponsoredbye.embeddings

# Set environment variables
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['MKL_THREADING_LAYER'] = 'GNU'

# Configure logging
logging.basicConfig(level=logging.INFO)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Create directory for checkpoints if it does not exist
checkpoint_dir = '/home/3214046/checkpoints'
os.makedirs(checkpoint_dir, exist_ok=True)

def save_checkpoint(state, filename='checkpoint.pth.tar'):
    """
    Saves the training state to a file.
    """
    torch.save(state, filename)
    logging.info(f"Checkpoint saved to '{filename}'")

def load_checkpoint(model, optimizer, filename='model_checkpoint_index.pth.tar'):
    """
    Loads the training state from a file.
    """
    if os.path.isfile(filename):
        logging.info(f"Loading checkpoint '{filename}'")
        checkpoint = torch.load(filename, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        epoch = checkpoint['epoch']
        last_index = checkpoint.get('last_index', 0)
        logging.info(f"Loaded checkpoint '{filename}' (epoch {epoch}, last index {last_index})")
        return epoch, last_index
    else:
        logging.info(f"No checkpoint found at '{filename}'")
        return 0, 0

def get_batch(batch_size=20, start_index=0):
    """
    Generates batches of data from MongoDB collection.
    """
    documents = collection.find().skip(start_index).limit(6000)
    batch = []
    count = 0
    for doc in documents:
        try:
            batch.append(doc)
            count += 1
            if count >= batch_size:
                yield batch, start_index + count
                batch = []
                count = 0
        except Exception as e:
            logging.error(f"An error occurred: {e} in {doc.get('videoID', 'unknown')}")
    if batch:
        yield batch, start_index + count

def adapt_data(batch):
    """
    Adapts raw MongoDB documents into a list of dictionaries containing videoID, embeddings, and labels.
    """
    data = []
    for doc in batch:
        try:
            for i, embedding in enumerate(doc['embeddings']):
                data.append({
                    'videoID': doc['videoID'],
                    'embedding': [float(num) for num in embedding['embedding']],
                    'label': doc['label'][i]
                })
        except Exception as e:
            logging.error(f"An error occurred: {e} in {doc['videoID']}")
    return data

# Define RNN model
input_size = 768 
hidden_size = 768
num_layers = 2
num_classes = 2

class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        """
        Initializes the RNN model with the specified parameters.
        """
        super(RNN, self).__init__()
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x, mask):
        """
        Defines the forward pass of the model.
        """
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.rnn(x, h0)
        out = out * mask.unsqueeze(-1)
        out = self.fc(out)
        return out

max_length = 1682  

model = RNN(input_size, hidden_size, num_layers, num_classes).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Load the model state from the checkpoint if it exists
start_epoch, start_index = load_checkpoint(model, optimizer, os.path.join(checkpoint_dir, 'model_checkpoint_index_10800.pth.tar'))

batch_size = 100
logging.info(f"You started from {batch_size * start_index}")
batch_generator = get_batch(batch_size=batch_size, start_index=start_index)

batches_count = 0
for batch, current_index in batch_generator:
    batches_count += 1
    logging.info(f"count {batches_count}")
    model.train()
    data = adapt_data(batch)

    video_ids = list(set(item['videoID'] for item in data))

    for video_id in tqdm(video_ids):
        video_data = [item for item in data if item['videoID'] == video_id]
        embeddings = [item['embedding'] for item in video_data]
        labels = [item['label'] for item in video_data]

        original_length = len(embeddings)
        pad_length = max_length - original_length
        if pad_length > 0:
            masks = [1] * len(embeddings) + [0] * pad_length
            embeddings.extend([[0.0] * len(embeddings[0])] * pad_length)
            labels.extend([-1] * pad_length)
        else:
            masks = [1] * max_length

        embeddings_tensor = torch.tensor(embeddings, dtype=torch.float32).unsqueeze(0).to(device)
        labels_tensor = torch.tensor(labels, dtype=torch.long).unsqueeze(0).to(device)
        masks_tensor = torch.tensor(masks, dtype=torch.float32).to(device)

        outputs = model(embeddings_tensor, masks_tensor)

        outputs = outputs.view(-1, outputs.size(-1))
        labels = labels_tensor.view(-1)
        masks = masks_tensor.view(-1)

        valid_outputs = outputs[masks > 0]
        valid_labels = labels[masks > 0]
        loss = criterion(valid_outputs, valid_labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if batches_count % 10 == 0:
        num = batch_size * start_index + batches_count * batch_size
        checkpoint_filename = f"model_checkpoint_index_{num}.pth.tar"
        checkpoint_path = os.path.join(checkpoint_dir, checkpoint_filename)
        logging.info(f"count save {num}")
        
        # Save the checkpoint
        state = {
            'epoch': batches_count,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss.item(),
            'last_index': current_index
        }
        save_checkpoint(state, checkpoint_path)

logging.info("Training complete.")
save_model_state(model, 'model_weights.pth')
