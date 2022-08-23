# ponyexpress

A cookiecutter template for SMO/MRML python tools

## Project set up

```
my_project/
|- my_project.sqlite
|- my_project.yml
|- my_projects_seed_file.txt
```

## Configuration

```
db_url: 'sqlite:///test.sqlite'
edge_table_name: 'edge_list'
node_table_name: 'node_list'
connector: 'telegram'
strategy: 'spikyball'
max_iteration: 10000
batch_size: 150
random_wait: True
seeds: # optional, either seeds or seed_file
 - things_to_add
seed_file: 'seeds.txt' # seeds_file takes precedence
```
## Developer Install

- Install poetry
- Clone repository
- In the cloned repository's root directory run poetry install
- Run poetry shell to start development virtualenv
- Run pytest to run all tests


---

[Philipp Kessling](mailto:p.kessling@leibniz-hbi.de) under MIT.