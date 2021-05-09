## My basic implementation of Series and DataFrame objects similar to those found in Pandas

### MySeries

Implements an indexed series stored as a dictionary.

Functionality:
- Accepts data as a list with optional index as a list
- Method to *print* the series
- Has methods *mean*, *min* and *max*

### MyDataFrame

Implements a basic DataFrame object with columns using MySeries objects.

Functionality:
- Accepts data as a dictionary with an optional index as a list.
- Method to *print* the DataFrame
- Method to *sort* in-place by column
- Calculates *mean*, *min* and *max* of columns
- Basic error checking
