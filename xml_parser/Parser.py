import logging
import traceback

import panel as pn
from atap_corpus._types import TCorpora
from atap_corpus.corpus.corpus import DataFrameCorpus
from atap_corpus_loader import CorpusLoader
from pandas import DataFrame
from panel.widgets import Select, Button, Tqdm
from regex import regex, Pattern, Match


class Parser(pn.viewable.Viewer):
    WHOLE_UTTERANCE_PATTERN: Pattern = regex.compile(r"<u.*</u>", cache_pattern=True)
    UTTERANCE_TEXT_PATTERN: Pattern = regex.compile(r"(?<=<u.*>).*(?=</u>)", cache_pattern=True)
    SPEAKER_PATTERN: Pattern = regex.compile(r"(?<=<u\s+who=\")([^\"]+)(?=\")", cache_pattern=True)
    XML_TAG_PATTERN: Pattern = regex.compile(r"<[^>]+>", cache_pattern=True)

    SPEAKER_COL: str = 'speaker'

    def log(self, msg: str, level: int):
        logger = logging.getLogger(self.logger_name)
        logger.log(level, msg)

    def __init__(self, corpus_loader: CorpusLoader, logger_name: str, **params):
        super().__init__(**params)
        self.corpus_loader: CorpusLoader = corpus_loader
        self.logger_name: str = logger_name
        self.corpora: TCorpora = self.corpus_loader.get_mutable_corpora()

        self.tqdm_obj = Tqdm(visible=False)

        self.corpus_selector = Select(name="Selected corpus")
        self.parse_corpus_button = Button(name="Parse XML", button_style='solid', button_type='primary')
        self.controls = pn.Column(
            self.corpus_selector,
            self.parse_corpus_button,
            self.tqdm_obj
        )

        self.panel = pn.Row(
            self.controls,
            sizing_mode='stretch_width'
        )

        self.parse_corpus_button.on_click(self.parse_corpus)

        self.corpus_loader.register_event_callback("build", self._update_corpus_list)
        self.corpus_loader.register_event_callback("rename", self._update_corpus_list)
        self.corpus_loader.register_event_callback("delete", self._update_corpus_list)

    def __panel__(self):
        return self.panel.servable()

    def display_error(self, error_msg: str):
        self.log(f"Error displayed: {error_msg}", logging.DEBUG)
        pn.state.notifications.error(error_msg, duration=0)

    def display_success(self, success_msg: str):
        self.log(f"Success displayed: {success_msg}", logging.DEBUG)
        pn.state.notifications.success(success_msg, duration=3000)

    def _update_corpus_list(self, *_):
        corpus_options: dict[str, DataFrameCorpus] = self.corpus_loader.get_corpora()
        self.corpus_selector.options = corpus_options
        if len(corpus_options):
            self.corpus_selector.value = list(corpus_options.values())[-1]

    def _get_new_corpus_name(self, prev_name: str) -> str:
        existing_names: list[str] = [name for name, value in self.corpus_loader.get_corpora().items()]

        new_name: str = f"{prev_name}-parsed.0"
        i = 1
        while new_name in existing_names:
            new_name = f"{prev_name}-parsed.{i}"
            i += 1

        return new_name

    def parse_corpus(self, *_):
        self.tqdm_obj.visible = True
        try:
            if self.corpus_selector.value is None:
                return

            corpus: DataFrameCorpus = self.corpus_selector.value
            corpus_df: DataFrame = corpus.to_dataframe()
            expected_cols = list(corpus_df.columns) + [self.SPEAKER_COL]
            doc_col = corpus._COL_DOC

            dict_df: list[dict] = corpus_df.to_dict(orient='records')
            result_dicts = []
            for dict_row in self.tqdm_obj(dict_df, desc="Parsing files", unit="documents"):
                result_dicts.append(self._parse_xml_row(dict_row, doc_col))
            flattened = [item for sublist in result_dicts for item in sublist]

            parsed_df = DataFrame(flattened, columns=expected_cols)

            new_name: str = self._get_new_corpus_name(corpus.name)
            new_corpus: DataFrameCorpus = DataFrameCorpus.from_dataframe(parsed_df, col_doc=doc_col, name=new_name)
            self.corpora.add(new_corpus)
            self._update_corpus_list()
        except Exception as e:
            self.tqdm_obj.visible = False
            self.log(str(traceback.format_exc()), logging.DEBUG)
            return

        self.tqdm_obj.visible = False
        self.display_success(f"XML parsed successfully. Parsed corpus: {new_corpus.name}")

    def _parse_xml_row(self, row: dict, doc_col: str) -> list[dict]:
        new_data: list[dict] = []

        doc_text: str = str(row[doc_col])
        match: Match
        for match in regex.finditer(self.WHOLE_UTTERANCE_PATTERN, doc_text):
            row_data = row.copy()

            utterance: str = match.group()
            speaker: str = self._retrieve_speaker(utterance)
            if len(speaker) == 0:
                continue

            utterance_text: str = self._remove_xml_tags(utterance)

            row_data[doc_col] = utterance_text
            row_data[self.SPEAKER_COL] = speaker

            new_data.append(row_data)

        return new_data

    @staticmethod
    def _retrieve_speaker(text: str) -> str:
        match = regex.search(Parser.SPEAKER_PATTERN, text)
        if match:
            return match.group()
        else:
            return ''

    @staticmethod
    def _remove_xml_tags(text: str) -> str:
        return regex.sub(r'<[^>]+>', '', text)
