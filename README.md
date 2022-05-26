# Description

Code for the project done during the course "(Introduction to) Network Analysis". Project title is "Exploring power-law distributions in cores and peripheries of networks".

# Setup

The setup is quite simple.

First [install `forceatlas2`](https://github.com/bhargavchippada/forceatlas2/issues/34#issuecomment-1102409914) with:
```
git clone https://github.com/bhargavchippada/forceatlas2
cd forceatlas2
pip install .
```

Next, install the requirements from `requirements.txt` with `pip install -r requirements.txt`.

# Repository "walkthrough"

The folder `data` contains all (and more) graphs used for testing. They are split into two folders - `directed` and `undirected`, and each folder contains the respective graphs. The file `network info.txt` contains the information about: (1) what type of graph it is (social, technological...), (2) the link where it was found.

The folder `results` contains the, well, results of the testing - a figure with 3 plots (one for the entire graph, one for the core, and one for the periphery) for every graph and algorithm tested.

`bz.py` contains the implementation of Batagelj and Zaveršnik's $O(m)$ CP algorithm. Currently it is not used.

`rc.py` contains the implementation of a CP algorithm based on the rich club effect, described in the paper linked in that same file.

`code.py` contains the "main" part of the code.
