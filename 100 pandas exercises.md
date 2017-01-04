
# 100 pandas exercises

This is a collection of exercises that have been collected by condensing various sources like project source code and the available documentation on pandas. The goal of this collection is to offer a quick reference for both old and new users but also to provide a set of exercices for those who teach.

If you find an error or think you've a better way to solve some of them, feel free to open an issue at <https://github.com/deeplook/pandas-100>

#### 1. Import the pandas package under the name `pd` (★☆☆)

```python
import pandas as pd
```


#### 2. Print the pandas version and a versions list of all package dependancies of pandas (★☆☆)


```python
print(pd.__version__)
pd.show_versions()
```


#### 3. Read a HTML table on a webpage like http://www.lenntech.com/periodic-chart-elements/melting-point.htm into a dataframe (★☆☆)

```python
basic = 'http://www.lenntech.com'
path = '/periodic-chart-elements/melting-point.htm'
pd.read_html(basic + path)
```


#### 99. //Add your suggested question including rating here// (★☆☆)

```python
# Author: <Your name>

# your code...
```
