# STAT 440 Statistical Data Management - Fall 2021
## Week02 Practice Lab00
### Only the driver should submit this assignment into their individual student repo. Save the filename as lab00-week02-wed-netID.Rmd. Then render this file to .html when completed.

**#1** Using Markdown syntax, make a numbered list with the first and last names of everyone at your station. Your name should appear in bold text.

**#2** Each lab assignment is worth how many points?

**#3** Which of the following is a tokenized URL?

a. https://data.urbanaillinois.us/api/views/6gtk-bwms

b. https://github-dev.cs.illinois.edu/stat440-fa21/stat440-fa21-course-content/blob/master/data/trips440-data.txt

c. https://raw.github-dev.cs.illinois.edu/stat440-fa21/stat440-fa21-course-content/master/data/chicago-food-inspections-data.csv?token=AAABJG5E3NYYWDFJPNK77YDBG7QAM

d. https://data.ccrpc.org/dataset/traffic-crashes/resource/e8adba01-2e38-4a33-a8dc-571f05d76ffa

e. None of the Above

**#4** Consider the information in the image below and the image itself as a data set. Make one Markdown list: one list contains 3 questions about the data set (i.e. things you want to know about the data). 

![](https://uofi.box.com/shared/static/7ina73ut31ncrx2ep3ed3j7x5hh2z0ws.png)

**#5** Import the Urbana Market at the Square Vendor Products Data using one programming language software and the data URL https://data.urbanaillinois.us/api/views/6gtk-bwms/rows.csv?accessType=DOWNLOAD. Now, print the structure of the data. **This structure should match the data description below. FYI, to import this dataset, you'll need a code chunk (RStudio) or code cell (Jupyter Lab).**

  - The dataset (a .csv file) contains 1185 rows and 15 columns in which each product being sold at the Market at the Square event is included along with the vendor, varieties of the product, and which months the product was available. The Market at the Square is a seasonal farmer's market that includes crafts as well as food products. This data was last updated in 2018. The original source is the City of Urbana.

**#6** Import the Nuisance Complaints Data using one programming language and the data URL https://data.urbanaillinois.us/api/views/tsn9-95m3/rows.tsv?accessType=DOWNLOAD&bom=true.

  - The dataset (a .tsv file) contains 10619 rows and 14 columns in which each complaint is recorded. The columns include details about the complaint and location of the nuisance. The original source is the City of Urbana.

**#7** Import the members of the current US Congress Data using one programming language software and the data URL https://raw.github-dev.cs.illinois.edu/stat440-fa21/stat440-fa21-course-content/master/data/data-leg?token=AAABJG56LGWR7IB4KBYBPO3BHABSK. Now, print the structure of the data. **This structure should match the data description below. FYI, to import this dataset, you'll need a code chunk (RStudio) or code cell (Jupyter Lab).** 

  - The dataset (a file with no extension) contains the 538 members of the US Congress with 6 variables ("columns") per person which includes details about the legislators' first and last names, middle name, nickname, and suffixes. According to the GovTrack, "the United States Congress has two chambers, one called the Senate and the other called the House of Representatives (or "House" for short) which share the responsibilities of the legislative process to create federal statutory law." The original source is GovTrack.
