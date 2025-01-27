# ARC
Our team's attempt to solve the ARC Challenge for the MoL Project in January 2025

## General

Our approach consists of two main modules. The knowledge graph (see *knowledge_graph*) used for object detection in the grids, and the domain specific language (see *dsl*). Images and plots are saved to the *images* folder.

Dependencies are listed in *requirements.txt*

## Resources

A collection of resources that inspired our approach: https://docs.google.com/document/d/1Vun0-QkvoiFlLQucCqk54E-_ZWlo65H7j77A2ixrk-o/edit?tab=t.0

## Setup & Run

1. Install dependencies
    ```sh
     bash dependencies.sh
    ```
    Note: this script installs pyenv which it uses manage both the python version and create the projects virtual environment `killer_shARCs'. This pyenv managed environment may be used for development but it is recommended that you first setup your shell environment for Pyenv as per these [instructions](https://github.com/pyenv/pyenv?tab=readme-ov-file#b-set-up-your-shell-environment-for-pyenv).

2. Run solver
    ```
    #TODO
    ```

### Development Tools

#### Docker for Kuzu DB visualizations

Follow the instructions for installing [docker desktop](https://docs.docker.com/desktop/setup/install/mac-install/) for your os. 

Docker desktop is used to visualize the knowledge graph (implemented as a Kuzu database) - this is helpful for development.  

Once docker desktop is running you can use the following command to launch the visualization software:

```sh
docker run -p 8000:8000 \
    -v /absolute/path/to/demo_db:/database \
    --rm kuzudb/explorer:latest
```
The query that lets you view the entire knowledge graph is:

```sql
MATCH (a)-[b]->(c)
RETURN *;
```

### Trouble Shooting

#### cairo/drawsvg issues 

in case cairo (needed to process the grid visualisations) does not work, you might need to install it another way. For instance on mac, you can use homebrew (which you need to set up first) to install it. Most helpful article: https://jonathansoma.com/everything/blog/2022/solution-to-no-library-called-cairo-2-was-found-error/
brew install cairo

*alternatively:* 
python3 -m pip install "drawsvg[all]"

### Git

*General:* Git allows you to collaborate on code by enabling version control. From the project code (which is often called “main” and we follow that convention), you can create your own copies (branches), which you can work on without affecting the remaining code. When you are done impleneting the feature you were working on, you can merge your branch with the main one again to consolidate the changes. This allows multiple people to work on the same code at the same time without running into conflicts. For instance, if someone else implemented on a different feature simultaneously as you were working on yours, you would merge your branch back into the updated version of the main.
Further, each branch has something like an “official version”. You can make changes to your code and delete them until you are happy. Only then do you add and commit your changes, which “officially changes” the code.
Lastly, each branch has a corresponding online (remote) and offline (local) version. Usually, you make (“official”) changes to your local code, then push it to the remote.

