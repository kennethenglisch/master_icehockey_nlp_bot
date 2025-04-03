from transformers import AutoTokenizer, AutoModelForQuestionAnswering, Trainer, TrainingArguments
from datasets import load_dataset, DatasetDict, Dataset
from evaluate import load
from config import EvaluationConfig

class RoBERTaEvaluator:
    def __init__(self, config):
        """
        Initialize the evaluator with the provided configuration.
        """
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_path"])
        self.model = AutoModelForQuestionAnswering.from_pretrained(config["model_path"])

    def load_dataset(self, path):
        print(f"Loading dataset from {path}...\n")
        return load_dataset('json', data_files=path, field='data')

    def flatten_dataset(self, dataset):
        contexts = []
        questions = []
        answers = []

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

        flattened_dataset = Dataset.from_dict({
            'context': contexts,
            'question': questions,
            'answers': answers
        })

        return DatasetDict({'train': flattened_dataset})

    def split_dataset(self, dataset, train_ratio=0.8):
        """Splits a dataset into train and validation splits."""
        train_size = int(len(dataset) * train_ratio)
        train_dataset = dataset.select(range(train_size))
        validation_dataset = dataset.select(range(train_size, len(dataset)))
        return DatasetDict({"train": train_dataset, "validation": validation_dataset})

    def preprocess_data(self, dataset):
        def preprocess_function(examples):
            return self.tokenizer(
                examples["question"],
                examples["context"],
                max_length=self.config["max_seq_length"],
                truncation=True,
                padding="max_length"
            )

        print("Preprocessing evaluation dataset...")
        split_datasets = self.split_dataset(dataset["train"])
        tokenized_dataset = split_datasets.map(preprocess_function, batched=True, remove_columns=dataset["train"].column_names)
        return tokenized_dataset

    def compute_metrics(self, eval_predictions):
        predictions, labels = eval_predictions

        squad_metric = load("squad_v2")

        # Format predictions correctly
        formatted_predictions = [
            {
                "id": pred["id"],
                "prediction_text": pred["prediction_text"],
                "no_answer_probability": pred.get("no_answer_probability", 0.0),
            }
            for pred in predictions
        ]

        # Format labels correctly by extracting answers from the nested structure
        formatted_labels = [
            {
                "id": label["id"],
                "answers": {
                    "text": [ans["text"] for ans in label["answers"]],
                    "answer_start": [ans["answer_start"] for ans in label["answers"]]
                }
            }
            for label in labels
        ]

        results = squad_metric.compute(predictions=formatted_predictions, references=formatted_labels)

        return results

    def evaluate(self):
        """
        Perform evaluation on the model using the processed dataset.
        """
        raw_dataset = self.load_dataset(self.config["eval_file"])
        flattened_dataset = self.flatten_dataset(raw_dataset)
        tokenized_dataset = self.preprocess_data(flattened_dataset)

        trainer = Trainer(
            model=self.model,
            processing_class=self.tokenizer,
            eval_dataset=tokenized_dataset,
            compute_metrics=self.compute_metrics
        )

        print("Starting evaluation...")
        results = trainer.evaluate()
        print("Evaluation results:", results)

        return results


if __name__ == "__main__":
    evaluator = RoBERTaEvaluator(EvaluationConfig)

    eval_predictions_a = (
        [
            {
                "id": "1.1",
                "prediction_text": "This is not allowed according to Rule 87.2 and should be reported to proper authorities.",
                "no_answer_probability": 0.0
            },
            {
                "id": "4.1",
                "prediction_text": "Yes. As soon as one of the officials notices that time has expired, they should blow the whistle to stop play.",
                "no_answer_probability": 0.0
            },
            {
                "id": "4.2",
                "prediction_text": "Play may continue until the officials have the opportunity and/or need to stop the play.",
                "no_answer_probability": 0.0
            }
        ],
        [
            {
                "id": "1.1",
                "answers": [
                    {
                        "text": "This is not allowed according to Rule 87.2 and should be reported to proper authorities.",
                        "answer_start": 0
                    }
                ]
            },
            {
                "id": "4.1",
                "answers": [
                    {
                        "text": "Yes. As soon as one of the officials notices that time has expired, they should blow the whistle to stop play. If a goal is scored after time has run out (but before an official notices), the Referee shall consult with the Video Review Consultant, and the goal may be disallowed. Rule 4.",
                        "answer_start": 0
                    }
                ]
            },
            {
                "id": "4.2",
                "answers": [
                    {
                        "text": "Play may continue until the officials have the opportunity and/or need to stop the play (if stopped, it should be done when the puck is in the neutral zone, and when no immediate scoring opportunity is imminent – i.e., breakaway, empty net, etc.). Play may be allowed to continue to a normal stoppage in play. The Referee should then confer with the Game Timekeeper and/or the Video Review Consultant to reset the clock to the proper time. Rule 4, Rule 34.7 and Rule 37.6.",
                        "answer_start": 0
                    }
                ]
            }
        ]
    )

    result_a = evaluator.compute_metrics(eval_predictions_a)
    print("Test metric output:", result_a)

    evaluator.evaluate()
