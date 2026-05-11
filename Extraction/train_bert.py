import json
import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset

# ── Use DistilBERT — lighter, faster, better on small datasets than full BERT ─
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "./bert_clause_model"
MAX_LENGTH = 128

# ── Load data ─────────────────────────────────────────────────────────────────
with open('training_data.json', 'r') as f:
    data = json.load(f)

texts  = [d['text']  for d in data]
labels = [d['label'] for d in data]

# ── Encode labels ─────────────────────────────────────────────────────────────
le = LabelEncoder()
encoded_labels = le.fit_transform(labels)

label_map = {int(i): label for i, label in enumerate(le.classes_)}
with open('label_map.json', 'w') as f:
    json.dump(label_map, f, indent=2)
print(f"✓ {len(label_map)} clause types: {list(label_map.values())}")

# ── Train / validation split ──────────────────────────────────────────────────
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, encoded_labels,
    test_size=0.15,
    random_state=42,
    stratify=encoded_labels
)
print(f"✓ Train: {len(train_texts)}  Validation: {len(val_texts)}")

# ── Tokenize ──────────────────────────────────────────────────────────────────
print("✓ Loading DistilBERT tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(text_list):
    return tokenizer(
        text_list,
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )

train_enc = tokenize(train_texts)
val_enc   = tokenize(val_texts)

class ClauseDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels    = labels
    def __len__(self):
        return len(self.labels)
    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

train_dataset = ClauseDataset(train_enc, train_labels)
val_dataset   = ClauseDataset(val_enc,   val_labels)

# ── Load model ────────────────────────────────────────────────────────────────
print("✓ Loading DistilBERT model (downloads ~250MB first time)...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label_map)
)

# ── Training args — tuned for small datasets ──────────────────────────────────
training_args = TrainingArguments(
    output_dir              = OUTPUT_DIR,
    num_train_epochs        = 10,           # more epochs for small data
    per_device_train_batch_size = 16,
    per_device_eval_batch_size  = 16,
    learning_rate           = 2e-5,         # key: lower LR = better fine-tuning
    warmup_ratio            = 0.1,          # warmup prevents early overshooting
    weight_decay            = 0.01,         # regularization to prevent overfitting
    eval_strategy     = "epoch",
    save_strategy           = "epoch",
    load_best_model_at_end  = True,
    metric_for_best_model   = "accuracy",
    logging_steps           = 5,
    fp16                    = False,        # set True if you have a GPU
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds    = np.argmax(logits, axis=1)
    accuracy = (preds == labels).mean()
    return {"accuracy": round(float(accuracy), 4)}

trainer = Trainer(
    model           = model,
    args            = training_args,
    train_dataset   = train_dataset,
    eval_dataset    = val_dataset,
    compute_metrics = compute_metrics,
    callbacks       = [EarlyStoppingCallback(early_stopping_patience=3)]
)

print("\n✓ Training started — watch accuracy climb each epoch...")
trainer.train()

# ── Save ──────────────────────────────────────────────────────────────────────
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"\n✓ Done! Model saved to {OUTPUT_DIR}")
print("✓ Run: python app.py")