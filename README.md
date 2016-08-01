Learn Issue Categorization
---

## Up and running

1. Make sure you're using Python 2.7.
   a. An easy way to make sure you're running the right version is to use
       `virtualenv`
   b. First run `virtualenv ~/Virtualenvs/issue-categorizer -p python2`
   c. Then run `source ~/Virtualenvs/bin/activate`
2. Install the dependencies: `pip install -r requirements.txt`
3. Create the database: `createdb issue_categorization`
4. Seed the database: `python seed.py`
5. Run the application: `python categorization.py`

## LICENSE

Copyright (c) 2016 The Flatiron School

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
