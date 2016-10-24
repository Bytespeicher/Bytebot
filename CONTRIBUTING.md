# Contributing
## Setup

* Fork / pull the project
	git clone; git checkout $BRANCH
* Create virtual environment
	pyvenv env
	. env/bin/activate
* Install dependencies (see [README](README.md))
	pip install -r contrib/requirements.txt
* Setup a `config.ini`
	cp config.ini{.example,}
	$EDITOR config.ini
* Start
	irc3 config.ini


## Coding Style

For the general code base, a clear style(with consideration for 
[PEP-8](https://www.python.org/dev/peps/pep-0008/) should be adopted:

### Source encoding:
* UTF-8
* every source file has a single line comment for encoding declaration at the
  top

### Indentation: 
* 4 spaces indent
* continuation lines:
  * aligned vertically to the delimiter **or**
  * with hanging indent and no arguments on the first line

### Line length and line breaks:
* maximum line-length of 79 characters
* maximum line-length of 72 characters inside doc blocks / comments
* line breaks must use Python's implied line continuation inside parentheses,
  brackets and braces if possible
* if not possible, a backslash may be used
* top level functions and classes are surrounded by two blank lines
* method declarations and class variables are surrounded by a single blank line
* logical separation with a single blank line may be used
* a semicolon must not occur to mark the end of a line
* multiple statements must not occur on the same line

### Whitespaces:
* whitespaces must not occur:
  * at the end of lines or on blank lines
  * before a comma, semicolon or colon
  * immediately inside parentheses, brackets or braces
  * immediately befor the parentheses that start an argument list for a
    function call or indexing/slicing
  * around the assignment-operator for keywords or parameters
* single whitespaces must occur:
  * around binary operators
    * assignment ( = )
    * augmented assignment ( +=, -=, /=, *= )
    * comparison ( == , < , > , != , <> , <= , >= , in , not in , is , is not )
    * boolean ( and , or , not )
    * after a colon inside lambdas, list comprehension

### Imports:
* imports must be at the top of the file
* separate imports must be on separate lines
* imports from the same module may be on a single line
* imports must be grouped by:
  * standard Python library
  * third-party libraries
  * Bytebot libraries
* imports must not use explicit relative import declarations
* imports must not use an asterisk import declaration (i.e. `from mod import *`)

### Quotes and comments:
* double quotes for all string literals
* triple quotes for comments and doc blocks
* comments must be full sentences
* inline comments should not be used
* doc strings are [PEP 257](https://www.python.org/dev/peps/pep-0257/)

### Naming:
* all identifiers must be in English
* configuration variables are all capitalized with underscores
* constants are all capitalized with underscores
* variables are all lowercase with underscores
* classes are capitalized words with no underscores
* the letters of abbreviations in class names are all capitialized
* Exception names are treated as class names
* plugin classes are all lowercase with no underscores
* module names are all lowercase and may contain underscores
* functions and class methods are all lowercase with underscores
* class methods inherited by the Twisted API are mixed case(commonly refered 
  to as "camel case")
* weak internal functions of classes are prefixed with an underscore
* class properties and methods not to be accessed externally must be prefixed
  with two underscores
* when an identifier conflicts with a Python keyword, a synonym must be used
* instance methods must use `self` as the first keyword
* class methods must use `cls` as the first keyword
