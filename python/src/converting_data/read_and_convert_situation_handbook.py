import os
import fitz
import json
import re
import rulebot

class SituationHandbookExtractor:
    def __init__(self):
        self.docs = []

        # section number: font-size=12.0, font-color=21407, font=RobotoCondensed-Bold, example=SECTION 01
        self.section_number_font_size = 12.0
        self.section_number_font_color = 21407
        self.section_number_font = "RobotoCondensed-Regular"

        # section name: font-size=25.744544982910156, font-color=21407, font=RobotoCondensed-Light, example=PLAYING AREA
        self.section_name_font_size = 25.744544982910156
        self.section_name_font_color = 21407
        self.section_name_font = "RobotoCondensed-Light"

        # rule headline: font-size=11.0, font-color=21407, font=RobotoCondensed-Regular, example=RULE 1
        self.rule_headline_font_size = 12.0
        self.rule_headline_font_color = 21407
        self.rule_headline_font = "RobotoCondensed-Regular"

        # situation number: font-size=12.0, font-color=21407, font=RobotoCondensed-Regular, example=SITUATION 1.1
        self.situation_number_font_size = 12.0
        self.situation_number_font_color = 21407
        self.situation_number_font = "RobotoCondensed-Regular"

        # situation question text: font-size=10.0, font-color=0, font=RobotoCondensed-Light, example=During the overtime...
        self.situation_question_text_font_size = 10.0
        self.situation_question_text_font_color = 0
        self.situation_question_text_font = "RobotoCondensed-Light"

        # situation answer headline: font-size=12.0, font-color=45292, font=RobotoCondensed-Regular, example=ANSWER
        self.situation_answer_headline_font_size = 12.0
        self.situation_answer_headline_font_color = 45292
        self.situation_answer_headline_font = "RobotoCondensed-Regular"

        # situation answer: font-size=10.0, font-color=0, font=RobotoCondensed-Light, example=This is not allowed...
        self.situation_answer_text_font_size = 10.0
        self.situation_answer_text_font_color = 0
        self.situation_answer_text_font = "RobotoCondensed-Light"

        self.current_section_number = None
        self.current_section_name = None
        self.current_rule_number = None
        self.current_situation_number = None
        self.current_question_text = ""
        self.current_answer_text = ""

        self.answer_headline_found = False

        self.old_section_number = None
        self.old_section_name = None
        self.old_rule_number = None
        self.old_situation_number = None

    def get_all_font_sizes(self):
        font_sizes = {
            self.section_number_font_size,
            self.section_name_font_size,
            self.rule_headline_font_size,
            self.situation_number_font_size,
            self.situation_question_text_font_size,
            self.situation_answer_headline_font_size,
            self.situation_answer_text_font_size,
        }

        return font_sizes

    def get_smallest_font_size(self):
        return min(self.get_all_font_sizes())

    def get_greatest_font_size(self):
        return max(self.get_all_font_sizes())

    @staticmethod
    def get_pdf_path():
        pdf_path = input(
            "Bitte geben Sie den Pfad zu Ihrem Situation Handbook (PDF) ein oder wählen Sie eine der folgenden Optionen\n1 - situation_handbook_two_sections_test.pdf\nEnter oder 2 - 2024_iihf_situationhandbook_07102024-v2_0.pdf\n----------------\nDeine Auswahl: ")

        if pdf_path == "1":
            pdf_path = str(rulebot.data_dir) + "/pdf/situation_handbook_two_sections_test.pdf"

        if pdf_path == "" or pdf_path == "2":
            pdf_path = str(rulebot.data_dir) + "/pdf/2024_iihf_situationhandbook_07102024-v2_0.pdf"

        if not os.path.isfile(pdf_path):
            print("Der angegebene Pfad ist ungültig. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")
            print(pdf_path)
            return None

        return pdf_path

    def extract_situations_from_pdf(self, pdf_path):
        last_span = None

        current_section = []
        current_rule = []
        current_situation = []

        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                for page_text in page.get_text("dict", None, None, None, True)["blocks"]:
                    if "lines" in page_text:
                        for line in page_text["lines"]:
                            if self.is_horizontal_text(line["dir"]):
                                for span in line["spans"]:

                                    anything_found = False

                                    text = span["text"].strip()
                                    font_size = span["size"]
                                    font_color = span["color"]
                                    font = span["font"]

                                    if font_size < self.get_smallest_font_size() or font_size > self.get_greatest_font_size():
                                        continue

                                    # check for section number
                                    if not anything_found:
                                        section_number_result = self.check_and_clean_section_number(text, font_size, font_color, font)
                                        if section_number_result["status"]:
                                            self.old_section_number = self.current_section_number
                                            self.current_section_number = section_number_result["section"]
                                            anything_found = True

                                    # check for section name
                                    if not anything_found:
                                        section_name_result = self.check_and_clean_section_name(text, font_size, font_color, font)
                                        if section_name_result["status"]:
                                            self.old_section_name = self.current_section_name
                                            self.current_section_name = section_name_result["name"]
                                            anything_found = True

                                    # check for rule number
                                    if not anything_found:
                                        rule_number_result = self.check_and_clean_rule_number(text, font_size, font_color, font)
                                        if rule_number_result["status"]:
                                            self.old_rule_number = self.current_rule_number
                                            self.current_rule_number = rule_number_result["num"]
                                            anything_found = True

                                    # check for situation number
                                    if not anything_found:
                                        situation_number_result = self.check_and_clean_situation_number(text, font_size, font_color, font)
                                        if situation_number_result["status"]:
                                            self.old_situation_number = self.current_situation_number
                                            self.current_situation_number = situation_number_result["num"]
                                            anything_found = True

                                    # check for question text
                                    if not anything_found:
                                        question_text_result = self.check_and_clean_question_text(text, font_size, font_color, font)
                                        if question_text_result["status"]:
                                            self.current_question_text = question_text_result["text"]
                                            anything_found = True

                                    if not anything_found:
                                        answer_headline_text_result = self.check_and_clean_answer_headline_text(text, font_size, font_color, font)
                                        if answer_headline_text_result["status"]:
                                            self.answer_headline_found = True

                                    if not anything_found:
                                        answer_text_result = self.check_and_clean_answer_text(text, font_size, font_color, font)
                                        if answer_text_result["status"]:
                                            self.current_answer_text = answer_text_result["text"]
                                            anything_found = True

                                    last_span = span

                                    if anything_found:
                                        if section_number_result["status"] and self.current_section_number != self.old_section_number:
                                            if current_section:
                                                if current_rule:
                                                    if current_situation:
                                                        current_rule = self.add_situation_if_needed(current_rule, current_situation)

                                                    current_section = self.add_rule_if_needed(current_section, current_rule)

                                                self.docs.append(current_section)
                                                current_rule = []
                                                current_situation = []
                                                self.answer_headline_found = False

                                            current_section = {
                                                "section_number": self.current_section_number,
                                                "section_name": None,
                                                "section_rules": []
                                            }

                                        if section_name_result["status"] and self.current_section_name != self.old_section_name:
                                            current_section["section_name"] = self.current_section_name

                                        if rule_number_result["status"] and self.current_rule_number != self.old_rule_number:
                                            if current_section and current_rule:
                                                if current_situation:
                                                    if self.current_question_text:
                                                        current_situation["question"] = self.current_question_text
                                                        self.current_question_text = ""

                                                    if self.current_answer_text:
                                                        current_situation["answer"] = self.current_answer_text
                                                        rule_references = self.extract_rule_reference_from_answer(self.current_answer_text)
                                                        if rule_references:
                                                            current_situation["rule_reference"] = rule_references
                                                        self.current_answer_text = ""

                                                    if current_rule["situations"] is None:
                                                        current_rule["situations"] = [current_situation]
                                                    else:
                                                        current_rule["situations"].append(current_situation)

                                                current_section["section_rules"].append(current_rule)
                                                current_situation = None
                                                self.answer_headline_found = False

                                            current_rule = {
                                                "rule_number": self.current_rule_number,
                                                "situations": None,
                                            }

                                        if situation_number_result["status"] and self.current_situation_number != self.old_situation_number:
                                            if current_section and current_rule and current_situation:
                                                if self.current_question_text:
                                                    current_situation["question"] = self.current_question_text
                                                    self.current_question_text = ""

                                                if self.current_answer_text:
                                                    current_situation["answer"] = self.current_answer_text
                                                    rule_references = self.extract_rule_reference_from_answer(
                                                        self.current_answer_text)
                                                    if rule_references:
                                                        current_situation["rule_reference"] = rule_references
                                                    self.current_answer_text = ""

                                                if current_rule["situations"] is None:
                                                    current_rule["situations"] = [current_situation]
                                                else:
                                                    current_rule["situations"].append(current_situation)

                                                self.answer_headline_found = False

                                            if self.current_question_text:
                                                self.current_question_text = ""

                                            current_situation = {
                                                "number": self.current_situation_number,
                                                "question": None,
                                                "answer": None,
                                                "rule_reference": None
                                            }

        if current_section and current_rule:
            if current_situation:
                if current_situation["question"] == "" or current_situation["question"] is None:
                    current_situation["question"] = self.current_question_text

                if current_situation["answer"] == "" or current_situation["answer"] is None:
                    current_situation["answer"] = self.current_answer_text
                    rule_references = self.extract_rule_reference_from_answer(self.current_answer_text)
                    if rule_references:
                        current_situation["rule_reference"] = rule_references

                current_rule = self.add_situation_if_needed(current_rule, current_situation)

            current_section = self.add_rule_if_needed(current_section, current_rule)
            self.docs.append(current_section)

        return self.docs

    @staticmethod
    def is_horizontal_text(direction):
        if direction == (1.0, 0.0):
            return True

        return False

    def has_found_section(self):
        return self.current_section_number is not None

    def check_and_clean_section_number(self, text, font_size, font_color, font):
        if font_size != self.section_number_font_size or font_color != self.section_number_font_color or self.section_number_font != font:
            return {"status": False, "section": None}

        if "SECTION" in text and text.isupper():
            return {"status": True, "section": text}

        return {"status": False, "section": None}

    def check_and_clean_section_name(self, text, font_size, font_color, font):
        if not self.has_found_section():
            return {"status": False, "name": None}

        # check for matching font-size, color and family
        if font_size != self.section_name_font_size or font_color != self.section_name_font_color or self.section_name_font != font:
            return {"status": False, "name": None}

        if text.isupper():
            return {"status": True, "name": text}

        return {"status": False, "name": None}

    def check_and_clean_rule_number(self, text, font_size, font_color, font):
        if font_size != self.rule_headline_font_size or font_color != self.rule_headline_font_color or self.rule_headline_font != font:
            return {"status": False, "num": None}

        try:
            match = re.search(r"RULE\s*(\d+)", text, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                return {"status": True, "num": num}
            else:
                return {"status": False, "num": None}
        except ValueError:
            return {"status": False, "num": None}

    def check_and_clean_situation_number(self, text, font_size, font_color, font):
        stripped_text = text.strip()

        if font_size != self.situation_number_font_size or font_color != self.situation_number_font_color or self.situation_number_font != font:
            return {"status": False, "num": None}


        match = re.search(r"SITUATION\s(\d{1,3}\.\d{1,3})", stripped_text)
        if match:
            return {"status": True, "num": match.group(1)}

        return {"status": False, "num": None}

    def check_and_clean_question_text(self, text, font_size, font_color, font):
        stripped_text = text.strip()

        if self.answer_headline_found or font_size != self.situation_question_text_font_size or font_color != self.situation_question_text_font_color or font != self.situation_question_text_font:
            return {"status": False, "text": None}

        question_text = self.current_question_text + " " + stripped_text

        # remove hyphenation
        question_text = self.remove_hyphenation(question_text)

        # remove whitespace between words with needed hyphenation in between
        question_text = self.remove_whitespace_between_words_with_hyphenation(question_text)

        return {"status": True, "text": question_text.strip()}

    def check_and_clean_answer_headline_text(self, text, font_size, font_color, font):
        stripped_text = text.strip()

        if font_size != self.situation_answer_headline_font_size or font_color != self.situation_answer_headline_font_color or font != self.situation_answer_headline_font:
            return {"status": False}

        if stripped_text.isupper() and stripped_text == "ANSWER":
            return {"status": True}

        return {"status": False}

    def check_and_clean_answer_text(self, text, font_size, font_color, font):
        stripped_text = text.strip()

        if not self.answer_headline_found or font_size != self.situation_answer_text_font_size or font_color != self.situation_answer_text_font_color or font != self.situation_answer_text_font:
            return {"status": False, "text": None}

        answer_text = self.current_answer_text + " " + stripped_text

        # remove hyphenation
        answer_text = self.remove_hyphenation(answer_text)

        # remove whitespace between words with needed hyphenation in between
        answer_text = self.remove_whitespace_between_words_with_hyphenation(answer_text)

        return {"status": True, "text": answer_text.strip()}

    def extract_rule_reference_from_answer(self, text):
        #pattern = r"Rule\s\d{1,3}(\.\d{1,3}){0,2}\.?\s?(?:\((I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\)|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)?$"
        #pattern = r"Rule\s(\d{1,3}(\.\d{1,3}){0,2}\.?\s?(?:\((I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\)|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)?)"
        #pattern = r"Rule\s(\d{1,3}(\.\d{1,3}){0,2}\.?\s?(?:\((I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\)|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)?)(?=\s|[.,;!?]|$)"
        pattern = r"Rule\s(\d{1,3}(?:\.\d{1,3}){0,2}\.?(?:\s\((?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)\))?|\s\((?:\d{1,3}(?:\.\d{1,3}){0,2})\))?(?=\s|[.,;!?)]|$)"

        matches = re.findall(pattern, text)
        if matches:
            rule_references = []
            for match in matches:
                if match.rstrip(".").strip() not in rule_references:
                    rule_references.append(match.rstrip(".").strip())

            return rule_references

        return None

    def add_rule_if_needed(self, current_section, current_rule):
        if current_rule is None:
            return current_section

        rule_number = current_rule["rule_number"]
        found = False
        for rule in current_section["section_rules"]:
            if rule_number == rule["rule_number"]:
                found = True
                break

        if not found:
            current_section["section_rules"].append(current_rule)

        return current_section

    def add_situation_if_needed(self, current_rule, current_situation):
        if current_situation is None:
            return current_rule

        if current_rule["situations"] is None:
            current_rule["situations"] = [current_situation]
            return current_rule

        situation_number = current_situation["number"]
        found = False
        for situation in current_rule["situations"]:
            if situation_number == situation["number"]:
                found = True
                break

        if not found:
            # add texts to situation since it's now finished
            if self.current_question_text:
                current_situation["question"] = self.current_question_text
                self.current_question_text = ""

            if self.current_answer_text:
                current_situation["answer"] = self.current_answer_text
                rule_references = self.extract_rule_reference_from_answer(self.current_answer_text)
                if rule_references:
                    current_situation["rule_reference"] = rule_references
                self.current_answer_text = ""

            current_rule["situations"].append(current_situation)

        return current_rule

    @staticmethod
    def remove_hyphenation(text):
        return re.sub(r"([a-zA-Z])-\s([a-zA-Z])", r"\1\2", text)

    @staticmethod
    def remove_whitespace_between_words_with_hyphenation(text):
        text = re.sub(r"([a-zA-Z])\s-\s([a-zA-Z])", r"\1-\2", text)
        text = re.sub(r"(“?[a-zA-Z]”?)\s?-\s(“?[a-zA-Z]”?)", r"\1-\2", text)
        return text


situationHandbookExtractor = SituationHandbookExtractor()
extract_pdf_path = situationHandbookExtractor.get_pdf_path()
if extract_pdf_path is not None:
    docs = situationHandbookExtractor.extract_situations_from_pdf(extract_pdf_path)

    with open(str(rulebot.data_dir) + '/json/situations/situations.json', 'w', encoding='utf-8') as f:
        json.dump(situationHandbookExtractor.docs, f, ensure_ascii=False, indent=4)

    print("\n--------------------------------------------------")
    print("Situationen wurden extrahiert und gespeichert.")