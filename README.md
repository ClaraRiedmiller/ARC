# ARC
Our team's attempt to solve the ARC Challenge for the MoL Project in January 2025



## General

Our approach consists of two main modules. The knowledge graph (see *knowledge_graph*) used for object detection in the grids, and the domain specific language (see *dsl*). Images and plots are saved to the *images* folder.

Dependencies are listed in *requirementes.txt*




## Setup (Notes for my team)

# Conda

*General:* With conda, you can create virtual environments. This means, you can group the exact packages and versions of them needed for a project separately from the rest. As a consequence, you can change them without affecting any other projects.

### set up conda

#### create new environment (here, arc is the environment name)
conda create --name arc

#### activate that environment
conda active arc


### our packages

#### to make it easy, I included all the necessary packages in the requirements.txt file. All you have to do is run
pip install -r requirements.txt





#### install the arckit library (pip is a python package manager)
pip install -U arckit


#### other useful commands

#### see your environments (and which one is active)
conda env list

#### see all packages in your current environment
conda list



### our packages

#### in case cairo (needed to process the grid visualisations) does not work, you might need to install it another way. For instance on mac, you can use homebrew (which you need to set up first) to install it. Most helpful article: https://jonathansoma.com/everything/blog/2022/solution-to-no-library-called-cairo-2-was-found-error/
brew install cairo



# Git

*General:* Git allows you to collaborate on code by enabling version control. From the project code (which is often called “main” and we follow that convention), you can create your own copies (branches), which you can work on without affecting the remaining code. When you are done impleneting the feature you were working on, you can merge your branch with the main one again to consolidate the changes. This allows multiple people to work on the same code at the same time without running into conflicts. For instance, if someone else implemented on a different feature simultaneously as you were working on yours, you would merge your branch back into the updated version of the main.
Further, each branch has something like an “official version”. You can make changes to your code and delete them until you are happy. Only then do you add and commit your changes, which “officially changes” the code.
Lastly, each branch has a corresponding online (remote) and offline (local) version. Usually, you make (“official”) changes to your local code, then push it to the remote.

