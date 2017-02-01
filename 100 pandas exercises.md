
# (Not yet) 100 pandas exercises

This is a collection of exercises that have been collected by condensing various sources like project source code and the available documentation on pandas. The goal of this collection is to offer a quick reference for both old and new users but also to provide a set of exercices for those who teach.

If you want to suggest another exercise or find an error or think you've a better way to solve some of them, feel free to open an issue or pull request at <https://github.com/deeplook/pandas-100>

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
df = pd.read_html(basic + path)
```

#### 50. Read a CSV file into a dataframe like the tables on https://www.ssa.gov/oact/babynames/limits.html (★☆☆)

```python
df = pd.read_csv(fn, names=['name', 'gender',
                            'count'])
```

#### 51. Create a new column in a data frame with the same value in all rows (★☆☆)

```python
df['year'] = 2017
```

#### 52. Merge a list of dataframes into one (★★☆)

```python
df_list = [df1, df2, df3]
df = pd.concat(df_list)
```

#### 53. Filter by one column (★★☆)

```python
girls = df[df['gender'] == 'F']
```

#### 54. Select one column of a dataframe (★☆☆)

```python
names = df['name']
```

#### 55. Select two columns of a dataframe (★★☆)

```python
names = df[['name', 'year']]
```

#### 56. Use a column as index (★★☆)

```python
by_year = df.set_index('year')
```


#### 57. Select every 20th entry of a dataframe (★☆☆)

```python
df = df[::20]
```

#### 58. Show summary of a dataframe (★☆☆)

```python
df.describe()
```

#### 59. Show all values in one column and how often they occur (★☆☆)

```python
df.values_counts()
```

#### 70. Turn a column to upper case (★★☆)

```python
def upper(s): return s.upper()

up = df['name'].apply(upper)
```

#### 71. Sum up values of one column grouped by another (★★☆)

```python
groups = names.groupby('name')['count'].apply(sum)
```

#### 72. TODO melt a dataframe?? (★★☆)

```python
pd.melt
```
df.drop


#### 73. Remove column from a dataframe CHECK (★☆☆)

```python
df.drop('name')
```

#### 80. Plot a dataframe (★★★)

```python
import matplotlib.pyplot as plt
madonna = df[df['name'] == 'Madonna']
madonna = madonna.set_index('year')
madonna.plot()
plt.show()
```


#### 99. //Add your suggested question including rating here// (★☆☆)

```python
# Author: <Your name>

# your code...
```
