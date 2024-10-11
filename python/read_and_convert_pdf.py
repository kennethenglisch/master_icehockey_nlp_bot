import os
import fitz
import json
import re

class RuleExtractor:
    def __init__(self):
        self.rules = []

        # page number: font-size=12.0, font-color:21407, font=RobotoCondensed-Bold, example=17
        self.page_number_font_size = 12.0
        self.page_number_font_color = 21407
        self.page_number_font = "RobotoCondensed-Bold"

        # section number: font-size=12.0, font-color=21407, font=RobotoCondensed-Bold, example=SECTION 01
        self.section_number_font_size = 12.0
        self.section_number_font_color = 21407
        self.section_number_font = "RobotoCondensed-Bold"

        # section name: font-size=25.744544982910156, font-color=21407, font=RobotoCondensed-Light, example=PLAYING AREA
        self.section_name_font_size = 25.744544982910156
        self.section_name_font_color = 21407
        self.section_name_font = "RobotoCondensed-Light"

        # rule headline: font-size=11.0, font-color=21407, font=RobotoCondensed-Regular, example=RULE 1
        self.rule_headline_font_size = 11.0
        self.rule_headline_font_color = 21407
        self.rule_headline_font = "RobotoCondensed-Regular"

        # subrule headline: font-size=11.0, font-color=21407, font=RobotoCondensed-Regular, example=1.1.
        self.subrule_headline_font_size = 11.0
        self.subrule_headline_font_color = 21407
        self.subrule_headline_font = "RobotoCondensed-Regular"

        # rules text: font-size=9.92471694946289, font-color=0, font=RobotoCondensed-Light, example=Games under jurisdiction of the IIHF...
        self.rule_text_font_size = 9.92471694946289
        self.rule_text_font_color = 0
        self.rule_text_font = "RobotoCondensed-Light"

        # rules text headlines: font-size=10.0, font-color=0, font=RobotoCondensed-Light, example=Games under jurisdiction of the IIHF...
        self.rule_text_headline_font_size = 10.0
        self.rule_text_headline_font_color = 0
        self.rule_text_headline_font = "RobotoCondensed-Regular"

        # appendix text: font-size=9.75, font-color=21407, font=RobotoCondensed-Regular, example=For more information refer to Appendix VI – Infographics.
        self.appendix_text_font_size = 9.75
        self.appendix_text_font_color = 21407
        self.appendix_text_font = "RobotoCondensed-Regular"

        # temp vars for rule creation
        self.current_page_number = 0
        self.current_section_number = None
        self.current_section_name = None
        self.current_rule_number = 0
        self.current_rule_name = None
        self.current_subrule_number = 0
        self.current_subrule_name = None
        self.current_rule_text = ""
        self.current_appendix_information = None

        self.old_section_number = None
        self.old_section_name = None
        self.old_rule_number = 0
        self.old_rule_name = None
        self.old_subrule_number = 0
        self.old_subrule_name = None

    def get_smallest_font_size(self):
        font_sizes = [
            self.page_number_font_size,
            self.section_number_font_size,
            self.section_name_font_size,
            self.rule_headline_font_size,
            self.subrule_headline_font_size,
            self.rule_text_font_size,
            self.appendix_text_font_size,
        ]

        return min(font_sizes)

    @staticmethod
    def get_pdf_path():
        pdf_path = input("Bitte geben Sie den Pfad zu Ihrem Regelbuch (PDF) ein oder wählen Sie eine der folgenden Optionen\nEnter oder 1 - rulebook_one_page_test.pdf\n2 - rulebook_three_page_test.pdf\n3 - rulebook_two_sections_test.pdf: ")

        if pdf_path == "" or pdf_path == "1":
            pdf_path = "../rulebook_one_page_test.pdf"

        if pdf_path == "2":
            pdf_path = "../rulebook_three_page_test.pdf"

        if pdf_path == "3":
            pdf_path = "../rulebook_two_sections_test.pdf"

        if not os.path.isfile(pdf_path):
            print("Der angegebene Pfad ist ungültig. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")
            return None

        return pdf_path

    def extract_rules_from_pdf(self, pdf_path):
        last_span = None
        old_rule_start_page = None
        new_rule_start_page = None

        current_section = []
        current_rule = []
        current_subrule = []

        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                for text in page.get_text("dict")["blocks"]:
                    if "lines" in text:
                        for line in text["lines"]:
                            if self.is_horizontal_text(self, line["dir"]):
                                for span in line["spans"]:

                                    anything_found = False # used for skipping other checks if anything found already

                                    text = span["text"]
                                    font_size = span["size"]
                                    font_color = span["color"]
                                    font = span["font"]

                                    if font_size < self.get_smallest_font_size():
                                        continue

                                    if not anything_found:
                                        # check for page number
                                        page_number_result = self.check_and_clean_page_number(text, font_size, font_color, font)
                                        if page_number_result["status"]:
                                            self.current_page_number = page_number_result["num"]
                                            anything_found = True

                                    if not anything_found:
                                        # check for section number
                                        section_number_result = self.check_and_clean_section_number(text, font_size, font_color, font)
                                        if section_number_result["status"]:
                                            self.old_section_number = self.current_section_number
                                            self.current_section_number = section_number_result["section"]
                                            anything_found = True

                                    if not anything_found:
                                        # check for section name
                                        section_name_result = self.check_and_clean_section_name(text, font_size, font_color,font)
                                        if section_name_result["status"]:
                                            self.old_section_name = self.current_section_name
                                            self.current_section_name = section_name_result["name"]
                                            anything_found = True

                                    if not anything_found:
                                        # check for rule number
                                        rule_number_result = self.check_and_clean_rule_number(text, font_size, font_color, font)
                                        if rule_number_result["status"]:
                                            self.old_rule_number = self.current_rule_number
                                            self.current_rule_number = rule_number_result["num"]
                                            anything_found = True

                                    if not anything_found:
                                        # check for rule name
                                        rule_name_result = self.check_and_clean_rule_name(text, font_size, font_color, font, last_span)
                                        if rule_name_result["status"]:
                                            self.old_rule_name = self.current_rule_name
                                            self.current_rule_name = rule_name_result["name"]
                                            anything_found = True

                                    if not anything_found:
                                        subrule_number_result = self.check_and_clean_subrule_number(text, font_size, font_color, font)
                                        if subrule_number_result["status"]:
                                            self.old_subrule_number = self.current_subrule_number
                                            self.current_subrule_number = subrule_number_result["num"]
                                            old_rule_start_page = new_rule_start_page
                                            new_rule_start_page = self.current_page_number
                                            anything_found = True

                                    if not anything_found:
                                        subrule_name_result = self.check_and_clean_subrule_name(text, font_size, font_color, font, last_span)
                                        if subrule_name_result["status"]:
                                            self.old_subrule_name = self.current_subrule_name
                                            self.current_subrule_name = subrule_name_result["name"]
                                            anything_found = True

                                    if not anything_found:
                                        rule_text_result = self.check_and_clean_rule_text(text, font_size, font_color, font, self.current_rule_text)
                                        if rule_text_result["status"]:
                                            self.current_rule_text = rule_text_result["text"]
                                            anything_found = True

                                    if not anything_found:
                                        additional_info_result = self.check_and_clean_appendix_information(text, font_size, font_color, font)
                                        if additional_info_result["status"]:
                                            self.current_appendix_information = additional_info_result["text"]
                                            anything_found = True

                                    last_span = span

                                    # check if we got a new rule or subrule
                                    if anything_found:
                                        # if self.current_rule_number == 0 or self.current_subrule_number == 0:
                                        #     continue

                                        # todo: new structure as in test.json
                                        # check for new section
                                        if section_number_result["status"] and self.current_section_number != self.old_section_number:
                                            if current_section:
                                                self.rules.append(current_section)
                                                print(current_section)

                                            # create new section and build structure
                                            current_section = {
                                                "section_number": self.current_section_number,
                                                "section_name": None,
                                                "section_rules": []
                                            }

                                        if section_name_result["status"] and self.current_section_name != self.old_section_name:
                                            # add name to section
                                            current_section["section_name"] = self.current_section_name

                                        # check for new rule
                                        if rule_number_result["status"] and self.current_rule_number != self.old_rule_number:
                                            # check if there was a rule before and close it before creating a new one
                                            if current_section and current_rule:
                                                if current_subrule:
                                                    # add rule text to rule, since it's now finished (if not already done)
                                                    if self.current_rule_text:
                                                        current_subrule["rule_text"] = self.current_rule_text
                                                        self.current_rule_text = ""
                                                    current_rule["subrules"].append(current_subrule)
                                                    current_section["section_rules"].append(current_rule)

                                                current_rule = []
                                                current_subrule = []

                                            # create new rule and build structure
                                            current_rule = {
                                                "page": self.current_page_number,
                                                "rule_number": self.current_rule_number,
                                                "rule_name": None,
                                                "subrules": []
                                            }

                                        if rule_name_result["status"] and self.current_rule_name != self.old_rule_name:
                                            # add rule name
                                            current_rule["rule_name"] = self.current_rule_name

                                        # check for new subrule
                                        if subrule_number_result["status"] and self.current_subrule_number != self.old_subrule_number:
                                            # check if there was a subrule before and close it before creating a new one
                                            if current_section and current_rule and current_subrule:
                                                # add rule text to rule, since it's now finished
                                                if self.current_rule_text:
                                                    current_subrule["rule_text"] = self.current_rule_text
                                                    self.current_rule_text = ""

                                                current_rule["subrules"].append(current_subrule)
                                                current_subrule = []

                                            # create subrule and build structure
                                            current_subrule = {
                                                "page": self.current_page_number,
                                                "subrule_number": self.current_subrule_number,
                                                "subrule_name": None,
                                                "rule_text": None,
                                                "appendix_information": None
                                            }

                                        if subrule_name_result["status"] and self.current_subrule_name != self.old_subrule_name:
                                            # add subrule name
                                            current_subrule["subrule_name"] = self.current_subrule_name

                                        if additional_info_result["status"] and self.current_appendix_information is not None:
                                            # add appendix result to subrule
                                            current_subrule["appendix_information"] = self.current_appendix_information
                                            self.current_appendix_information = None

                                        # rule_number_changed = rule_number_result["status"] and self.current_rule_number != self.old_rule_number
                                        # subrule_number_changed = subrule_number_result["status"] and self.current_subrule_number != self.old_subrule_number
                                        # rule_names_set = self.current_rule_name is not None and self.current_subrule_name is not None
                                        # rule_text_set = self.current_rule_text is not None and self.current_rule_text != ""
                                        #
                                        # if (rule_number_changed or subrule_number_changed) and rule_names_set and rule_text_set:
                                        #
                                        #     page = new_rule_start_page
                                        #     if new_rule_start_page != old_rule_start_page:
                                        #         page = old_rule_start_page
                                        #
                                        #     self.rules.append({
                                        #         "page": page,
                                        #         "section_number": self.current_section_number,
                                        #         "section_name": self.current_section_name,
                                        #         "rule_number": self.current_rule_number,
                                        #         "rule_name": self.current_rule_name,
                                        #         "subrule_number": self.old_subrule_number,
                                        #         "subrule_name": self.current_subrule_name,
                                        #         "rule_text": self.current_rule_text.strip(),
                                        #         "appendix_information": self.current_appendix_information,
                                        #     })
                                        #
                                        #     self.current_rule_text = ""
                                        #     self.current_appendix_information = None
                                        #
                                        #     if rule_number_changed:
                                        #         self.old_rule_number = self.current_rule_number
                                        #
                                        #     if subrule_number_changed:
                                        #         self.old_subrule_number = self.current_subrule_number

        # todo: need to add the last subrule to the current rule and the current section
        if current_section and current_rule and current_subrule:
            if current_subrule["rule_text"] == "" or current_subrule["rule_text"] is None:
                current_subrule["rule_text"] = self.current_rule_text

            if current_subrule["appendix_information"] != "" or current_subrule["appendix_information"] is None:
                current_subrule["appendix_information"] = self.current_appendix_information

            current_section["section_rules"][-1]["subrules"].append(current_subrule)
            self.rules.append(current_section)

        return self.rules

    @staticmethod
    def is_horizontal_text(self, direction):
        if direction == (1.0, 0.0):
            return True

        return False

    def check_and_clean_page_number(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # try to convert to integer
        try:
            num = int(stripped_text)

            # check for matching font-size, color and family
            if font_size != self.page_number_font_size or font_color != self.page_number_font_color or self.page_number_font != font_family:
                return {"status": False, "num": None}

            return {"status": True, "num": num}
        except ValueError:
            return {"status": False, "num": None}

    def check_and_clean_section_number(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.section_number_font_size or font_color != self.section_number_font_color or self.section_number_font != font_family:
            return {"status": False, "section": None}

        if "SECTION" in stripped_text and stripped_text.isupper():
            return {"status": True, "section": stripped_text}

        return {"status": False, "section": None}

    def check_and_clean_section_name(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.section_name_font_size or font_color != self.section_name_font_color or self.section_name_font != font_family:
            return {"status": False, "name": None}

        if stripped_text.isupper():
            return {"status": True, "name": stripped_text}

        return {"status": False, "name": None}

    def check_and_clean_rule_number(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.rule_headline_font_size or font_color != self.rule_headline_font_color or self.rule_headline_font != font_family:
            return {"status": False, "num": None}

        if "RULE" in stripped_text and stripped_text.isupper():
            # convert only number (everything after "RULE")
            # try to convert to integer
            try:
                num = int(stripped_text.split("RULE")[1])
                return {"status": True, "num": num}
            except ValueError:
                return {"status": False, "num": None}

        return {"status": False, "num": None}

    # re.fullmatch("^(RULE \d{1,3}|\d{1,3}\.\d{1,2}(\.\d{1,2})?)$", stripped_text)
    def check_and_clean_rule_name(self, text, font_size, font_color, font_family, last_span):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.rule_headline_font_size or font_color != self.rule_headline_font_color or self.rule_headline_font != font_family:
            return {"status": False, "name": None}

        if stripped_text.isupper() and last_span:
            # check last span
            result = self.check_and_clean_rule_number(last_span["text"], last_span["size"], last_span["color"], last_span["font"])
            if result["status"]:
                return {"status": True, "name": stripped_text}

        return {"status": False, "name": None}

    def check_and_clean_subrule_number(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.subrule_headline_font_size or font_color != self.subrule_headline_font_color or self.subrule_headline_font != font_family:
            return {"status": False, "num": None}


        if re.fullmatch("^\d{1,3}\.\d{1,2}(\.\d{1,2})?\.?$", stripped_text):
            return {"status": True, "num": stripped_text}

        return {"status": False, "num": None}

    def check_and_clean_subrule_name(self, text, font_size, font_color, font_family, last_span):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.subrule_headline_font_size or font_color != self.subrule_headline_font_color or self.subrule_headline_font != font_family:
            return {"status": False, "name": None}

        if stripped_text.isupper() and last_span:
            # check last span
            result = self.check_and_clean_subrule_number(last_span["text"], last_span["size"], last_span["color"], last_span["font"])
            if result["status"]:
                return {"status": True, "name": stripped_text}

        return {"status": False, "name": None}

    def check_and_clean_rule_text(self, text, font_size, font_color, font_family, current_rule_text):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        is_rule_text = font_size == self.rule_text_font_size and font_color == self.rule_text_font_color and self.rule_text_font == font_family
        is_rule_text_headline = font_size == self.rule_text_headline_font_size and font_color == self.rule_text_headline_font_color and self.rule_text_headline_font == font_family
        if not is_rule_text and not is_rule_text_headline:
            return {"status": False, "text": None}

        rule_text = current_rule_text + " " + stripped_text
        return {"status": True, "text": rule_text}

    def check_and_clean_appendix_information(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size != self.appendix_text_font_size or font_color != self.appendix_text_font_color or self.appendix_text_font != font_family:
            return {"status": False, "text": None}

        match = re.search(r"For more information refer to Appendix (.*?)\.", stripped_text)
        if match:
            return {"status": True, "text": match.group(1).strip()}

        return {"status": False, "text": None}

    def reset_current_variables(self):
        # temp vars for rule creation
        self.current_page_number = 0
        self.current_section_number = 0
        self.current_section_name = None
        self.current_rule_number = 0
        self.current_rule_name = None
        self.current_subrule_number = 0
        self.current_subrule_name = None
        self.current_rule_text = ""

rule_extractor = RuleExtractor()
extract_pdf_path = rule_extractor.get_pdf_path()
if extract_pdf_path is not None:
    rules = rule_extractor.extract_rules_from_pdf(extract_pdf_path)

    # Speichere die erfassten Regeln im JSON-Format
    with open('rules.json', 'w', encoding='utf-8') as f:
        json.dump(rule_extractor.rules, f, ensure_ascii=False, indent=4)

    print("\n--------------------------------------------------")
    print("Regeln wurden extrahiert und gespeichert.")