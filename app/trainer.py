import numpy as np
import torch
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sqlalchemy import select
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from app.db import SessionLocal
from app.models import Article, TrainingLabel

MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"
LABEL2ID = {"NO_EVENTO": 0, "EVENTO": 1}
ID2LABEL = {0: "NO_EVENTO", 1: "EVENTO"}


class EventDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = self.labels[idx]
        return item


class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            weight = torch.tensor(self.class_weights, dtype=torch.float32, device=logits.device)
            loss_fn = torch.nn.CrossEntropyLoss(weight=weight)
        else:
            loss_fn = torch.nn.CrossEntropyLoss()

        loss = loss_fn(logits, labels)
        return (loss, outputs) if return_outputs else loss


def load_labeled_data() -> tuple[list[str], list[int]]:
    db = SessionLocal()
    try:
        stmt = (
            select(Article.title, Article.content, TrainingLabel.is_event)
            .join(TrainingLabel, Article.id == TrainingLabel.article_id)
            .where(TrainingLabel.labeled_by != "skipped")
        )
        rows = db.execute(stmt).all()

        texts = []
        labels = []
        for title, content, is_event in rows:
            text = f"{title or ''} {content or ''}".strip()
            if text:
                texts.append(text[:1500])
                labels.append(1 if is_event else 0)

        return texts, labels
    finally:
        db.close()


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    f1 = f1_score(labels, predictions, average="binary")
    return {"f1": f1}


def train(epochs: int = 3, batch_size: int = 16, output_dir: str = "./models/beto-events"):
    print("Loading labeled data from database...")
    texts, labels = load_labeled_data()
    print(f"  Total samples: {len(texts)}")
    print(f"  Events: {sum(labels)} | Not events: {len(labels) - sum(labels)}")

    n_event = sum(labels)
    n_not_event = len(labels) - n_event
    weight_event = n_not_event / n_event if n_event > 0 else 1.0
    class_weights = [1.0, weight_event]
    print(f"  Class weights: NOT_EVENTO=1.0, EVENTO={weight_event:.1f}")

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, stratify=labels, random_state=42
    )
    print(f"  Train: {len(train_texts)} | Val: {len(val_texts)}")

    print(f"\nLoading tokenizer and model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    print("Tokenizing...")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=512)

    train_dataset = EventDataset(train_encodings, train_labels)
    val_dataset = EventDataset(val_encodings, val_labels)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=10,
        report_to="none",
    )

    trainer = WeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print(f"\nTraining for {epochs} epochs...")
    trainer.train()

    print(f"\nSaving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\n--- Evaluation on validation set ---")
    predictions = trainer.predict(val_dataset)
    preds = np.argmax(predictions.predictions, axis=-1)
    print(classification_report(val_labels, preds, target_names=["NO_EVENTO", "EVENTO"]))

    print(f"\nDone! Model saved to: {output_dir}")
    print(f"To use it, set EVENT_CLASSIFIER_TYPE=transformer in your .env")
