import logging
import traceback

import panel as pn
from atap_corpus._types import TCorpora
from atap_corpus.corpus.corpus import DataFrameCorpus
from atap_corpus_loader import CorpusLoader
from pandas import DataFrame, Series
from panel.widgets import Select, Button


class Parser(pn.viewable.Viewer):
    def log(self, msg: str, level: int):
        logger = logging.getLogger(self.logger_name)
        logger.log(level, msg)

    def __init__(self, corpus_loader: CorpusLoader, logger_name: str, **params):
        super().__init__(**params)
        self.corpus_loader: CorpusLoader = corpus_loader
        self.logger_name: str = logger_name
        self.corpora: TCorpora = self.corpus_loader.get_mutable_corpora()

        self.corpus_selector = Select(name="Selected corpus")
        self.parse_corpus_button = Button(name="Parse XML", button_style='solid', button_type='primary')
        self.controls = pn.Column(
            self.corpus_selector,
            self.parse_corpus_button
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
        while new_name not in existing_names:
            new_name = f"{prev_name}-parsed.{i}"
            i += 1

        return new_name

    def parse_corpus(self, *_):
        try:
            if self.corpus_selector.value is None:
                return

            corpus: DataFrameCorpus = self.corpus_selector.value
            corpus_df: DataFrame = corpus.to_dataframe()
            doc_col = corpus._COL_DOC
            parsed_df = corpus_df.apply(self._parse_xml, axis=1, args=(doc_col,))

            new_name: str = self._get_new_corpus_name(corpus.name)
            new_corpus: DataFrameCorpus = DataFrameCorpus.from_dataframe(parsed_df, col_doc=doc_col, name=new_name)
            self.corpora.add(new_corpus)
        except Exception as e:
            self.log(str(traceback.format_exc()), logging.DEBUG)
            return
    
        self.display_success(f"XML parsed successfully. Parsed corpus: {new_corpus.name}")

    def _parse_xml(self, row: Series, doc_col: str) -> Series:
        
