import os
import fitz
import json
import re

# todo: maybe highlight bold text with <b> or something else
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
        self.rule_headline_font_sizes = [11.0, 10.754817008972168]
        self.rule_headline_font_color = 21407
        self.rule_headline_font = "RobotoCondensed-Regular"

        # subrule headline: font-size=11.0, font-color=21407, font=RobotoCondensed-Regular, example=1.1.
        # font size can also be: 11.109999656677246
        self.subrule_headline_font_sizes = [11.0, 11.109999656677246, 10.754817008972168]
        self.subrule_headline_font_color = 21407
        self.subrule_headline_font = "RobotoCondensed-Regular"

        # rules text: font-size=9.92471694946289, font-color=0, font=RobotoCondensed-Light, example=Games under jurisdiction of the IIHF...
        self.rule_text_font_sizes = [9.92471694946289, 10.023963928222656, 9.703460693359375]
        self.rule_text_font_color = 0
        self.rule_text_fonts = ["RobotoCondensed-Light", "RobotoCondensed-Regular"] # regular für römische Ziffern

        # rules text headlines: font-size=10.0, font-color=0, font=RobotoCondensed-Light, example=Games under jurisdiction of the IIHF...
        self.rule_text_headline_font_size = 10.0
        self.rule_text_headline_font_color = 0
        self.rule_text_headline_font = "RobotoCondensed-Regular"

        # appendix text: font-size=9.75, font-color=21407, font=RobotoCondensed-Regular, example=For more information refer to Appendix VI – Infographics.
        self.appendix_text_font_sizes = [9.75, 10.100000381469727]
        self.appendix_text_font_color = 21407
        self.appendix_text_font = "RobotoCondensed-Regular"

        # appendix text: font-size=9.75, font-color=21407, font=RobotoCondensed-Regular, example=For more information refer to Appendix VI – Infographics.
        self.rule_reference_text_font_sizes = [9.75, 10.100000381469727, 9.53267765045166, 9.676623344421387, 9.848857879638672, 9.92471694946289]
        self.rule_reference_text_font_color = 21407
        self.rule_reference_text_font_color_alternative = 2251163
        self.rule_reference_text_fonts = ["RobotoCondensed-Regular", "RobotoCondensed-Light"]

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
        self.current_rule_reference = None

        self.old_section_number = None
        self.old_section_name = None
        self.old_rule_number = 0
        self.old_rule_name = None
        self.old_subrule_number = 0
        self.old_subrule_name = None

    def get_smallest_font_size(self):
        font_sizes = {
            self.page_number_font_size,
            self.section_number_font_size,
            self.section_name_font_size,
        }

        for size in self.rule_text_font_sizes:
            font_sizes.add(size)

        for size in self.rule_headline_font_sizes:
            font_sizes.add(size)

        for size in self.subrule_headline_font_sizes:
            font_sizes.add(size)

        for size in self.rule_reference_text_font_sizes:
            font_sizes.add(size)

        for sizes in self.appendix_text_font_sizes:
            font_sizes.add(sizes)

        return min(font_sizes)

    def get_greatest_font_size(self):
        font_sizes = {
            self.page_number_font_size,
            self.section_number_font_size,
            self.section_name_font_size,
        }

        for size in self.rule_text_font_sizes:
            font_sizes.add(size)

        for size in self.rule_headline_font_sizes:
            font_sizes.add(size)

        for size in self.subrule_headline_font_sizes:
            font_sizes.add(size)

        for size in self.rule_reference_text_font_sizes:
            font_sizes.add(size)

        for sizes in self.appendix_text_font_sizes:
            font_sizes.add(sizes)

        return max(font_sizes)

    @staticmethod
    def get_pdf_path():
        pdf_path = input("Bitte geben Sie den Pfad zu Ihrem Regelbuch (PDF) ein oder wählen Sie eine der folgenden Optionen\n1 - rulebook_one_page_test.pdf\n2 - rulebook_three_page_test.pdf\n3 - rulebook_two_sections_test.pdf\n4 - rulebook_three_sections_test.pdf\nEnter oder 5 - 2024_iihf_rulebook_24052024_v1.pdf\n----------------\nDeine Auswahl: ")

        if pdf_path == "1":
            pdf_path = "../../data/pdf/rulebook_one_page_test.pdf"

        if pdf_path == "2":
            pdf_path = "../../data/pdf/rulebook_three_page_test.pdf"

        if pdf_path == "3":
            pdf_path = "../../data/pdf/rulebook_two_sections_test.pdf"

        if pdf_path == "4":
            pdf_path = "../../data/pdf/rulebook_three_sections_test.pdf"

        if pdf_path == "" or pdf_path == "5":
            pdf_path = "../../data/pdf/2024_iihf_rulebook_24052024_v1.pdf"

        if not os.path.isfile(pdf_path):
            print("Der angegebene Pfad ist ungültig. Bitte überprüfen Sie den Pfad und versuchen Sie es erneut.")
            return None

        return pdf_path

    def extract_rules_from_pdf(self, pdf_path):
        break_all = False
        last_span = None

        current_section = []
        current_rule = []
        current_subrule = []

        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                for page_text in page.get_text("dict", None, None, None, True)["blocks"]:
                    if "lines" in page_text:
                        for line in page_text["lines"]:
                            if self.is_horizontal_text(self, line["dir"]):
                                for span in line["spans"]:

                                    anything_found = False # used for skipping other checks if anything found already

                                    text = span["text"]
                                    font_size = span["size"]
                                    font_color = span["color"]
                                    font = span["font"]

                                    # used to remove unnecessary information
                                    if "»" in text or text == " ":
                                        last_span = span

                                    if font_size < self.get_smallest_font_size() or font_size > self.get_greatest_font_size():
                                        continue

                                    # if we have found an "APPENDIX" that is a section, we can skip every page from now on and finish the extracting
                                    if "APPENDIX" in text and self.has_found_section():
                                        result = self.check_and_clean_section_number(text, font_size, font_color,font)
                                        if not result["status"] and "appendix" in result and result["appendix"]:
                                            break_all = True
                                            break

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
                                            anything_found = True

                                    if not anything_found:
                                        subrule_name_result = self.check_and_clean_subrule_name(text, font_size, font_color, font, last_span)
                                        if subrule_name_result["status"]:
                                            self.old_subrule_name = self.current_subrule_name
                                            self.current_subrule_name = subrule_name_result["name"]
                                            anything_found = True

                                    if not anything_found:
                                        rule_text_result = self.check_and_clean_rule_text(text, font_size, font_color, font, self.current_rule_text, last_span)
                                        if rule_text_result["status"]:
                                            self.current_rule_text = rule_text_result["text"]
                                            anything_found = True

                                    if not anything_found:
                                        additional_info_result = self.check_and_clean_appendix_information(text, font_size, font_color, font)
                                        if additional_info_result["status"]:
                                            self.current_appendix_information = additional_info_result["text"]
                                            anything_found = True

                                    if not anything_found:
                                        rule_reference_result = self.check_and_clean_rule_reference(text, font_size, font_color, font, current_subrule)
                                        if rule_reference_result["status"]:
                                            self.current_rule_reference = rule_reference_result["text"]
                                            anything_found = True

                                    last_span = span

                                    # check if we got a new rule or subrule
                                    if anything_found:
                                        # todo: new structure as in test.json
                                        # check for new section
                                        if section_number_result["status"] and self.current_section_number != self.old_section_number:
                                            if current_section:
                                                if current_rule:
                                                    if current_subrule:
                                                        current_rule = self.add_subrule_if_needed(current_rule, current_subrule)
                                                    else:
                                                        if current_rule["rule_text"] == "" or current_rule["rule_text"] is None:
                                                            current_rule["rule_text"] = self.current_rule_text

                                                    current_section = self.add_rule_if_needed(current_section, current_rule)
                                                self.rules.append(current_section)
                                                current_rule = []
                                                current_subrule = []

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

                                                # case if rule does not has subrules -> check if rule_text is not "" or None and write to rule itself + append
                                                else:
                                                    if self.current_rule_text:
                                                        current_rule["rule_text"] = self.current_rule_text
                                                        self.current_rule_text = ""
                                                        current_section["section_rules"].append(current_rule)

                                                current_rule = []
                                                current_subrule = []

                                            # create new rule and build structure
                                            current_rule = {
                                                "page": self.current_page_number,
                                                "rule_number": self.current_rule_number,
                                                "rule_name": None,
                                                "rule_text": None,
                                                "appendix_information": None,
                                                "rule_reference": None,
                                                "subrules": [],
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

                                            if self.current_rule_text:
                                                self.current_rule_text = ""

                                            # create subrule and build structure
                                            current_subrule = {
                                                "page": self.current_page_number,
                                                "subrule_number": self.current_subrule_number,
                                                "subrule_name": None,
                                                "rule_text": None,
                                                "appendix_information": None,
                                                "rule_reference": None
                                            }

                                        if subrule_name_result["status"] and self.current_subrule_name != self.old_subrule_name:
                                            # add subrule name
                                            if current_subrule:
                                                if current_subrule["subrule_name"] is None:
                                                    current_subrule["subrule_name"] = self.current_subrule_name
                                                else:
                                                    current_subrule["subrule_name"] += " " + str(self.current_subrule_name)
                                            else:
                                                print("Error: no current_subrule", self.current_subrule_name, self.current_page_number)

                                        if additional_info_result["status"] and self.current_appendix_information is not None:
                                            # add appendix result to subrule or rule
                                            if not current_subrule:
                                                current_rule["appendix_information"] = self.add_appendix_information_to_subrule(current_rule)
                                            else:
                                                current_subrule["appendix_information"] = self.add_appendix_information_to_subrule(current_subrule)

                                            self.current_appendix_information = None

                                        if rule_reference_result["status"] and self.current_rule_reference is not None:
                                            # add rule reference to subrule
                                            current_subrule["rule_reference"] = self.add_rule_reference_to_subrule(current_subrule)
                                            self.current_rule_reference = None

                            if break_all:
                                break

                    if break_all:
                        break

                if break_all:
                    break

        if current_section and current_rule:
            if current_subrule:
                if current_subrule["rule_text"] == "" or current_subrule["rule_text"] is None:
                    current_subrule["rule_text"] = self.current_rule_text

                current_subrule["appendix_information"] = self.add_appendix_information_to_subrule(current_subrule)
                current_subrule["rule_reference"] = self.add_rule_reference_to_subrule(current_subrule, True)

                current_rule = self.add_subrule_if_needed(current_rule, current_subrule)
            else:
                if current_rule["rule_text"] == "" or current_rule["rule_text"] is None:
                    current_rule["rule_text"] = self.current_rule_text

            current_section = self.add_rule_if_needed(current_section, current_rule)
            self.rules.append(current_section)

        return self.rules

    @staticmethod
    def is_horizontal_text(self, direction):
        if direction == (1.0, 0.0):
            return True

        return False

    def has_found_section(self):
        return self.current_section_number is not None

    def has_found_rule(self):
        return self.current_rule_number != 0

    def has_found_subrule(self):
        return self.current_subrule_number != 0

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

        if "APPENDIX" in stripped_text and stripped_text.isupper():
            return {"status": False, "appendix": True}

        return {"status": False, "section": None}

    def check_and_clean_section_name(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        if not self.has_found_section():
            return {"status": False, "name": None}

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
        if font_size not in self.rule_headline_font_sizes or font_color != self.rule_headline_font_color or self.rule_headline_font != font_family:
            return {"status": False, "num": None}

        try:
            # convert only number (after "RULE")
            match = re.search(r"RULE\s*(\d+)", stripped_text, re.IGNORECASE)
            if match:
                num = int(match.group(1)) # cast to int
                return {"status": True, "num": num}
            else:
                return {"status": False, "num": None}
        except ValueError:
            return {"status": False, "num": None}

    # re.fullmatch("^(RULE \d{1,3}|\d{1,3}\.\d{1,2}(\.\d{1,2})?)$", stripped_text)
    def check_and_clean_rule_name(self, text, font_size, font_color, font_family, last_span):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size not in self.rule_headline_font_sizes or font_color != self.rule_headline_font_color or self.rule_headline_font != font_family:
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
        if font_size not in self.subrule_headline_font_sizes or font_color != self.subrule_headline_font_color or self.subrule_headline_font != font_family:
            return {"status": False, "num": None}

        if re.fullmatch("^\d{1,3}\.\d{1,2}(\.\d{1,2})?\.?$", stripped_text):
            return {"status": True, "num": stripped_text}

        return {"status": False, "num": None}

    def check_and_clean_subrule_name(self, text, font_size, font_color, font_family, last_span):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        if font_size not in self.subrule_headline_font_sizes or font_color != self.subrule_headline_font_color or self.subrule_headline_font != font_family:
            return {"status": False, "name": None}

        if stripped_text.isupper() and last_span:
            # check last span
            subrule_number_before = self.check_and_clean_subrule_number(last_span["text"], last_span["size"], last_span["color"], last_span["font"])
            subrule_name_not_finished = last_span["text"].endswith(" ")

            if subrule_number_before["status"] or subrule_name_not_finished:
                return {"status": True, "name": stripped_text}

        return {"status": False, "name": None}

    def check_and_clean_rule_text(self, text, font_size, font_color, font_family, current_rule_text, last_span):
        # strip text for white spaces
        stripped_text = text.strip()

        # check for matching font-size, color and family
        is_rule_text = font_size in self.rule_text_font_sizes and font_color == self.rule_text_font_color and font_family in self.rule_text_fonts
        is_rule_text_headline = font_size == self.rule_text_headline_font_size and font_color == self.rule_text_headline_font_color and self.rule_text_headline_font == font_family

        # check for text in between rule references
        is_text_between_rule_references = font_size in self.rule_reference_text_font_sizes and font_color == self.rule_text_font_color and font_family in self.rule_text_fonts

        if not is_rule_text and not is_rule_text_headline and not is_text_between_rule_references:
            return {"status": False, "text": None}

        if "»" in last_span["text"] or last_span["text"] == " " and "For more information refer to" in stripped_text:
            stripped_text = "( » " + stripped_text + ")"

        if stripped_text.startswith(")"):
            rule_text = current_rule_text + stripped_text
        else:
            rule_text = current_rule_text + " " + stripped_text

        # remove hyphenation
        rule_text = self.remove_hyphenation(rule_text)

        # remove whitespace between words with needed hyphenation in between
        rule_text = self.remove_whitespace_between_words_with_hyphenation(rule_text)

        return {"status": True, "text": rule_text.strip()}

    def check_and_clean_appendix_information(self, text, font_size, font_color, font_family):
        # strip text for white spaces
        stripped_text = text.strip()

        # if not self.has_found_rule():
        #     return {"status": False, "name": None}

        # check for matching font-size, color and family
        if font_size not in self.appendix_text_font_sizes or font_color != self.appendix_text_font_color or self.appendix_text_font != font_family:
            return {"status": False, "text": None}

        match = re.search(r"refer to Appendix (.*?)(?:\.|$)", stripped_text)
        if match:
            return {"status": True, "text": match.group(1).strip()}

        return {"status": False, "text": None}

    def check_and_clean_rule_reference(self, text, font_size, font_color, font_family, current_subrule):
        # strip text for white spaces, remove quotation marks and commas
        stripped_text = text.strip().replace("\"", "").rstrip(",")

        # check for matching font-size, color and family
        is_font_size = font_size in self.rule_reference_text_font_sizes
        is_font_color = font_color == self.rule_reference_text_font_color or font_color == self.rule_reference_text_font_color_alternative
        is_font_family = font_family in self.rule_reference_text_fonts

        if stripped_text != "" and is_font_size and is_font_color and is_font_family:
            # match = re.search(r"Rule \d{1,3}(\.\d{1,2})*\.?\s*[-–]", stripped_text)
            match = re.search(r"Rules? \d{1,3}(\.\d{1,2})*\.?\s*([-–]\s*.+)?", stripped_text)
            if match:
                if stripped_text.startswith("Rules"):
                    stripped_text = stripped_text.replace("Rules", "Rule", 1)

                return {"status": True, "text": stripped_text.rstrip(".")}
            else:
                if self.has_found_section():
                    # add this part to the last one and later check if they start the same and overwrite them in rule_reference
                    if stripped_text != "–" and stripped_text != "-":
                        if stripped_text == "Rule":
                            return {"status": True, "text": stripped_text}

                        if current_subrule and current_subrule["rule_reference"]:
                            reference = current_subrule["rule_reference"][len(current_subrule["rule_reference"]) - 1]
                            if "-" in reference or "–" in reference:
                                if reference.endswith(" "):
                                    reference += stripped_text
                                else:
                                    reference += " " + stripped_text
                            else:
                                if stripped_text[0].isdigit():
                                    if reference.endswith(" "):
                                        reference += stripped_text
                                    else:
                                        reference += " " + stripped_text
                                else:
                                    if reference.endswith(" "):
                                        reference += "– " + stripped_text
                                    else:
                                        reference += " – " + stripped_text

                            # remove hyphenation
                            reference = self.remove_hyphenation(reference)
                            current_subrule["rule_reference"][len(current_subrule["rule_reference"]) - 1] = reference.rstrip(".")
                        else:
                            print("ERROR:",stripped_text, self.current_page_number)

        return {"status": False, "text": None}

    def add_appendix_information_to_subrule(self, current_subrule):
        if self.current_appendix_information is None or self.current_appendix_information == "":
            return current_subrule["appendix_information"]

        if current_subrule["appendix_information"] is None:
            return [self.current_appendix_information]

        found = False
        for information in current_subrule["appendix_information"]:
            if information == self.current_appendix_information:
                found = True
                break

        if not found:
            current_subrule_appendix_information = current_subrule["appendix_information"]
            current_subrule_appendix_information.append(self.current_appendix_information)
            return current_subrule_appendix_information

        return current_subrule["appendix_information"]

    def add_rule_reference_to_subrule(self, current_subrule, last = False):
        if self.current_rule_reference is None or self.current_rule_reference == "":
            return current_subrule["rule_reference"]

        if current_subrule["rule_reference"] is None:
            self.current_rule_text += " {rule_reference_0}" # add rule reference placeholder also for first reference
            return [self.current_rule_reference]

        found = False
        rule_reference_index = 0
        for index, reference in enumerate(current_subrule["rule_reference"]):
            if reference == self.current_rule_reference or reference.split("–")[0].strip() == self.current_rule_reference.split("–")[0].strip():
                found = True
                rule_reference_index = index
                break

        if not found:
            current_subrule_rule_reference = current_subrule["rule_reference"]
            current_subrule_rule_reference.append(self.current_rule_reference)

            # add placeholder for rule reference to rule text
            rule_reference_index = len(current_subrule_rule_reference) - 1
            self.current_rule_text += " {rule_reference_" + str(rule_reference_index) + "}"

            return current_subrule_rule_reference
        else:
            # add placeholder for rule reference to rule text
            self.current_rule_text += " {rule_reference_" + str(rule_reference_index) + "}"

        return current_subrule["rule_reference"]

    def add_subrule_if_needed(self, current_rule, current_subrule):
        if current_subrule is None:
            return current_rule

        subrule_number = current_subrule["subrule_number"]
        found = False
        for subrule in current_rule["subrules"]:
            if subrule_number == subrule["subrule_number"]:
                found = True
                break

        if not found:
            # add rule text to rule, since it's now finished (if not already done)
            if self.current_rule_text:
                current_subrule["rule_text"] = self.current_rule_text
                self.current_rule_text = ""

            current_rule["subrules"].append(current_subrule)

        return current_rule

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

    @staticmethod
    def remove_hyphenation(text):
        return re.sub(r"([a-zA-Z])-\s([a-zA-Z])", r"\1\2", text)

    @staticmethod
    def remove_whitespace_between_words_with_hyphenation(text):
        text = re.sub(r"([a-zA-Z])\s-\s([a-zA-Z])", r"\1-\2", text)
        text = re.sub(r"(“?[a-zA-Z]”?)\s?-\s(“?[a-zA-Z]”?)", r"\1-\2", text)
        return text

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

    with open('../../data/json/rules/rules.json', 'w', encoding='utf-8') as f:
        json.dump(rule_extractor.rules, f, ensure_ascii=False, indent=4)

    print("\n--------------------------------------------------")
    print("Regeln wurden extrahiert und gespeichert.")