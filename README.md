# XML Parser

The XML Parser is a tool for parsing XML-encoded texts to obtain the content and speaker/author of utterances within the text.

### Inputs

The XML corpus can be provided either as a collection of text files or as an Excel or CSV table.
The loader currently supports loading a corpus from the following file types: txt, odt, docx, csv, tsv, xlsx, ods, xml

Utterances must be contained by <u> tags and must include a 'who' attribute. Only utterances that follow this format will be included.
An example of valid utterances is as follows:

```xml
<u who="PETER">Hello, world.</u>
<u who="WORLD">Hello, Peter.</u>
<u who="PETER">Wow!</u>
```

### Output

Once a corpus has been parsed, it can be exported in one of three formats: csv, xlsx, or zip.
The zip format provides a zip file containing each utterance as a txt file, with a metadata.csv containing the corpus metadata.
The csv and xlsx formats are structured as a table where each row represents an utterance. The table for the above input example would look as follows:

| document_     | speaker |
|---------------|---------|
| Hello, world. | PETER   |
| Hello, Peter. | WORLD   |
| Wow!          | PETER   |

## Instructions

1. Upload your document files to the 'corpus_data' directory
2. Run the cell below and use the Corpus Loader to build a corpus from your selected documents
3. Once the corpus is built, navigate to the 'XML Parser' tab. Here, select your corpus in the dropdown and click 'Parse XML'
4. When parsing is complete, navigate to the 'Corpus Overview' tab to export the parsed corpus.

Click [here](Corpus Loader User Guide.pdf) for more detailed instructions for the Corpus Loader.

## Notes

- The XML Parser keeps all corpus metadata but adds a column called 'speaker'. If there is already a metadata column called 'speaker' it will be overwritten
- When parsing utterances, the XML Parser will skip any utterance that does not have a speaker

## Demo

Click the button below to access a demo deployed on Binderhub

[![Binder](https://binderhub.atap-binder.cloud.edu.au/badge_logo.svg)](https://binderhub.atap-binder.cloud.edu.au/v2/gh/Australian-Text-Analytics-Platform/xml-parser/main?labpath=parser.ipynb)

## Authors

  - **Hamish Croser** - [h-croser](https://github.com/h-croser)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
