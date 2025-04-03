import json
from transformers import (AutoTokenizer, AutoModelForQuestionAnswering, Trainer, TrainingArguments, DefaultDataCollator, EarlyStoppingCallback)
from datasets import load_dataset, DatasetDict, Dataset, load_from_disk, dataset_dict
from config import FirstTrainingConfig, FineTuningConfig

class RoBERTaTrainer:
    def __init__(self, model_config):
        self.config = model_config

        # load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_config["model_name"])
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_config["model_name"])

    def load_dataset(self, path):
        print(f"Loading dataset from {path}...\n")
        dataset = load_dataset('json', data_files=path, field='data')
        return dataset

    def flatten_dataset(self, dataset):
        contexts = []
        questions = []
        answers = []

        # Iteriere durch jeden Artikel im Dataset
        for article in dataset['train']:
            for paragraph in article['paragraphs']:
                context = paragraph['context']
                for qa in paragraph['qas']:
                    question = qa['question']
                    for answer in qa['answers']:
                        contexts.append(context)
                        questions.append(question)
                        answers.append({
                            'text': answer['text'],
                            'answer_start': answer['answer_start']
                        })

        # Erstelle ein flaches Dataset
        flattened_train_dataset = Dataset.from_dict({
            'context': contexts,
            'question': questions,
            'answers': answers
        })

        return DatasetDict({'train': flattened_train_dataset})

    def split_dataset(self, dataset, train_ratio=0.8):
        """Splits a dataset into train and validation splits."""
        train_size = int(len(dataset) * train_ratio)
        train_dataset = dataset.select(range(train_size))
        validation_dataset = dataset.select(range(train_size, len(dataset)))
        return DatasetDict({"train": train_dataset, "validation": validation_dataset})

    def preprocess_data(self, dataset):
        def preprocess_function(examples):
            questions = [q.lstrip() for q in examples["question"]]
            inputs = self.tokenizer(
                questions,
                examples["context"],
                max_length=512,
                truncation=True,
                padding="max_length"
            )

            # Process answers
            start_positions = []
            end_positions = []

            for i, answer in enumerate(examples["answers"]):
                start = answer["answer_start"]
                end = start + len(answer["text"])
                start_positions.append(start)
                end_positions.append(end)

            inputs["start_positions"] = start_positions
            inputs["end_positions"] = end_positions

            return inputs

        print("Preprocessing dataset...\n")

        split_datasets = self.split_dataset(dataset["train"])
        tokenized_dataset = split_datasets.map(preprocess_function, batched=True, remove_columns=dataset["train"].column_names)
        return tokenized_dataset

    def train(self):
        raw_dataset = self.load_dataset(self.config["train_file"])
        flattened_dataset = self.flatten_dataset(raw_dataset)
        tokenized_dataset = self.preprocess_data(flattened_dataset)

        data_collator = DefaultDataCollator()

        training_args = TrainingArguments(
            output_dir=self.config["output_dir"],
            eval_strategy=self.config["evaluation_strategy"],
            learning_rate=self.config["learning_rate"],
            per_device_train_batch_size=self.config["train_batch_size"],
            per_device_eval_batch_size=self.config["eval_batch_size"],
            num_train_epochs=self.config["num_train_epochs"],
            weight_decay=self.config["weight_decay"],
            save_strategy=self.config["save_strategy"],
            logging_dir=self.config["logging_dir"],
            logging_steps=self.config["logging_steps"],
            log_level="info",
            log_level_replica="info",
            fp16=FineTuningConfig["fp16"],
            gradient_accumulation_steps=FineTuningConfig["gradient_accumulation_steps"],
            lr_scheduler_type=FineTuningConfig["lr_scheduler_type"],
            max_grad_norm=FineTuningConfig["max_grad_norm"],
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset["validation"],
            processing_class=self.tokenizer,
            data_collator=data_collator,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=self.config["early_stopping_patience"])],
        )

        print("Starting training...\n")
        trainer.train()

        print("Saving model...\n")
        trainer.save_model(self.config["output_dir"])
        self.model.save_pretrained(self.config["output_dir"])
        self.tokenizer.save_pretrained(self.config["output_dir"])
        print("Model saved successfully.\n")

if __name__ == "__main__":
    fine_tuning = True
    trainer = RoBERTaTrainer(FirstTrainingConfig if not fine_tuning else FineTuningConfig)
    trainer.train()
