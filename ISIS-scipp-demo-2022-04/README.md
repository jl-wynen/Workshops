# Scipp Workshop at ISIS 2022-04-05

For ISIS Scientific Software Group On-Site Day.

## Exercises

### Prepare

1. Install [scipp](https://scipp.github.io/) and Jupyter.
   The reccommended way is by creating a new conda environment from **`env.yml`**:
   ```
   conda env create -f env.yml -n scipp-exercise
   ```

2. Obtain the data.
   Either download https://public.esss.dk/groups/scipp/scipp/1/rhessi_flares.h5 or run `prepare_exercise_data_rhessi.py`.

### Run

The Jupyter notebook **`exercise.ipynb`** contains the exercises and explanations.
Solutions in `solution.ipynb`.


## Slides

The slides are in `slides/slides.ipynb` and require additional Python packages.
They were written in an environment created from `dev-env.yml`
