# XML Parser

The XML Parser is a tool for parsing XML-encoded texts to obtain the content and speaker/author of utterances within the text.

### Inputs

The XML corpus can be provided either as a collection of text files or as an Excel/CSV table.
The loader currently supports loading a corpus from the following file types: txt, odt, docx, csv, tsv, xlsx, ods, xml

Following [Hardie (2014)](https://doi.org/10.2478/icame-2014-0004), utterances must be contained by 'u' tags and must include a 'who' attribute. Only utterances that follow this format will be included.
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

1. Upload your document files to the 'corpus_data' directory.
2. Run the cell below and use the Corpus Loader to build a corpus from your selected documents.
3. Once the corpus is built, navigate to the 'XML Parser' tab. Here, select your corpus in the dropdown and click 'Parse XML'.
4. When parsing is complete, navigate to the 'Corpus Overview' tab to export the parsed corpus.

See the [user guide](Corpus%20Loader%20User%20Guide.pdf) for detailed instructions and hover over the tooltips in the loader for simplified instructions on how to load and build the corpus.

## Notes

- The XML Parser keeps all corpus metadata but adds a metadata called 'speaker'. If there is already a metadata column called 'speaker' it will be overwritten.
- When parsing utterances, the XML Parser will skip any utterance that does not have a speaker.
- When parsing utterances, the XML Parser will remove any XML tags within the contents of the utterance.

## Demo

Click the button below to access a demo deployed on Binderhub.

[![Binder](https://binderhub.atap-binder.cloud.edu.au/badge_logo.svg)](https://binderhub.atap-binder.cloud.edu.au/v2/gh/Australian-Text-Analytics-Platform/xml-parser/main?labpath=parser.ipynb)

## Authors

  - **Hamish Croser** - [h-croser](https://github.com/h-croser)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
