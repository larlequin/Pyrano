% PYRANO 
% G.T. Vallet
% 2013/03/01

Pyrano offers a simple GUI (Graphical User Interface) to run ANOVA (analysis of variance) using [R](www.rcran.org). 
All experimental designs can be tested with only between, or within or mixed factors ANOVA. 
If reaction times are recorded, you can choose to filter lowest and/or highest values as well as defining a number of standard deviations to keep the values in.
You can also compute ANOVA on correct response rate if your data set has a column indicating what is a good and bad response.


## Getting started

### Data  

First of all, you need to load a data set into the software. To do so, go to the Data tab and click on the "..." button. Then select a text or csv file. At this point, Pyrano could only open this type of files. If you have an Excel file (.xls), you can export your data as a csv file using the 'Save as' option of Excel (or any spreadsheet application).

Data set should be composed of raw records in "long format" where each line correspond to a trial. File should have a subject column (or another wid variable), at least one independent variable and one dependent variable. Here is an example with different subjects indicated in the first column ('Subjects'), two independent variables ('V1' with 2 levels and 'V2' with 3 levels), a dependent variable  ('DV') as reaction times and a column to indicate whether the response made by the participant was correct or not.

    +----------+-----+-----+--------+------+
    | Subjects | V1  | V2  | DV     | Corr |
    +==========+=====+=====+========+======+
    | 1        | A   | A   | 356.75 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | A   | A   | 420.63 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | A   | B   | 397.02 | 0    |
    +----------+-----+-----+--------+------+
    | 1        | A   | B   | 415.15 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | A   | C   | 489.65 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | A   | C   | 603.98 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | A   | C   | 366.86 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | B   | A   | 387.42 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | B   | A   | 442.36 | 0    |
    +----------+-----+-----+--------+------+
    | 1        | B   | B   | 410.41 | 1    |
    +----------+-----+-----+--------+------+
    | 1        | B   | B   | 463.17 | 1    |
    +----------+-----+-----+--------+------+
    | ...      | ... | ... | ...    | ...  |
    +----------+-----+-----+--------+------+

You can view your data set by clicking on the "View data" button located in the Summary tab.

**Options:**  

- *Delimiter:* specify what character is used to delimiter each column of your file. Default is ";".
- *Lines to skip:* define how many lines should be skipped to read the data (e.g. the header before the variable's names). Default is 0.
- *Correct responses:* define the column name where to find the correct/incorrect response code (1 for correct, 0 for incorrect). This option leads to automatically compute an ANOVA on correct response rates.

### Variables

Once data loaded, you need to define the experimental variables to run the ANOVA. Click on the Variables tab and then select the variable names needed. At least, the subject column (or another wid variable), the dependent variable and one between or one within factor should be provided. 

**Note:** You can select multiple variables but make sure to select only one for the subject and one dependent variable. Even if you select multiple names for these two variables, only the first one (by order of appearance) will be used. 

### Filtering reaction times values

If your experiment involves to record reaction times (RT), you might want to filter extreme values to increase the reliability of the ANOVA. Click on the RT Filter tab and there you can choose to filter RT based on predefined extreme values and/or by values outside some standard deviation of the mean.

- **Extreme values:** this option leads to remove all the RT values (as indicated by the dependent variable) below and/or above the provided value.
- **Standard deviation:** this option will compute the mean and standard deviation per experimental condition. Then it will remove all RT values below and above the number of provided standard deviations.


## The results

To run the ANOVA, go to the Summary tab. There, you can check the different parameter chosen and run the ANOVA. Once the button pushed, and if the software can compute it, one or two new windows will appear displaying the results. The dependent variable window gives the results for the selected dependent variable, and if the correct response column is defined, the second window will give the correct response rates results.

In each window, the **ANOVA** results are first provided with:

1) the main ANOVA with all the effects, degree of freedom of the numerator (DFn), of the denominator (DFd), the F value, p value, if the p is significant (at .05) and the power (eta square, general for within design, partial for between design).
2) the sphericity test of Mauchly (for within design)
3) the corrected ANOVA 

Then, the **descriptive statistics** are indicated for each condition with :

1) the number of observation (N)
2) mean of the dependent variable
3) norm of the DV (for within design)
4) standard deviation of the DV
5) standard error of the DV corrected for the within design using ....
6) confidence intervals at 95% corrected for the within design 


## Dependencies

### Python/GUI

- python 2.7 or  higher 2.x
- pyQT 4.x

### R

- working R installation
- plyr package


## Licence

Pyrano is under the GPL v3 licence. Please read the licence text before using it. Thanks!