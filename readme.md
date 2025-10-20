# simulation model retriever

intended to make finding models easy and select possible on some parameters.

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
- search entry with simple or no wildchars, 
activate on button or enter
- checkbox for model recursion
  - must be checked to find models within subckt 
- checkbox model
- checkbox subckt
- search result
  - simple list with found names
- extracted model with folder, file and extension

sec page
- list with found extension (with checkbox)

third page
- list with folders with checkbox

4th page
- list with models with checkbox