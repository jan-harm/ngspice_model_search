# simulation model retriever

intended to make finding models easy.

targets
- search thru all text files and remember the extension.
- find .model and .subckt be aware of nesting
- with models mark the type (NMOS, NPN etc. and allow for exclusion)
- mark folder (allow for exclusion)
- mark extensions (allow for exclusion)
- no speed target
- try to keep comment before subckt (* only)
  - in most cases the comment is direct before the subckt or model

views:

first page
- search entry with no wildchars (empty search all, literal string if found in name, bss finds BSS170 etc.) 
activate on button or enter, clear clears all searches
- checkbox for model recursion
  - must be checked to find models within .subckt 
- checkbox model (look for .model)
- checkbox subckt (look for .subckt)
- search result
  - simple list with found names
- extracted model with folder, file and extension

sec page
- list with found models (PNP, D etc), uncheck to repeat search without model.


third page
- file extension (uncheck to skip in next search) checkbox)

third page
- list with all files found (uncheck to skip file or clear when changing folder list)

fourth page
- list with folders with checkbox
