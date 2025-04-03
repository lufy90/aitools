
for getting person information from we_chat

## how to
```
python get_person.py <person_name>
```

## Using tessdata to ocr

```
## this not work well, cannot get right text
## this would generate output.txt, inside with text it detected
TESSDATA_PREFIX=./tessdata/ tesseract cards/<person_name>.png output -l chi_sim
```

## tesseract

data:

https://github.com/tesseract-ocr/tessdata_best
