def pre_processing(name: str, short_description_text: str, short_description_mm_text: str,
                       long_description_text: str,
                       long_description_mn_text: str, marketing_text_mm_text: str) -> str:
        text = " ".join(name) + "[SEP]"
        if type(short_description_text) == str and len(short_description_text) > 5 and short_description_text not in name:
            text += short_description_text + " [SEP] "

        if type(long_description_text) == str and len(long_description_text) > 5:
            text += long_description_text + " [SEP] "
        if type(long_description_mn_text) == str and len(long_description_mn_text) > 5:
            text += long_description_mn_text + " [SEP] "

        if type(marketing_text_mm_text) == str and len(marketing_text_mm_text) > 5 and marketing_text_mm_text not in name:
            text += marketing_text_mm_text + " [SEP] "

        return text
