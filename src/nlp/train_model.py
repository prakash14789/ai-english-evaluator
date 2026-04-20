from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from datasets import Dataset
import torch

def train_grammar_model(data_pairs, output_dir="./local_grammar_model"):
    """
    Trains (fine-tunes) a T5 model on provided (input, output) pairs.
    data_pairs: List of tuples (incorrect_sentence, correct_sentence)
    """
    model_name = "t5-small" # Use small for demonstration/local training speed
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # Prepare dataset
    def preprocess_function(examples):
        inputs = ["gec: " + doc for doc in examples["input"]]
        model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
        
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(examples["output"], max_length=128, truncation=True, padding="max_length")

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    # Convert list to HuggingFace Dataset
    inputs = [p[0] for p in data_pairs]
    outputs = [p[1] for p in data_pairs]
    raw_dataset = Dataset.from_dict({"input": inputs, "output": outputs})
    
    tokenized_dataset = raw_dataset.map(preprocess_function, batched=True)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=10,
        save_total_limit=2,
        logging_steps=1,
        learning_rate=5e-5,
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    print("Starting training...")
    trainer.train()
    
    print(f"Saving model to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Training complete.")

if __name__ == "__main__":
    # Example toy dataset
    toy_data = [
        ("i goes to school", "I go to school"),
        ("he don't like apple", "He doesn't like apples"),
        ("she sing good", "She sings well"),
        ("where you are?", "Where are you?"),
        ("i has a book", "I have a book"),
    ]
    
    # In a real scenario, the user would provide a CSV or JSON with thousands of rows
    print("This is a demo script to train your own English model.")
    print("Training on 5 examples for demonstration purposes...")
    train_grammar_model(toy_data)
