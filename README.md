# ReversiBot

This is an attempt to implement simple Artificial Neural Networks to play the game of Reversi/Othello. Please notify me is you find any of my plenty of mistakes... :P

NOTE: the 'Edax' engine is bundled with this repository and I do not possess any rights to that engine.

## Getting Started

### Dependencies

This project is built on Python 2.7 but a few outside modules were used:
  - anytree
  - matplotlib (optional*)
  - Cython (optional for ~1.5x speedup)

*I haven't yet implemented automatically adjusting for if it's installed... just search through the errors and remove all the instances of pylab :P)  <- I'll look to making it easier in the near future :D

```
pip install anytree
pip install matplotlib
pip install cython
```

### Installing

Clone the directory. If all the dependencies are met, you can easily run with:
```
python gui.py
```

To compile with Cython, do:
```
python setup.py build_ext --inplace
```

and run it as you would normally.

## Other notes

Data collection is done with the command:

```
python collect_data.py
```

Training is done by:

```
python train.py
```

## TODO

Implement better ease of use... -_- ... *sigh... I also need to explain this better.

## Acknowledgments

* [Edax](https://github.com/abulmo/edax-reversi) -- released under GNU GPL version 3

