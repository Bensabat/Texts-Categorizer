# Text Categorizer

Resume
------

This project is about creating a text categorizer, giving a text it has to return the most consistent theme. To achieve this, the program is trained with text files from a giving topics dataset, and calculates the n-gram for each topic. Then, a jaccard distance is done between all n-grams generated from train dataset and the giving text file. The user can add some topics and text files on the datasets.

The main steps are interaction with user and the datasets, texts preprocessing, n-grams extraction and theme recognition with jaccard distance.
 
This program has been developed with Python programming language.

The folder contains:

* src folder containing the source files
* resources folder containing
     * dataset folder of training topic with texts
     * dataset folder of testing topic with texts
     * file of stop words

___
Execution
---------

Go into the root folder and launch this command if you want to train the program using dataset:

    > python3 src/main.py -train

Or this command if you want to launch the topic recognition of a text file:

    > python3 src/main.py -test

# How to launch the app

## BDD
First of all you have to create a postgreSQL database named "thematisation" with a user called "seo"
and no password.

## Back-end
To launch the back end, open the folder /back/SEO/SEO.
Once your are in, enter the following command:
"python manage.py runserver"

## Front-end
For the front-end, go to the folder /front/seo.
Enter the following command in the right order:
- npm i
- npm run start

___
Authors
-------

EPITA School, SCIA/MTI Master 1 - Project for Search Engine Optimisation Course. 

Authors: 
- **BENSABAT David** (bensab_d)
- **LAMBERT Valentin** (lamber_p)