# import rulebot
# from datasets import load_dataset, DatasetDict
#
# # Lade den bestehenden SQuAD-Datensatz
# dataset = load_dataset("json", data_files=str(rulebot.data_dir) + "/json/squad/situations/updated_squad.json", field="data")
#
# # Aufteilen in 80% Training und 20% Validation
# train_test_split = dataset["train"].train_test_split(test_size=0.2, seed=42)
#
# # Speichere die aufgeteilten Datensätze
# squad_dataset = DatasetDict({
#     "train": train_test_split["train"],
#     "validation": train_test_split["test"]
# })
#
# # Speichern der neuen aufgeteilten Datei
# squad_dataset.save_to_disk(str(rulebot.data_dir) + "/json/squad/situations/split_squad")

#----------------------------------------------------------------------------------------------

# import rulebot
# from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
#
# model_path = str(rulebot.data_dir) + "/roberta/roberta_model_trained_v3"
# tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForQuestionAnswering.from_pretrained(model_path)
#
# nlp_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
#
# # example = {
# #     'question': "During a breakaway, shootout attempt (or Penalty Shot) the goalkeeper deliberately removes its helmet and/or facemask. What action should be taken by the Referee? Where do you find this in the rule book?",
# #     'context': "If the Goalkeeper deliberately removes their helmet and/or face mask when the opposing Team is on a breakaway (where the criteria’s for a penalty shot is meet except for a foul from behind), or during the course of a “Penalty Shot” or shootout attempt, the Referee shall award a goal to the non-offending Team."
# # }
#
# question = "Team A scores on a Penalty Shot while on the power play. Does that mean that Team B get the penalized player back in play? Where do you find this in the rule book?"
# context = "This rule does not apply when a goal is scored on a “Penalty Shot” (i.e., offending Team’s penalized Player(s) do not get released on the scoring of a goal on a “Penalty Shot”)"
#
# result = nlp_pipeline(question=question, context=context)
# print(result)




